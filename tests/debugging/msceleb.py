#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
import json
import shutil
import glob
import time
import csv
import re

import face_recognition
from PIL import Image

from dolly.db import *
from dolly.main import *
from dolly.utils import *


MSCELEB_DIR = '/Users/salvacarrion/Documents/Programming/Python/Projects/dolly/data/faces/msceleb/'
DIRNAME = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
csv.field_size_limit(sys.maxsize)


def _save_msceleb_image(freebase_mid, image_id, isr, img, base_dir=MSCELEB_DIR):
    celeb_folder = os.path.normpath(base_dir + freebase_mid)
    img_name = '{}-FaceId-0.jpg'.format(isr)

    # Create folder if it doesn't exists
    if not os.path.isdir(celeb_folder):
        os.makedirs(celeb_folder)

    # Save image
    filename = celeb_folder + '/' + img_name
    img.save(filename)


def _face_parser(row, encode_face, query_type):
    # Column1: Image ID
    # Column2: FaceData_Base64Encoded
    # Column3: Freebase MID
    # Column4: ImageSearchRank
    # Column5: ImageURL
    # DB => image_name, face_location, freebase_mid, face_encoding, image_search_rank, image_url, hard_face

    # Decode image in base64
    face_location = None
    try:
        img = decode_b64_image(row[1])
        np_image = np.array(img)

        face_location = face_recognition.face_locations(np_image)[0]
        encoding = face_recognition.face_encodings(np_image, [face_location])[0] if encode_face else None
        hard_face = False
        _save_msceleb_image(freebase_mid=row[2], image_id=row[0], isr=row[3], img=img)
    except IndexError as e:  # Face not found with HOG. Try with CNN?
        encoding = None
        hard_face = True
        print('(Face not found [Entity: {}; Name: {}; ISR: {}])'.format(row[2], row[0], row[3]))

    if query_type == 'insert':
        return row[0], str(face_location), row[2], encoding, row[3], row[4], hard_face
    elif query_type == 'update_encoding':
        return str(face_location), encoding, hard_face
    else:
        raise KeyError('Unknown query type')


def _entities_parser(row):
    # Column1: Freebase MID
    # Column2: "Name String"@Language
    freebase_mid = row[0]
    #gkg_id = '/m/' + freebase_mid[2:]

    try:
        name, lang = re.findall('^(.*)@([^@]+)$', row[1])[0]
        if lang == 'en':
            if name.startswith('"') and name.endswith('"'):  # Remove quoting
                name = name[1:-1]
            return freebase_mid, decode_str(name)  #, gkg_id
    except Exception as e:
        print(str(row) + '\n' + str(e))
    return None


def _get_entity_summary(cur):
    # Get number of encodings per entity
    index_encodings = {}
    cur.execute('SELECT freebase_mid, COUNT(*) as total, COUNT(face_encoding) as encodings '
                'FROM faces GROUP BY freebase_mid;')
    for row in cur:
        index_encodings[row[0]] = row[2]  # encodings
    return index_encodings


def _get_face(cur, data):
    cur.execute('SELECT * FROM faces WHERE image_name=? and freebase_mid=? and image_search_rank=?;', data)
    return cur.fetchone()


def _choose_action_face(cur, index_encodings, min_num_encodings, *faceargs):
    freebase_mid = faceargs[1]
    total_encodings = index_encodings.get(freebase_mid)

    # Check if the entity has the minimum number of encodings required
    if total_encodings >= min_num_encodings:
        pass
        #print('Skipping entity: ' + freebase_mid + '. (Enough encodings)')

    else:   # Does the face really exists in our DB?
        face_db = _get_face(cur, *faceargs)  # Get face
        fdb_id, fdb_encoding, fdb_hardface = face_db[0], face_db[5], face_db[8]  # DB face values

        if not face_db:  # [ADD] Face doesn't exist
            return 'a', None

        else:  # Face exists -> Update (if needed)
            sd = (fdb_id, bool(fdb_encoding), fdb_hardface)
            if (not fdb_encoding) and (not fdb_hardface):  # [UPDATE] (no encoding and no hard/null)
                return 'u', sd
            else:  # [Ignore Face] already encoded or hard_face
                pass
                #print('Skipping entity: ' + freebase_mid + '\t[encoding:{}, hard_face:{}]'.format(*sd))
    return None, None


def _load_faces_db(filename, database, sql, parser, csvkargs, buffer=10000, min_num_encodings=1, **kwargs):
    data_add = []
    data_update = []
    num_changes_db = 0

    sql_add, sql_update = sql['add'], sql['update']
    commit_flag = False

    encode_face = bool(1) if min_num_encodings > 0 else bool(0)
    act_txt = {'a': 'Adding', 'u': 'Updating'}

    # Create a database connection
    conn = create_connection(database)
    cur = conn.cursor()
    with conn:
        # Get number of encodings per entity
        index_encodings = _get_entity_summary(cur)  # {key => num_encodings}

        with open(filename) as csvfile:
            reader = csv.reader(csvfile, **csvkargs)
            for counter, (is_last, row) in enumerate(isLast(reader)):  # Read TSV file
                freebase_mid = row[2]  # TSV face values
                res_upd = b_encoding = hard_face = None

                # Does entity exist?
                if not index_encodings.get(freebase_mid):  # [ADD face] Entity doesn't exists or error raised
                    action_flag = 'a'
                    index_encodings[freebase_mid] = 0

                else:  # [Check for add/update face]
                    faceargs = (row[0], row[2], row[3])  # image_name, freebase_mid, image_search_rank
                    action_flag, res_upd = _choose_action_face(cur, index_encodings, min_num_encodings, *faceargs)

                # Actions to take in the DB
                if action_flag == 'a':  # Add new face
                    values = parser(row, encode_face, query_type='insert', **kwargs)
                    b_encoding, hard_face = (values[3] is not None), values[-1]
                    data_add.append(values)

                elif action_flag == 'u':  # Update face
                    values = parser(row, encode_face, query_type='update_encoding')
                    fdb_id, sd = res_upd
                    b_encoding, hard_face = (values[1] is not None), values[-1]
                    data_update.append((*values, fdb_id))  # ROW MUST EXIST (encoding, hard_face, id)

                # Reset vars
                if action_flag:
                    num_changes_db += 1
                    index_encodings[freebase_mid] += 1 if b_encoding else 0  # Update number of encodings
                    commit_flag = True if num_changes_db % buffer == 0 else False
                    print_data = (act_txt[action_flag], freebase_mid, b_encoding, hard_face)
                    #print('{} face...\t[entity: {}; encoding: {}; hard_face: {}]'.format(*print_data))

                # Force commit (To make sure the commit is done at this point)
                if commit_flag or is_last:
                    # Execute Query
                    cur.executemany(sql_add, data_add)
                    cur.executemany(sql_update, data_update)
                    conn.commit()

                    n_commit = int((num_changes_db + 1) / buffer)
                    print("- Commit #{}\t\t(csv_line: {}, Added: {}, Modified: {})".format(
                        n_commit, counter + 1, len(data_add), len(data_update)))

                    # Reset vars
                    data_add = []
                    data_update = []
                    commit_flag = False

                    if is_last:
                        print('Finished!')


def _load_faces_msceleb():
    filename = '/Users/salvacarrion/Downloads/TrainData_Base.tsv'
    database = '/Users/salvacarrion/Documents/Programming/Python/Projects/dolly/data/msceleb.sqlite'

    # SQLs
    sql_add = "INSERT INTO faces(image_name, face_location, freebase_mid, face_encoding, image_search_rank, image_url, " \
              "hard_face) VALUES(?, ?, ?, ?, ?, ?, ?);"
    sql_update = "UPDATE faces SET face_location=?, face_encoding=?, hard_face=? WHERE id=?"
    sql_q = {'add': sql_add, 'update': sql_update}

    # Call function
    csvkargs = {'delimiter': '\t', 'quoting': csv.QUOTE_NONE}
    kwargs = {}
    _load_faces_db(filename, database, sql_q, _face_parser, csvkargs, buffer=100, min_num_encodings=1, **kwargs)


def _load_entities_msceleb():
    filename = '/Users/salvacarrion/Downloads/Top1M_MidList.Name.tsv'
    database = '/Users/salvacarrion/Documents/Programming/Python/Projects/dolly/data/msceleb.sqlite'

    # SQLs
    sql_entities = "INSERT INTO entities(freebase_mid, name_en) VALUES (?, ?);"

    # Call function
    csvkargs = {'delimiter': '\t', 'quoting': csv.QUOTE_NONE}
    load_into_db(filename, database, sql_entities, _entities_parser, csvkargs, buffer=10000)


if __name__ == '__main__':
    #empty_dir(MSCELEB_DIR)
    start_t = time.time()
    #_load_faces_msceleb()
    end_t = time.time() - start_t
    print('- Elapsed time: %.5fs' % end_t)
