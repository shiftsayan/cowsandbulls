'''
This file is used to apply a perspective transform on the given image. It also
has the ability to apply it on images not in the frame (isolation function) but
that wasn't used in this project specifically.

I refered to multiple tutorials / StackOverflow answers online to learn this.
Perspective Transforms in OpenCV: https://docs.google.com/presentation/d/16GrQydwwljdta1kFb26GG9N3Da-69vx2_Ysw0LrT1eM/edit#slide=id.g2aadb1d8b7_2_210
Detecting the Vertices: https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
'''

####################################
# Modules
####################################

import sys

for p in sys.path:
    if p.startswith('/System/Library/Frameworks/Python.framework/Versions/2.7/Extras'):
        sys.path.remove(p)

import numpy
import cv2
import math

####################################
# Helper Function
####################################

def distanceFormula(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

####################################
# Obtain Corners of Rectangle
####################################

# Source: https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
def findVertices(points):
    # Ininitalize 4 x 2 NumPy array to store coordinates of vertices in
    # clockwise order, i.e. [TL, TR, BR, BL]
    coordinates = numpy.zeros((4, 2), dtype = "float32")

    s = points.sum(axis = 1)
    d = numpy.diff(points, axis = 1)

    # TL has smallest sum
    coordinates[0] = points[numpy.argmin(s)]
    # TR has smallest difference
    coordinates[1] = points[numpy.argmin(d)]
    # BR has largest sum
    coordinates[2] = points[numpy.argmax(s)]
    # BL has largest difference
    coordinates[3] = points[numpy.argmax(d)]

    # Return the ordered coordinates
    return coordinates

####################################
# perspectiveTransform / perspectiveZoom
####################################

def perspectiveTransform(image, points):
    # Get vertex coordinates
    tl, tr, br, bl = findVertices(points)

    # Compute width and height of the new image
    # Maximum of distance(TL, TR) and distance(BL, BR)
    width  = int(max(distanceFormula(br[0], br[1], bl[0], bl[1]), distanceFormula(tr[0], tr[1], tl[0], tl[1])))
    # Maximum of distance(TR, BR) and distance(TL, BL)
    height = int(max(distanceFormula(tr[0], tr[1], br[0], br[1]), distanceFormula(tl[0], tl[0], bl[0], bl[1])))

    # Compute perspectiveTransform matrix
    M = cv2.getPerspectiveTransform( numpy.array([tl, tr, br, bl], dtype = "float32"),
                                     numpy.array([ [0, 0], [width, 0], [width, height], [0, height]], dtype = "float32")
                                   )

    # Apply perspectiveTransform
    result = cv2.warpPerspective(image, M, (width, height))

    # Return transformed images
    return result

####################################
# Isolate paper from image
####################################

def isolation(image):
    # Preprocessing
    # im_rsiz = cv2.resize(image, (0, 0), fx=0.5, fy=0.5) # (uncomment if required)
    # im_gray = cv2.cvtColor(im_rsiz, cv2.COLOR_BGR2GRAY)
    im_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    im_blur = cv2.GaussianBlur(im_gray, (5, 5), 0)
    im_edge = cv2.Canny(im_blur, 50, 200, 255)

    # Find countours in image
    _, contours, _ = cv2.findContours(im_edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # im_cont = cv2.drawContours(image, contours, -1, (0,255,0), 3)
    # Sort the countours in decreasing order of areas
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Initialize the paper
    paper = None

    # Source: https://docs.opencv.org/3.1.0/dd/d49/tutorial_py_contour_features.html
    for contour in contours:
        # Maximum distance of contour from given contour
        epsilon = 0.05 * cv2.arcLength(contour, True) # 10% of perimeter of contour
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # The paper will be the largest contour with 4 vertices
        if len(approx) == 4:
        	paper = approx
        	break

    if paper == None: raise Exception("Couldn't detect.")

    # Convert NumPy array to 2D list
    paperCoordinates = paper.reshape(4, 2)

    im_warp = perspectiveTransform(im_gray, paperCoordinates)
    im_zoom = perspectiveTransform(image, paperCoordinates)

    return image, im_warp, im_zoom
