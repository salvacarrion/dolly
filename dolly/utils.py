#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, shutil, glob
import codecs
import base64
import io

import numpy as np
from face_recognition import load_image_file
from PIL import Image


def image_loader(filename_or_np_array):
    # Read filename or load np_array
    if isinstance(filename_or_np_array, str):
        # Load the image file into a numpy array
        return load_image_file(filename_or_np_array), str
    elif isinstance(filename_or_np_array, np.ndarray):
        return filename_or_np_array, np.ndarray
    else:
        raise TypeError('Invalid image type')


def crop_image(filename_or_np_array, coords, save_path=None, console=True, **kwargs):
    # Load image (np_array)
    image, _type = image_loader(filename_or_np_array)

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

