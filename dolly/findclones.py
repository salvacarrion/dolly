#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys, os, time
import argparse, sys
import json
import shutil
import glob
import bisect
import uuid
import pickle
import nmslib

import face_recognition
import numpy as np
from PIL import Image, ImageDraw
from googleapiclient.discovery import build

from dolly.db import *
from dolly.utils import *

__all__ = ['Finder']

DIRNAME = os.path.dirname(os.path.dirname(__file__))


class Finder:

    def __init__(self, db_conn=None, in_memory=True, version='v1'):
        # vars
        self.conn = db_conn
        self.in_memory = in_memory
        self.SQLs = {'faces_with_encodings': 'SELECT * from faces WHERE face_encoding IS NOT NULL;',
                     'entity_from_faceid': 'SELECT * from entities WHERE freebase_mid=(SELECT freebase_mid from faces WHERE id=?);'
                     }

        # Create a database connection
        if not db_conn:
            print('Connecting to DB...')
            db_path = os.path.join(DIRNAME, 'data/production/msceleb/{}/db/msceleb.sqlite'.format(version))
            self.conn = create_connection(db_path)

        # Build index in memory
        if in_memory:
            pickle_path = os.path.join(DIRNAME, 'data/production/msceleb/{}/pickle/'.format(version))

            # Load vectors and build index
            self.np_ids = pickle.load(open(pickle_path + 'np_ids.pkl', 'rb'))
            self.index = nmslib.init(method='hnsw', space='cosinesimil')
            self.index.addDataPointBatch(pickle.load(open(pickle_path + 'np_encodings.pkl', 'rb')))
            self.index.createIndex()

    def analyze_face(self, filename_or_np_array, model='hog'):
        # Load image (np_array)
        image, _type = image_loader(filename_or_np_array)

        # Find all facial features
        face_locations = face_recognition.face_locations(image, model=model)
        if len(face_locations):
            face_location = face_locations[0]
            face_landmarks = face_recognition.face_landmarks(image, [face_location])[0]
            face_encoding = face_recognition.face_encodings(image, [face_location])[0]
            return face_location, face_landmarks, face_encoding
        return None, None, None

    def findclones(self, face_encoding, top_k=10, print_results=False):
        if self.in_memory:
            func = self._fc_memory
        else:
            func = self._fc_db
        return func(face_encoding, top_k, )

    def enhance_results(self, top_candidates):
        res = []

        with self.conn:
            cur = self.conn.cursor()

            for i, candidate in enumerate(top_candidates):
                dist, face_id = candidate

                # Get info from DB
                db_row = cur.execute(self.SQLs['entity_from_faceid'], (face_id,)).fetchone()
                res.append((face_id, db_row[1], db_row[2], dist))  # (Face_id, freebase_mid, entity_name, dist)
        return res

    def print_results(self, candidates):
        for i, c in enumerate(candidates):
            face_id, freebase_mid, entity_name, dist = c
            values = (i + 1, entity_name, freebase_mid, dist)
            print('#{}. {};\tEntityID: {};\tDistance: {};'.format(*values))

    def execute(self, *args, **kwargs):
        with self.conn:
            cur = self.conn.cursor()
            return cur.execute(*args, **kwargs)

    def _fc_memory(self, face_encoding, top_k, **kwargs):
        ids, distances = self.index.knnQuery(face_encoding, k=top_k)
        ids_db = self.np_ids[ids]
        top_candidates = [(float(distances[i]), int(ids_db[i])) for i in range(0, len(ids))]
        return self.enhance_results(top_candidates)

    def _fc_db(self, face_encoding, top_k=10, **kwargs):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(self.SQLs['faces_with_encodings'])

            # Find similar faces, without using too much memory
            top_candidates = []  # Max. size 10
            for row in cur:  # Iterator. Doesn't load the whole table
                face_id = int(row[0])
                dist = float(face_recognition.face_distance([convert_array(row[5])], face_encoding)[0])

                # Add to list IN ORDER
                t = (dist, face_id)
                if len(top_candidates) < top_k:
                    bisect.insort(top_candidates, t)
                else:
                    if dist < top_candidates[-1][0]:  # Closer than the last element
                        bisect.insort(top_candidates, t)
                        top_candidates.pop()  # Remove last element

            return self.enhance_results(top_candidates)

