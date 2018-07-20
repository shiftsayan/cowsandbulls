'''
This file controls the input for the OCR. Bundles in tkinter and OpenCV using
the provided template for the barebones stuff.
https://github.com/VasuAgrawal/112-opencv-tutorial/blob/master/opencvTkinterTemplate.py

I refered to multiple tutorials / StackOverflow answers online to learn this.
Contouring/Thresholding in OpenCV: https://docs.google.com/presentation/d/16GrQydwwljdta1kFb26GG9N3Da-69vx2_Ysw0LrT1eM/edit#slide=id.g2aadb1d8b7_3_11
How to make multiple tkinter windows: https://stackoverflow.com/questions/47520170/opening-another-tkinter-window-from-one-tkinter-window?noredirect=1#comment81998192_47520170
'''

####################################
# Modules
####################################

import sys

for p in sys.path:
    if p.startswith('/System/Library/Frameworks/Python.framework/Versions/2.7/Extras'): sys.path.remove(p)

import numpy
import cv2

from tkinter import *
from PIL import Image, ImageTk

import string
import time

from isolation import *
from ocr import *
from cowsandbulls import *

####################################
# Functions
####################################

# Source: https://github.com/VasuAgrawal/112-opencv-tutorial/blob/master/opencvTkinterTemplate.py
def opencvToTk(frame):
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_image)
    tk_image = ImageTk.PhotoImage(image=pil_img)
    return tk_image

####################################
# Animation Framework
####################################

def init(data):
    data.ocrmode = "input"

    # Initialize the webcams
    camera = cv2.VideoCapture(data.camera_index)
    data.camera = camera

    # Magic Numbers
    data.fmx = 0.7
    data.rmx = 0.65
    data.tmx = 0.15112

    # Obtain first frame to calculate height and width
    _, ff = data.camera.read()
    height, width, _ = ff.shape

    # Dimensions
    data.width,  data.height   = int(width * data.fmx), int(height * data.fmx)
    data.rWidth, data.rHeight  = int(data.width * data.rmx), int(data.height * data.rmx)
    data.tWidth, data.tHeight  = data.width//2 - data.rWidth//2, int(data.height * data.tmx)

    # Coordinates
    data.x1, data.y1 = data.width//2 - data.rWidth//2, data.height//2 - data.rHeight//2
    data.x2, data.y2 = data.width//2 + data.rWidth//2, data.height//2 + data.rHeight//2

    data.message = ""

def mousePressed(event, data):
    pass

def keyPressed(event, data):
    # Restart
    if event.keysym == "Escape": init(data)
    # Mode specific
    elif data.ocrmode == "input": inputKeyPressed(event, data)
    elif data.ocrmode == "edit": editKeyPressed(event, data)

def inputKeyPressed(event, data):
    if event.keysym == "s" or "S":
        data.ocrmode = "edit"
        data.zoomed = perspectiveTransform(data.frame, numpy.array([[data.x1, data.y1], [data.x2, data.y1], [data.x2, data.y2], [data.x1, data.y2]], dtype = "float32"))
        data.zoomed = cv2.cvtColor(data.zoomed, cv2.COLOR_BGR2GRAY)
        data.curWord = list(ocr(data.zoomed))
        data.curChar = 0
        data.message = getMessage(data)

def getMessage(data):
    word = data.curWord
    if len(word) > WORDLENGTH:
        data.drawWord = 0
        return "The word cannot contain more than 4 characters. Press 'Escape' to try again."
    elif len(word) < WORDLENGTH:
        data.drawWord = 0
        return "The word cannot contain less than 4 characters. Press 'Escape' to try again."
    elif wordContainsRepeats(data.curWord):
        data.drawWord = 1
        return "The word cannot contain repeated letters! Use arrow keys to change the characters."
    else:
        data.drawWord = 1
        return "Press 'Enter' to confirm this word. Use arrow keys to change the characters."

def editKeyPressed(event, data):
    if event.keysym == "Return":
        if wordContainsRepeats(data.curWord): data.message = "The word cannot contain repeated letters! Use arrow keys to change the characters."
        else: data.top.quit()
    elif event.keysym == "Left": data.curChar = (data.curChar - 1) % WORDLENGTH
    elif event.keysym == "Right": data.curChar = (data.curChar + 1) % WORDLENGTH
    elif event.keysym in string.ascii_letters:
        data.curWord[data.curChar] = event.keysym.upper()

def timerFired(data):
    pass

def cameraFired(data):
    # Preprocessing
    data.frame = cv2.resize(data.frame, (0, 0), fx=data.fmx, fy=data.fmx)

    # Draw input boundary and text
    data.frame = cv2.putText(data.frame, "Press 's' to enter.", (data.tWidth, data.tHeight), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
    data.frame = cv2.rectangle(data.frame, (data.x1, data.y1), (data.x2, data.y2), (0, 255, 0), thickness=2, lineType=8, shift=0)

def drawCamera(canvas, data):
    data.tk_image = opencvToTk(data.frame)
    canvas.create_image(data.width/2, data.height/2, image=data.tk_image)

def drawEditScreen(canvas, data):
    drawMessage(canvas, data)
    drawTiles(canvas, data)

def drawTiles(canvas, data):
    # Magic Numbers
    tileGapMx = 1/50
    tileWMx = 1/6
    tileHMx = 1/2
    # Draw Tiles
    for i in range(WORDLENGTH):
        x1 = data.width * tileGapMx / 2 + data.width / 2 - (WORDLENGTH/2 - i) * data.width * (tileGapMx + tileWMx)
        x2 = x1 + data.width * tileWMx
        y1 = data.height * tileHMx - data.width * tileWMx / 2
        y2 = y1 + data.width * tileWMx
        fill = "red" if i == data.curChar else "black"
        canvas.create_rectangle(x1, y1, x2, y2, fill=fill, width=0)
        # Draw Character
        if data.drawWord and data.curWord[i] != None: canvas.create_text((x1+x2)//2, (y1+y2)//2, text=data.curWord[i], fill="white", font="Courier 60")

def drawMessage(canvas, data):
    # Magic Numbers
    messageWMx = 1/4 - 3/26
    messageHMx = 2/7
    # Text
    canvas.create_text(data.width * messageWMx, data.height * messageHMx, anchor=W, text=data.message, font="Courier")

def redrawAll(canvas, data):
    if data.ocrmode == "input": drawCamera(canvas, data)
    elif data.ocrmode == "edit": drawEditScreen(canvas, data)

def imageRun(parent, width=640, height=360):

    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.camera_index = 0

    data.timer_delay = 100 # ms
    data.redraw_delay = 50 # ms

    # Initialize variables
    init(data)

    # Make tkinter window and canvas
    data.top = Toplevel(parent)
    data.top.title("OCR")
    canvas = Canvas(data.top, width=data.width, height=data.height)
    canvas.pack()

    # Basic bindings. Note that only timer events will redraw.
    data.top.bind("<Button-1>", lambda event: mousePressed(event, data))
    data.top.bind("<Key>", lambda event: keyPressed(event, data))

    # Timer fired needs a wrapper. This is for periodic events.
    def timerFiredWrapper(data):
        # Ensuring that the code image_runs at roughly the right periodicity
        start = time.time()
        timerFired(data)
        end = time.time()
        diff_ms = (end - start) * 1000
        delay = int(max(data.timer_delay - diff_ms, 0))
        data.top.after(delay, lambda: timerFiredWrapper(data))

    # Wait a timer delay before beginning, to allow everything else to
    # initialize first.
    data.top.after(data.timer_delay, lambda: timerFiredWrapper(data))

    def redrawAllWrapper(canvas, data):
        start = time.time()

        # Get the camera frame and get it processed.
        _, data.frame = data.camera.read()
        cameraFired(data)

        # Redrawing code
        canvas.delete(ALL)
        redrawAll(canvas, data)

        # Calculate delay accordingly
        end = time.time()
        diff_ms = (end - start) * 1000

        # Have at least a 5ms delay between redraw. Ideally higher is better.
        delay = int(max(data.redraw_delay - diff_ms, 5))

        data.top.after(delay, lambda: redrawAllWrapper(canvas, data))

    # Start drawing immediately
    data.top.after(0, lambda: redrawAllWrapper(canvas, data))

    # Loop tkinter
    data.top.mainloop()

    # Once the loop is done, release the camera.
    print("Releasing camera!")
    data.camera.release()
    data.top.destroy()

    return data.curWord
