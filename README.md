gi# Dolly
Dolly is a simple program to find your doubles

## Design requirements

1. Given an input image, return its vector

    ```
    dolly vector filename
    => [0.56789 0.91285 0.01232 ...]
    ```

2. Given a directory, return a dictionary with the vectors of all the images

    ```
    dolly matrix dir
    => {'filename_1': [0.56789 0.91285 0.01232 ...],
        'filename_2': [0.24987 0.51033 0.12346 ...]
        'filename_3': [0.25951 0.25353 0.00126 ...]}
    ```

3. Given a vector (image) and a list of vectors (dir of images), return the list of vectors sorted by similarity

    ```
    dolly findclones filename dir
    => [[0.999, 'filename_1'],
        [0.731, 'filename_2'],
        [0.325, 'filename_3']]
    ```


## Additional functionality

1. Find faces

    ```
    dolly findfaces filename
    => [[x1, y1, x2, y2], [...]] or None
    ```

2. Find faces, crop them and save them

    ```
    dolly findfaces filename_1 dir_1
    => filename_{0..i} or None
    ```


3. Find a faces in a directory, crop them and save them

    ```
    dolly cropfaces dir dir2
    => number of faces or None
    ```