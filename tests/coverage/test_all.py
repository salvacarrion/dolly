import os
import unittest

from PIL import Image
from dolly.processing import *

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data/tests/')
DB_PATH = os.path.join(BASE_DIR, 'db/')
IMAGES_PATH = os.path.join(BASE_DIR, 'images/')
PICKLE_PATH = os.path.join(BASE_DIR, 'pickle/')


class TestDolly(unittest.TestCase):

    def test_crop_image(self):
        filename = os.path.join(IMAGES_PATH, 'original/obama.jpg')
        save_path = os.path.join(IMAGES_PATH, 'cropped/') + 'obama_cropped.jpg'
        coords = (44, 187, 152, 79)  # Obama's face

        # [FILENAME] Crop by filename and save it
        res = crop_image(np_image=image_loader(filename), coords=coords, save_path=save_path)
        self.assertEqual(os.path.isfile(save_path), True)
        self.assertIsInstance(res, Image.Image)

    def test_findfaces(self):
        filename = os.path.join(IMAGES_PATH, 'original/obama.jpg')
        save_path = os.path.join(IMAGES_PATH, 'cropped/')
        prefix = 'testing_findfaces'

        # [FILENAME] Find face and save it
        res = findfaces(np_image=image_loader(filename), save_path=save_path, prefix_name=prefix)
        self.assertEqual(os.path.isfile(save_path + prefix + '_face_0.jpg'), True)
        self.assertEqual(len(res), 1)

    def test_draw_boxes(self):
        filename = os.path.join(IMAGES_PATH, 'original/obama.jpg')
        save_path = os.path.join(IMAGES_PATH, 'cropped/obama_boxes.jpg')

        # [FILENAME] Draw boxes and save it
        res = draw_boxes(np_image=image_loader(filename), save_path=save_path)
        self.assertEqual(os.path.isfile(save_path), True)
        self.assertEqual(len(res), 2)

    def test_draw_landmarks(self):
        filename = os.path.join(IMAGES_PATH, 'original/obama.jpg')
        save_path = os.path.join(IMAGES_PATH, 'cropped/obama_landmarks.jpg')

        # [FILENAME] Draw boxes and save it
        res = draw_boxes(np_image=image_loader(filename), save_path=save_path)
        self.assertEqual(os.path.isfile(save_path), True)
        self.assertEqual(len(res), 2)


    def test_findfacesdir(self):
        directory = os.path.join(IMAGES_PATH, 'original/')
        save_path = os.path.join(IMAGES_PATH, 'cropped/')

        # [FILENAME] Find face and save it
        res = findfacesdir(directory=directory, save_path=save_path)
        self.assertGreater(res, 0)  # num_faces images

    def test_findclones(self):
        filename = os.path.join(IMAGES_PATH, 'original/obama.jpg')
        database = os.path.join(DB_PATH, 'msceleb.sqlite')

        from dolly.findclones import Finder
        from dolly.db import create_connection

        f = Finder(db_conn=create_connection(database), in_memory=True, data_path=BASE_DIR)
        f_loc, f_lmarks, f_enc = analyze_face(np_image=image_loader(filename), model='hog')
        res = f.findclones(face_encoding=f_enc, top_k=3)
        f.print_results(res)

        # Check against DB
        f.in_memory = False
        res2 = f.findclones(face_encoding=f_enc, top_k=3)

        # Check against gold standard
        gs_values = [(4, 'm.02mjmr', 'Barack Obama', 0.03169),
                     (2, 'm.06w2sn5', 'Justin Bieber', 0.14482),
                     (5, 'm.06qjgc', 'Lionel Messi', 0.20264)]
        self.assertEqual(len(res), len(res2))
        self.assertEqual(len(res), len(gs_values))
        self.assertEqual(res[0][0], gs_values[0][0])
        for i in range(0, len(res)):
            self.assertEqual(res[i][0], gs_values[i][0])


if __name__ == '__main__':
    # Test all
    unittest.main()

    # # Test single test
    # suite = unittest.TestSuite()
    # suite.addTest(TestDolly('test_findclones'))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)

    # # Delete all files created during the test (this line doesn't when unittesting)
    # print('Deleting test files...')
    # delete_all_files_dir(os.path.join(IMAGES_PATH, 'cropped/'))
    # print('Done!')
