import os
import json
import shutil
import glob
import time

import face_recognition
from PIL import Image

from dolly.db import *
from dolly.main import *
from dolly.utils import *

DIRNAME = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def fill_db():
    # Big DBs
    #database = os.path.join(DIRNAME, 'data/faces.sqlite')
    #faces_dir = '/Users/salvacarrion/Documents/Programming/Data/faces/original'
    #faces_cropped = '/Users/salvacarrion/Documents/Programming/Data/faces/cropped'

    # Small DB
    database = os.path.join(DIRNAME, 'data/faces_small.sqlite')
    faces_dir = os.path.join(DIRNAME, 'data/faces/original')
    faces_cropped = os.path.join(DIRNAME, 'data/faces/cropped')

    # Other variables
    MAX_FACES = 0  # LIMIT OF FACES OT FIND

    # create a database connection
    conn = create_connection(database)
    with conn:
        print('Deleting previous results...')
        try:
            delete_all_files_dir(faces_cropped)
        except FileNotFoundError as e:
            os.mkdir(faces_cropped)

        print('Reading directory...')
        num_faces = 0

        for filename in images_in_path(faces_dir):
            # File data
            f_head, f_tail = os.path.split(filename)
            f_name, f_ext = os.path.splitext(f_tail)

            print('Finding faces (%d) in: %s' % (num_faces + 1, f_tail))

            # Load image
            image = face_recognition.load_image_file(filename)

            # Get attributes
            face_locations = face_recognition.face_locations(image)
            face_landmarks_list = face_recognition.face_landmarks(image, face_locations)
            image_encodings = face_recognition.face_encodings(image, face_locations)

            # Save each face individually
            data_f = []
            for i in range(0, len(face_locations)):
                # Crop face
                fc_name = f_name + '_face_' + str(i) + '.jpg'
                save_path = faces_cropped + '/' + fc_name
                crop_image(image, face_locations[i], save_path)
                #print('\t - Image saved in ' + save_path + '\n')

                # Cast variables to string
                face_location = str(face_locations[i])
                face_landmarks = json.dumps(face_landmarks_list[i])
                image_encoding = image_encodings[i]

                data_f.append((f_name, face_location, face_landmarks, image_encoding, fc_name, f_tail))

            # Save faces into DBs
            sql_line = "INSERT INTO faces(name, face_location, face_landmarks, face_encoding, face_cropped, " \
                       "original_image) VALUES(?, ?, ?, ?, ?, ?);"
            cur = conn.cursor()
            cur.executemany(sql_line, data_f)
            conn.commit()  # Force commit (To make sure the commit is done at this point)

            # Increase counter
            num_faces += len(data_f)
            if MAX_FACES != 0 and num_faces > MAX_FACES:
                    break
        print('\n----------------------------')
        print('A total of %d images were added' % num_faces)


if __name__ == '__main__':
    start_t = time.time()
    #fill_db()
    end_t = time.time() - start_t
    print('- Elapsed time: %.5fs' % end_t)
