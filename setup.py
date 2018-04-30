# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

NAME = 'dolly'
VERSION = '0.2.1'
DESCRIPTION = 'Dolly is a simple face detection to find your clones!'
AUTHOR = 'Salva Carrión'
AUTHOR_EMAIL = ''
LICENCE = 'MIT'
URL = "https://github.com/salvacarrion/dolly"
DOWNLOAD_URL = "https://github.com/salvacarrion/dolly/tarball/{}".format(VERSION)

ENTRY_POINTS = {
    'console_scripts': (
        'dolly = dolly.cli:main',
    ),
}

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      url=URL,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENCE,
      packages=find_packages(),
      install_requires=requirements,
      zip_safe=False,
      entry_points=ENTRY_POINTS
      )