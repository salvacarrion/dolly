import os
import unittest

from PIL import Image
from dolly import *

DIRNAME = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class TestDolly(unittest.TestCase):

    def test_crop_image(self):
        filename = os.path.join(DIRNAME, 'data/faces/original/obama.jpg')
        save_path = os.path.join(DIRNAME, 'data/faces/cropped') + '/obama_cropped.jpg'
        coords = (44, 187, 152, 79)  # Obama's face

        # [FILENAME] Crop by filename and save it
        res = crop_image(filename, coords=coords, save_path=save_path)
        self.assertEqual(os.path.isfile(save_path), True)
        self.assertIsInstance(res, Image.Image)

        # Test np_array

    def test_findfaces(self):
        filename = os.path.join(DIRNAME, 'data/faces/original/obama.jpg')
        save_path = os.path.join(DIRNAME, 'data/faces/cropped')

        # [FILENAME] Find face and save it
        res = findfaces(filename, save_path=save_path)
        self.assertEqual(os.path.isfile(save_path + '/obama_face_0.jpg'), True)
        self.assertEqual(len(res), 1)

    def test_findfacesdir(self):
        filename = os.path.join(DIRNAME, 'data/faces/original/')
        save_path = os.path.join(DIRNAME, 'data/faces/cropped/')

        # [FILENAME] Find face and save it
        res = findfacesdir(filename, save_path=save_path)
        self.assertGreater(res, 0)  # num_faces images

    def test_findclones(self):
        filename = os.path.join(DIRNAME, 'data/faces/original/obama.jpg')
        database = os.path.join(DIRNAME, 'data/faces_small.sqlite')

        # [FILENAME] Find face and save it
        res = findclones(filename, top_k=5, database=database)
        self.assertEqual(len(res), 5)  # List of candidates

    def test_draw_boxes(self):
        filename = os.path.join(DIRNAME, 'data/faces/original/obama.jpg')
        save_path = os.path.join(DIRNAME, 'data/faces/cropped/obama_boxes.jpg')

        # [FILENAME] Draw boxes and save it
        res = draw_boxes(filename, save_path=save_path)
        self.assertEqual(os.path.isfile(save_path), True)
        self.assertEqual(len(res), 2)

    def test_draw_landmarks(self):
        filename = os.path.join(DIRNAME, 'data/faces/original/obama.jpg')
        save_path = os.path.join(DIRNAME, 'data/faces/cropped/obama_landmarks.jpg')

        # [FILENAME] Draw boxes and save it
        res = draw_boxes(filename, save_path=save_path)
        self.assertEqual(os.path.isfile(save_path), True)
        self.assertEqual(len(res), 2)


if __name__ == '__main__':
    # Test all
    # unittest.main()

    # # Test single test
    # suite = unittest.TestSuite()
    # suite.addTest(TestDolly("test_findclones"))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)

    # Delete all files created during the test (this line doesn't when unittesting)
    print('Deleting test files...')
    delete_all_files_dir(os.path.join(DIRNAME, 'data/faces/cropped'))
    print('Done!')
