#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys, os, time
import argparse, sys
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


def crop_image(filename_or_np_array, coords, save_path=None, console=True, **kwargs):
    # Load image (np_array)
    image, _type = __image_loader(filename_or_np_array)

    # Load PIL image and crop it
    (top, right, bottom, left) = coords
    pil_image = Image.fromarray(image)
    pil_image = pil_image.crop((left, top, right, bottom))

    # Save image
    if save_path:
        pil_image.save(save_path, 'JPEG', quality=100)
    elif console:  # Display the resulting image
        pil_image.show()

    return pil_image


def findfaces(filename_or_np_array, save_path=False, verbose=1, **kwargs):
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


def findfacesdir(directory, save_path, max_faces=0, **kwargs):
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


def findclones(filename_or_np_array, top_k=10, database=None, **kwargs):
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


def draw_boxes(filename_or_np_array, save_path=None, console=True, **kwargs):
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
    elif console:  # Display the resulting image
        pil_image.show()

    return image, face_locations


def draw_landmarks(filename_or_np_array, save_path=None, console=True, **kwargs):
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
    elif console:  # Display the resulting image
        pil_image.show()

    return image, face_landmarks


def main():
    try:
        arg1 = str(sys.argv[1])

        parser = argparse.ArgumentParser(description='Find all faces in an image')
        parser.add_argument('command', help='Action to take')  # Ignore
        # Select command
        if arg1 == 'findfaces':
            parser.add_argument('-f', '--filename', help='filename of the image to process',
                                dest='filename_or_np_array', required='True')
            parser.add_argument('-d', '--save_path', help='directory to save the faces found')
            func = findfaces

        elif arg1 == 'findfacesdir':
            parser.add_argument('-d', '--directory', help='directory to search for faces', required='True')
            parser.add_argument('-d2', '--save_path', help='directory to save the faces found', required='True')
            parser.add_argument('-m', '--max_faces', help='maximum number of faces to save', type=int, default=0)
            func = findfacesdir

        elif arg1 == 'draw_boxes':
            parser.add_argument('-f', '--filename', help='filename of the image to process',
                                dest='filename_or_np_array', required='True')
            parser.add_argument('-s', '--save_path', help='directory to save the faces found')
            func = draw_boxes

        elif arg1 == 'draw_landmarks':
            parser.add_argument('-f', '--filename', help='filename of the image to process',
                                dest='filename_or_np_array', required='True')
            parser.add_argument('-s', '--save_path', help='directory to save the faces found')
            func = draw_landmarks

        else:
            raise SyntaxError

        # Call function
        results = vars(parser.parse_args())
        func(**results)

    except (SyntaxError, IndexError) as e:
        print('Unknown command')
        print('Available commands: [findfaces, findfacesdir, draw_boxes, draw_landmarks]')


if __name__ == '__main__':
    #draw_landmarks('/Users/salvacarrion/Desktop/Unknown.jpeg')
    main()
