#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, glob


def delete_all_files_dir(directory):
    _dir = os.path.normpath(directory) + '/*'
    for f in glob.glob(_dir):
        os.remove(f)


def images_in_path(directory):
    files = []
    extensions_allowed = ['*.jpg', '*.jpeg', '*.png']
    for ext in extensions_allowed:
        files.extend(glob.glob(os.path.join(directory, ext)))
    return files
