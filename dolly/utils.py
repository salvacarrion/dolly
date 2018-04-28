#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, shutil, glob, codecs
import codecs
import base64
import io

from PIL import Image
import numpy as np


def delete_all_files_dir(directory):
    _dir = os.path.normpath(directory) + '/*'
    for f in glob.glob(_dir):
        os.remove(f)


def empty_dir(directory):
    _dir = os.path.normpath(directory) + '/'
    shutil.rmtree(_dir)
    os.makedirs(_dir)


def images_in_path(directory):
    files = []
    extensions_allowed = ['*.jpg', '*.jpeg', '*.png']
    for ext in extensions_allowed:
        files.extend(glob.glob(os.path.join(directory, ext)))
    return files


def decode_str(text):
    return codecs.escape_decode(bytes(text, "utf-8"))[0].decode("utf-8")


def decode_b64_image(str_img):
    data = base64.b64decode(str_img)
    return Image.open(io.BytesIO(data))


def isLast(itr):
  old = next(itr)
  for new in itr:
    yield False, old
    old = new
  yield True, old