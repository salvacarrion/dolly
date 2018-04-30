#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid

import face_recognition
from PIL import Image, ImageDraw
from googleapiclient.discovery import build

from dolly.utils import *


def findfaces(np_image, save_path=None, prefix_name=None, **kwargs):
    """Find all faces in an image

    Args:
        np_image (numpy ndarray): A Numpy matrix that represents the image
        save_path (:obj:`str`, optional): Defaults to None. Path to save the faces faound.
        prefix_name: (:obj:`str`, optional): Defaults to None. Prefix for the faces to be saved.

    Returns:
        list: Face locations

    """

    # Get attributes
    face_locations = face_recognition.face_locations(np_image)

    # For each faces
    for i in range(0, len(face_locations)):
        # Print coordinates
        top, right, bottom, left = face_locations[i]
        values = (i+1, top, right, bottom, left, right-left, bottom-top)
        print('\t- Face #{}: (top={}, right={}, bottom={}, left={}) - {}x{}px'.format(*values))

        # Crop face and save it
        if save_path:
            if not prefix_name:
                prefix_name = str(uuid.uuid1())

            path = os.path.normpath(save_path) + '/' + prefix_name + '_face_' + str(i) + '.jpg'
            crop_image(np_image, face_locations[i], path)

    return face_locations


def draw_boxes(np_image, save_path=None, **kwargs):
    """Draw boxes to highlight each face in an image

    Args:
        np_image (numpy ndarray): A Numpy matrix that represents the image
        save_path (:obj:`str`, optional): Defaults to None. Path to save the faces faound.

    Returns:
        tuple: PIL image, List of face locations

    """

    # Find all the faces
    face_locations = face_recognition.face_locations(np_image)

    # Convert the image to a PIL-format image so that we can draw on top of it with the Pillow library
    # See http://pillow.readthedocs.io/ for more about PIL/Pillow
    pil_image = Image.fromarray(np_image)

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

    return pil_image, face_locations


def draw_landmarks(np_image, save_path=None, **kwargs):
    """Draw landmarks to highlight the features of each face in an image

    Args:
        np_image (numpy ndarray): A Numpy matrix that represents the image
        save_path (:obj:`str`, optional): Defaults to None. Path to save the faces faound.

    Returns:
        tuple: PIL image, List of face landmarks

    """
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

    # Find all facial features in all the faces in the image
    face_landmarks_list = face_recognition.face_landmarks(np_image)

    # Convert the image to a PIL-format image so that we can draw on top of it with the Pillow library
    # See http://pillow.readthedocs.io/ for more about PIL/Pillow
    pil_image = Image.fromarray(np_image)

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

    return pil_image, face_landmarks_list


def findfacesdir(directory, save_path, max_faces=0, **kwargs):
    """Find all faces in a directory

    Args:
        directory (str): Path where look for the images to analyze.
        save_path (str): Path where the faces found will be saved.
        max_faces: (:obj:`int`, optional): Defaults to zero. Maximum number of faces to extract from the directory.

    Returns:
        int: Number of faces found

    """

    num_faces = 0
    for filename in images_in_path(directory):
        f_head, f_tail = os.path.split(filename)  # File data
        f_name, f_ext = os.path.splitext(f_tail)

        print('Finding faces (%d) in: %s' % (num_faces+1, f_tail))
        face_locations = findfaces(image_loader(filename), save_path, prefix_name=f_name)
        num_faces += len(face_locations)

        if max_faces != 0 and num_faces > max_faces:  # Stop
            break

    print('Finished.')
    print('A total of %d images were added' % num_faces)
    return num_faces


def analyze_face(np_image, model='hog'):
    """Get face locations, landmarks and encodings from the first found face

        Args:
            np_image (numpy ndarray): A Numpy matrix that represents the image
            model (str): 'hog' or 'cnn'

        Returns:
            tuple: (list of face locations, list of face landmarks, list of face encodings)

    """

    # Find all facial features
    face_locations = face_recognition.face_locations(np_image, model=model)
    if len(face_locations):
        face_location = face_locations[0]
        face_landmarks = face_recognition.face_landmarks(np_image, [face_location])[0]
        face_encoding = face_recognition.face_encodings(np_image, [face_location])[0]
        return face_location, face_landmarks, face_encoding
    return None, None, None


def get_more_info(api_key, freebase=True, **kwargs):
    """Get more information about an entity from Google Knowledge Graph

        Args:
            api_key (str): Google Knowledge Graph API key
            freebase (bool): Set to True if using freebase IDs
            **kwargs: Args from Google Knowledge Graph API
        Returns:
            dict

    """
    if freebase:
        kwargs['ids'] = '/' + kwargs['ids'].replace('.', '/')

    # Build a service object for interacting with the API. Visit
    # the Google APIs Console <http://code.google.com/apis/console>
    # to get an API key for your own application.
    # Services: https://developers.google.com/api-client-library/python/apis/
    # GKG API: https://developers.google.com/knowledge-graph/reference/rest/v1/
    # More: https://developers.google.com/resources/api-libraries/documentation/kgsearch/v1/python/latest/kgsearch_v1.entities.html
    service = build('kgsearch', 'v1', developerKey=api_key)
    return service.entities().search(**kwargs).execute()


if __name__ == '__main__':
    from dolly.findclones import Finder
    filename = '/Users/salvacarrion/Desktop/obama.jpg'

    f = Finder(in_memory=True)
    f_enc = analyze_face(filename)[2]
    res = f.findclones(face_encoding=f_enc, top_k=10)
    f.print_results(res)
    asd = 23
    #draw_landmarks('/Users/salvacarrion/Desktop/Unknown.jpeg')
    #main()
