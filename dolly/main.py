#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys, os, time
import json
import shutil
import glob
import bisect
import uuid

import face_recognition
import numpy as np
from PIL import Image, ImageDraw

from dolly.db import *
from dolly.utils import *


def __image_loader(filename_or_np_array):
    _type = None
    # Read filename or load np_array
    if isinstance(filename_or_np_array, str):
        # Load the image file into a numpy array
        image = face_recognition.load_image_file(filename_or_np_array)
        _type = str
    elif isinstance(filename_or_np_array, np.ndarray):
        image = filename_or_np_array  # Must be a np_array
        _type = np.ndarray
    else:
        raise TypeError('Invalid image type')
    return image, _type


def crop_image(filename_or_np_array, coords, save_path=None):
    # Load image (np_array)
    image, _type = __image_loader(filename_or_np_array)

    # Load PIL image and crop it
    (top, right, bottom, left) = coords
    pil_image = Image.fromarray(image)
    pil_image = pil_image.crop((left, top, right, bottom))

    # Save image
    if save_path:
        pil_image.save(save_path, 'JPEG', quality=100)
    else:  # Display the resulting image
        pil_image.show()

    return pil_image


def findfaces(filename_or_np_array, save_path=False, verbose=1):
    # Load image (np_array)
    image, _type = __image_loader(filename_or_np_array)

    # Get attributes
    face_locations = face_recognition.face_locations(image)

    # For each faces
    for i in range(0, len(face_locations)):
        # Print coordinates
        top, right, bottom, left = face_locations[i]
        values = (i+1, top, right, bottom, left, right-left, bottom-top)
        print('- Face {}: (top={}, right={}, bottom={}, left={}) - {}x{}px'.format(*values))

        # Crop face and save it
        if save_path:
            if _type == str:
                # File data
                f_head, f_tail = os.path.split(filename_or_np_array)
                f_name, f_ext = os.path.splitext(f_tail)
            else:
                f_name = uuid.uuid1()

            path = os.path.normpath(save_path) + '/' + f_name + '_face_' + str(i) + '.jpg'
            crop_image(image, face_locations[i], path)

    if verbose > 0:
        print('\nNumber of faces: %d' % len(face_locations))

    return face_locations


def findfacesdir(directory, save_path, max_faces=False):
    print('Reading directory...')
    num_faces = 0
    for filename in images_in_path(directory):
        # File data
        f_head, f_tail = os.path.split(filename)

        print('\nFinding faces (%d) in: %s' % (num_faces+1, f_tail))
        face_locations = findfaces(filename, save_path, verbose=0)
        num_faces += len(face_locations)

        if max_faces != 0 and num_faces > max_faces:  # Stop
            break

    print('Finished.')
    print('A total of %d images were added' % num_faces)
    return num_faces


def findclones(filename_or_np_array, top_k=10, database=None):
    # Load image (np_array)
    image, _type = __image_loader(filename_or_np_array)

    # Find enconding vector
    image_encodings = face_recognition.face_encodings(image)

    # Check database source
    if not database:
        DIRNAME = os.path.dirname(os.path.dirname(__file__))
        database = os.path.join(DIRNAME, 'data/faces.sqlite')

    # Create a database connection
    print('Connecting to DB...')
    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT * from faces;')

        top_candidates = []  # Max. size 10
        for row in cur:  # Iterator. Doesn't load the whole table
            # Compute distance
            dist = face_recognition.face_distance([convert_array(row[4])], image_encodings[0])[0]
            t = (dist, row)

            # Add to list
            if len(top_candidates)>= top_k:
                if dist < top_candidates[-1][0]:  # Closer than the last element
                    bisect.insort(top_candidates, t)
                    top_candidates.pop()  # Remove last element

            else:  # if total < K: Add anyway
                bisect.insort(top_candidates, t)

        # Print images
        for c in top_candidates:  # Sorted
            dist, row = c
            values = (dist, row[6])
            print('Distance={}; original={}'.format(*values))

        return top_candidates


def draw_boxes(filename_or_np_array, save_path=None, select_all=True, highlight=1):
    # Load image (np_array)
    image, _type = __image_loader(filename_or_np_array)

    # Find all the faces
    face_locations = face_recognition.face_locations(image)

    # Convert the image to a PIL-format image so that we can draw on top of it with the Pillow library
    # See http://pillow.readthedocs.io/ for more about PIL/Pillow
    pil_image = Image.fromarray(image)

    # Create a Pillow ImageDraw Draw instance to draw with
    draw = ImageDraw.Draw(pil_image)

    # Loop through each face found in the unknown image
    for counter, val in enumerate(face_locations):
        top, right, bottom, left = val

        # Draw a box around the face using the Pillow module
        color = (255, 0, 0) if counter > 0 else (0, 255, 0)
        draw.rectangle(((left, top), (right, bottom)), outline=color)

    # Remove the drawing library from memory as per the Pillow docs
    del draw

    # Save image
    if save_path:
        pil_image.save(save_path, 'JPEG', quality=100)
    else:  # Display the resulting image
        pil_image.show()

    return image, face_locations


def draw_landmarks(filename_or_np_array, save_path=None):
    facial_features = [
        'chin',
        'left_eyebrow',
        'right_eyebrow',
        'nose_bridge',
        'nose_tip',
        'left_eye',
        'right_eye',
        'top_lip',
        'bottom_lip'
    ]

    # Load image (np_array)
    image, _type = __image_loader(filename_or_np_array)

    # Find all facial features in all the faces in the image
    face_landmarks_list = face_recognition.face_landmarks(image)

    # Convert the image to a PIL-format image so that we can draw on top of it with the Pillow library
    # See http://pillow.readthedocs.io/ for more about PIL/Pillow
    pil_image = Image.fromarray(image)

    # Create a Pillow ImageDraw Draw instance to draw with
    draw = ImageDraw.Draw(pil_image)

    # Let's trace out each facial feature in the image with a line!
    for face_landmarks in face_landmarks_list:  # Faces
        for facial_feature in facial_features:  # Features
            draw.line(face_landmarks[facial_feature], width=1)

    # Remove the drawing library from memory as per the Pillow docs
    del draw

    # Save image
    if save_path:
        pil_image.save(save_path, 'JPEG', quality=100)
    else:  # Display the resulting image
        pil_image.show()

    return image, face_landmarks


def main():
    try:
        arg1 = str(sys.argv[1])
        if arg1 == 'vector':
            print('vector filename1')
        elif arg1 == 'matrix':
            print('matrix dir')
        elif arg1 == 'findclones':
            findclones(str(sys.argv[2]))

        elif arg1 == 'findfaces':
            if len(sys.argv) == 3:
                findfaces(str(sys.argv[2]), save_path=False)
            elif len(sys.argv) == 4:
                findfaces(str(sys.argv[2]), save_path=str(sys.argv[3]))
            else:
                raise IndexError
        elif arg1 == 'findfacesdir':
            if len(sys.argv) == 4:
                findfacesdir(str(sys.argv[2]), save_path=str(sys.argv[3]))
            elif len(sys.argv) == 5:
                findfacesdir(str(sys.argv[2]), save_path=str(sys.argv[3]), max_faces=int(sys.argv[4]))
            else:
                raise IndexError
        elif arg1 == 'drawboxes':
            if len(sys.argv) == 3:
                draw_boxes(str(sys.argv[2]))
            elif len(sys.argv) == 4:
                draw_boxes(str(sys.argv[2]), save_path=str(sys.argv[3]))

        else:
            raise IndexError

    except IndexError as e:
        print('vector\tFor a given image, return its vector\n'
              'matrix\tFor a given directory, return a dictionary with the vectors of each image\n'
              'findfaces filename (save_path)\tFind faces in a image. Option to save them.\n'
              'findfacesdir filename save_path\tFinf faces in a directory and save them in another. Option to limit the maximun number of faces\n'
              '-h\t\tTo list all available options')


if __name__ == '__main__':
    draw_landmarks('/Users/salvacarrion/Desktop/Unknown.jpeg')
    #main()
