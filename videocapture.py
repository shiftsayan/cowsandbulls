'''
This file was used to build and debug the OCR video capture. Now it has been
rendered moot due to imageinput.py which integrates with tkinter. RIP.

The sources are the same as imageinput.py
'''

####################################
# Modules
####################################

import sys

for p in sys.path:
    if p.startswith('/System/Library/Frameworks/Python.framework/Versions/2.7/Extras'):
        sys.path.remove(p)

import cv2
import numpy

from isolation import *
from ocr import *

####################################
# Actual Function
####################################

def readWord():
    # Setup reference to (default) webcam
    cap = cv2.VideoCapture(0)

    # Initialize result frame
    ret, result = cap.read()

    # Magic Numbers
    fmx = 0.7
    rmx = 0.65
    tmx = 0.15112
    height, width, _ = result.shape

    # Dimensions
    width,  height  = int(width * fmx), int(height * fmx)
    rWidth, rHeight = int(width * rmx), int(height * rmx)
    tWidth, tHeight = width//2 - rWidth//2, int(height * tmx)

    # Coordinates
    x1, y1 = width//2 - rWidth//2, height//2 - rHeight//2
    x2, y2 = width//2 + rWidth//2, height//2 + rHeight//2

    while True:
        # Capture frame-by-frame
        _, frame = cap.read()

        # Preprocessing
        resized = cv2.resize(frame, (0, 0), fx=fmx, fy=fmx)
        result = resized.copy()

        # Draw input boundary and text
        texted = cv2.putText(resized, "Press 's' to enter.", (tWidth, tHeight), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        rected = cv2.rectangle(texted, (x1, y1), (x2, y2), (0, 255, 0), thickness=2, lineType=8, shift=0)

        # Display the flipped frame with boundary
        cv2.imshow('Show your word to the camera!', rected)

        # Exit control
        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.destroyAllWindows()
            break

    # Zoom into ROI
    zoomed = perspectiveTransform(result, numpy.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], dtype = "float32"))
    # cv2.imshow('Resized', zoomed)
    # cv2.waitKey(0)
    gray = cv2.cvtColor(zoomed, cv2.COLOR_BGR2GRAY)

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

    return ocr(gray)
