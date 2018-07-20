'''
This file does the heavy-lifting of the OCR.

I refered to multiple tutorials / StackOverflow answers online to learn this.
kNN Regression in OpenCV: https://docs.opencv.org/3.0-beta/modules/ml/doc/k_nearest_neighbors.html
OCR with kNN Regressions: https://stackoverflow.com/a/9620295/4982987

NOTE: The "OCR with kNN Regressions" tutorial was in OpenCV 2 and I had to
reimplement it myself for Python3.
'''

####################################
# Modules
####################################

import sys

for p in sys.path:
    if p.startswith('/System/Library/Frameworks/Python.framework/Versions/2.7/Extras'): sys.path.remove(p)

import cv2
import numpy as np

from isolation import *

####################################
# Training
####################################

# Load data
features = np.loadtxt('ocr_features.data', np.float32)
labels = np.loadtxt('ocr_labels.data', np.float32)

# Train kNN model
model = cv2.ml.KNearest_create()
model.train(features, cv2.ml.ROW_SAMPLE, labels)

####################################
# Global Variables
####################################

MINIMUMCONTOURAREA     = 1000
MAXIMUMCONTOURAREA     = 7500
MINIMUMCHARACTERHEIGHT = 28
MINIMUMCHARACTERWIDTH  = 15

####################################
# Regression
####################################

def ocr(image):
    # Preprocessing
    im_blur = cv2.GaussianBlur(image, (31, 31), 0)
    im_trsh = cv2.adaptiveThreshold(im_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    # Detect contours in im_trsholded image
    _, contours, _ = cv2.findContours(im_trsh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize result dictionary
    characters = {}

    # Iterate through all detected contours
    for contour in contours:
        # Only for large enough contours
        if MINIMUMCONTOURAREA < cv2.contourArea(contour) < MAXIMUMCONTOURAREA:
            # Find bounding rectangle for the character
            x, y, width, height = cv2.boundingRect(contour)
            # Only for large enough characters
            if height > MINIMUMCHARACTERHEIGHT:
                # Zoom into region of interest
                roi = perspectiveTransform(im_trsh, numpy.array([[x, y], [x+width, y], [x+width, y+height], [x, y+height]]))
                # Resize and reshape region of interest to 10x10 grid
                roi = cv2.resize(roi, (10,10))
                roi = roi.reshape((1, 100))
                roi = np.float32(roi)
                # Implement kNN model
                _, result, _, _ = model.findNearest(roi, k=1)
                # Get character from ASCII
                character = chr(int((result[0][0])))
                # Add character to result
                characters[x] = character

    # Omit overlapping contours
    previousKey = -100
    largeCharacters = {}
    for key in sorted(characters.keys()):
        if key - previousKey < MINIMUMCHARACTERWIDTH: continue
        previousKey = key
        largeCharacters[key] = characters[key]

    word = ""
    for key in sorted(largeCharacters.keys()):
        word += str(largeCharacters[key])

    return word
