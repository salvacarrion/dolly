#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import argparse

from dolly.processing import *


def _replace_filename_with_image(**kwargs):
    if kwargs.get('filename'):
        kwargs['np_image'] = image_loader(kwargs['filename'])
        del kwargs['filename']
    return kwargs


def _findclones_cli(np_image, top_k, in_memory, model, dataset='msceleb', version='v1', **kwargs):
    from dolly.findclones import Finder
    from dolly.db import create_connection

    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'data/production/{}/{}/'.format(dataset, version))
    database = os.path.join(BASE_DIR, 'db/msceleb.sqlite')

    f = Finder(db_conn=create_connection(database), in_memory=in_memory, data_path=BASE_DIR)
    f_loc, f_lmarks, f_enc = analyze_face(np_image=np_image, model=model)
    res = f.findclones(face_encoding=f_enc, top_k=top_k)
    f.print_results(res)


def main():
    try:
        arg1 = str(sys.argv[1])

        parser = argparse.ArgumentParser(description='Find all faces in an image')
        parser.add_argument('command', help='Action to take')  # Ignore
        # Select command
        if arg1 == 'findfaces':
            parser.add_argument('-f', '--filename', help='filename of the image to process', required=True)
            parser.add_argument('-d', '--save_path', help='directory to save the faces found')
            func = findfaces

        elif arg1 == 'findfacesdir':
            parser.add_argument('-d', '--directory', help='directory to search for faces', required=True)
            parser.add_argument('-d2', '--save_path', help='directory to save the faces found', required=True)
            parser.add_argument('-m', '--max_faces', help='maximum number of faces to save', type=int, default=0)
            func = findfacesdir

        elif arg1 == 'drawboxes':
            parser.add_argument('-f', '--filename', help='filename of the image to process', required=True)
            parser.add_argument('-s', '--save_path', help='directory to save the faces found', required=True)
            func = draw_boxes

        elif arg1 == 'drawlandmarks':
            parser.add_argument('-f', '--filename', help='filename of the image to process', required=True)
            parser.add_argument('-s', '--save_path', help='directory to save the faces found', required=True)
            func = draw_landmarks

        if arg1 == 'findclones':
            parser.add_argument('-f', '--filename', help='filename of the image to process', required=True)
            parser.add_argument('-k', dest='top_k', help="Get 'K' nearest faces", type=int, default=10)
            parser.add_argument('--in_memory', help='Process all in memory (faster) or in disk (slower)',
                                type=bool, default=True)
            parser.add_argument('--model', help="Model used for face detection ('hog' or 'cnn'", default='hog')

            func = _findclones_cli

        else:
            raise SyntaxError

        # Call function
        results = _replace_filename_with_image(**vars(parser.parse_args()))
        func(**results)

    except (SyntaxError, IndexError) as e:
        print('Unknown command')
        print('Available commands: [findfaces, findfacesdir, draw_boxes, draw_landmarks]')


if __name__ == '__main__':
    #_findclones_cli('/Users/salvacarrion/Desktop/obama.jpg')
    main()
