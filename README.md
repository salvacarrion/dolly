# Dolly
Dolly is a simple program to find faces in a image or in a directory,
crop them, draw boxes, landmarks,... Then there are some funny functions to
find your doubles!

This project is based on [dlib](http://dlib.net) and [face_recognition](https://github.com/ageitgey/face_recognition)

## Installation

### Requirements

  * Python 3.3+ or Python 2.7
  * macOS or Linux (Windows not officially supported, but might work)

### Installation Options:

#### Installing on Mac or Linux

Install this module from pypi using `pip3` (or `pip2` for Python 2):

```
pip3 install ./dolly
```


## Usage

### Command-Line Interface

I like to create an alias in `.bash_profile/.bashrc` to access easily.

    alias dolly="python3 /.../Projects/dolly/dolly/main.py"


#### `findfaces` command line tool
Find faces in an image, and optionally, they can be cropped and saved in a directory.

    ```
    usage: main.py [-h] -f FILENAME_OR_NP_ARRAY [-d SAVE_PATH] command


    $ dolly vector -f ./obama.jpg
    - Face 1: (top=44, right=187, bottom=152, left=79) - 108x108px
    ```

![](https://github.com/salvacarrion/dolly/raw/master/docs/images/findfaces.png)


#### `findfacesdir` command line tool
Find faces in all the images of a directory, then, the faces are cropped and saved into another directory.

    ```
    usage: main.py [-h] -d DIRECTORY -d2 SAVE_PATH [-m MAX_FACES] command


    $dolly findfacesdir -d ./original -d2 ./cropped
    Reading directory...

    Finding faces (1) in: obama_and_biden.jpg
    - Face 1: (top=449, right=923, bottom=634, left=737) - 186x185px
    - Face 2: (top=390, right=1356, bottom=613, left=1133) - 223x223px
    - Face 3: (top=1062, right=1749, bottom=1216, left=1594) - 155x154px

    Finding faces (4) in: obama.jpg
    - Face 1: (top=44, right=187, bottom=152, left=79) - 108x108px
    ```


#### `draw_boxes` command line tool

Draw a rectangle on the face

    ```
    usage: main.py [-h] -f FILENAME_OR_NP_ARRAY [-s SAVE_PATH] command

    $dolly draw_boxes -f obama.jpg
    ```

![](https://github.com/salvacarrion/dolly/raw/master/docs/images/rectangle.jpg)


#### `draw_landmarks` command line tool

Draw the set of landmarks on the face

    ```
    usage: main.py [-h] -f FILENAME_OR_NP_ARRAY [-s SAVE_PATH] command

    $dolly draw_landmarks -f obama.jpg
    ```

![](https://github.com/salvacarrion/dolly/raw/master/docs/images/landmarks.jpg)


## Funny stuff

### Find your clone!

I've created a simple `sqlite` database using a few thousand images from
[CelebA](http://mmlab.ie.cuhk.edu.hk/projects/CelebA.html) to play a bit.

A script like this:

    ```
    #!/usr/bin/env python3

    from dolly import *

    findclones('./some_face.jpg', top_k=10, database='data/faces_small.sqlite)
    ```

...should return the top 10 most similar images found in your database. And with a simple visualization it looks pretty cool.

```
Connecting to DB...
Distance=0.40746634721648173; original=107167.jpg
Distance=0.4889576149502122; original=020690.jpg
Distance=0.5589136585105391; original=055150.jpg
Distance=0.5598040234357228; original=076761.jpg
Distance=0.5804593914355708; original=016137.jpg
Distance=0.5837395193877429; original=008446.jpg
Distance=0.5873013908017849; original=034369.jpg
Distance=0.5974321872132632; original=010395.jpg
Distance=0.6012312733115952; original=089172.jpg
Distance=0.6048747076109878; original=075257.jpg
```

*(I'll try to upload an online demo)*