'''
This file does the heavy-lifting of training the OCR.

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
import numpy
import os

from isolation import *

####################################
# Magic Numbers
####################################

MINIMUMCONTOURAREA = 50
MAXIMUMCONTOURAREA = 1200
MINIMUMCHARACTERHEIGHT = 28

####################################
# Dataset
####################################

features =  numpy.empty((0,100))
labels = []

####################################
# Iterate over all characters in the dataset
# Files saved as <char>.jpg
####################################

for filename in os.listdir("./ocr/jpg/"):
    # Ignore fucking .DS_Store
    if filename == ".DS_Store": continue

    print("Training " + filename + "...")

    # Load current dataset
    image = cv2.imread("./ocr/jpg/" + filename)

    # Preprocessing
    im_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    im_blur = cv2.GaussianBlur(im_gray, (5,5), 0)
    im_trsh = cv2.adaptiveThreshold(im_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    # Detect contours in im_trsholded image
    _, contours, _ = cv2.findContours(im_trsh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

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
                roi = numpy.float32(roi)
                # Append ASCII value of character and ROI to features and sample
                features = numpy.append(features, roi, 0)
                labels.append(ord(filename[0]))

labels = numpy.array(labels, numpy.float32)
labels = labels.reshape((labels.size, 1))

print("Trained!")

# Save training data to files
numpy.savetxt('ocr_features.data', features)
numpy.savetxt('ocr_labels.data', labels)
