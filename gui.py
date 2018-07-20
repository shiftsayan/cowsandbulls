'''
This file contains all of the GUI for the project.
'''

####################################
# Modules
####################################

from tkinter import *
from PIL import ImageTk

from cowsandbulls import *
from wordinput import *
from imageinput import *
from ai import *
from sockets import *

import math
import string
import random
import colors

####################################
# init() Functions
####################################

def startMode(data):
    updateRectangles(data)
    # Magic Numbers
    playWMx = 1/2
    playHMx = 5/7
    rootThreeByTwo = math.sqrt(3) / 2
    # Dimensions
    data.playButtonSize = 70
    data.playButtonPoints = [
                              (data.width * playWMx - rootThreeByTwo * data.playButtonSize//2, data.height * playHMx - data.playButtonSize//2),
                              (data.width * playWMx - rootThreeByTwo * data.playButtonSize//2, data.height * playHMx + data.playButtonSize//2),
                              (data.width * playWMx + data.playButtonSize//2, data.height * playHMx)
                            ]

def optionMode(data):
    data.mousePane = 0

def humanMode(data):
    data.player        = 0      # player1 = 0; player2 = 1
    data.stage         = 0      # give = 0; guess = 1
    data.betweenRounds = 0      # after word has been guessed
    data.score         = [0, 0] # [player1.score, player2.score]

    data.pID       = 0
    data.players   = 1

    data.curWord   = [ None ] * WORDLENGTH
    data.curTarget = []
    data.guesses   = []
    data.pvpScore  = getCowsAndBulls(data)

    data.maxTurns  = 10
    data.turnsLeft = data.maxTurns
    data.message   = None
    data.history   = 0 # Display history

    data.arena     = None # Arena mode

def aiMode(data):
    data.aiGuess, data.aiGuesses, data.aiChoices = nextGuess(None)

    data.pvcScore = [ None, None ]
    data.wrongscores = 0

def init(data):
    data.mode = "start"

    startMode(data)
    optionMode(data)
    humanMode(data)
    aiMode(data)

####################################
# Animation Functions
####################################

def mousePressed(event, data):
    if data.mode == "option":
        if event.x <= data.width//2: data.mode = "human"
        elif event.x > data.width//2: data.mode = "ai"
    elif data.mode == "human" and data.arena == None:
        if event.x <= data.width//2:
            data.arena = 0
        elif event.x > data.width//2:
            data.arena = 1
            startServer(data)

'''
Runs whenever the mouse is moved. Bounded to <Motion>.
'''
def mouseMotion(event, data):
    if data.mode  == "option":
        if event.x <= data.width//2:
            if data.mousePane == 1: beep()
            data.mousePane = 0
        elif event.x > data.width//2:
            if data.mousePane == 0: beep()
            data.mousePane = 1
    if data.mode  == "human" and data.arena == None:
        if event.x <= data.width//2:
            if data.mousePane == 1: beep()
            data.mousePane = 0
        elif event.x > data.width//2:
            if data.mousePane == 0: beep()
            data.mousePane = 1

def keyPressed(event, data):
    # Restart
    if event.keysym == "Escape": init(data)

    # Start Mode
    if data.mode == "start":
        if event.keysym == "P" or event.keysym == "p": data.mode = "rules"

    # Rules Mode
    elif data.mode == "rules":
        if event.keysym == "P" or event.keysym == "p": data.mode = "option"

    # Human Mode
    if data.mode == "human":
        if event.keysym == "space": data.curWord = imageRun(data.root)
        elif event.keysym == "Up": data.history = 1
        elif event.keysym == "Down": data.history = 0
        elif not data.history:
            if data.stage == 0:
                if data.arena and data.player != data.pID: return
                humanWordInput(event.keysym, data)
            elif data.stage == 1:
                if data.arena and data.player == data.pID: return
                humanWordGuess(event.keysym, data)

        # Send the socket message in Arena mode
        if data.arena:
            socket = constructSocket(data)
            if (socket != ""):
              print ("Sending: ", socket,)
              data.server.send(socket.encode())

    # AI Mode
    if data.mode == "ai":
        if event.keysym == "Up": data.history = 1
        elif event.keysym == "Down": data.history = 0
        elif not data.history:
            if data.stage == 0: aiWordInput(event.keysym, data)
            elif data.stage == 1: aiWordGuess(event.keysym, data)

def timerFired(data):
    if data.mode == "start": updateRectangles(data)
    # timerFired receives instructions and executes them
    elif data.arena: receiveSocket(data)

def updateRectangles(data):
    rects = []
    for i in range(10):
        x = random.randint(0, data.width)
        y = random.randint(0, data.height)
        w = random.randint(0.25*data.width, 0.5*data.width)
        h = random.randint(0.25*data.height, 0.5*data.height)
        color = random.choice(["gray99", "gray94", "gray89", "gray84", "gray79"])
        rects.append([x, y, w, h, color])
    data.rects = rects

####################################
# Draw Functions
####################################

def redrawAll(canvas, data):
    if data.mode == "start": drawStartScreen(canvas, data)
    elif data.mode == "rules": drawRulesScreen(canvas, data)
    elif data.mode == "option": drawOptionScreen(canvas, data)
    elif data.history: drawHistoryScreen(canvas, data)
    elif data.mode == "human": drawHumanScreen(canvas, data)
    elif data.mode == "ai": drawAIScreen(canvas, data)

def drawStartScreen(canvas, data):
    drawBackground(canvas, data)
    # Title
    titleWMx = 1/2
    titleHMx = 1/4
    canvas.create_text(data.width * titleWMx, data.height * titleHMx,
                       font="Gotham 50 bold",
                       text="COWS AND BULLS!")
    # Play Button
    canvas.create_polygon(data.playButtonPoints, fill="springGreen4")
    # Subtitle
    subtitleWMx = 1/2
    subtitleHMx = 6/7
    canvas.create_text(data.width * subtitleWMx, data.height * subtitleHMx,
                       font="Gotham 30 bold",
                       text="Press P to play!")

# Idea Credits: Maia Iyer
def drawBackground(canvas, data):
    for x, y, w, h, color in data.rects: canvas.create_rectangle(x, y, x+w, y+h, fill=color, width=0)

def drawRulesScreen(canvas, data):
    # Title
    titleWMx = 1/2
    titleHMx = 1/5
    canvas.create_text(data.width * titleWMx, data.height * titleHMx,
                       font="Gotham 50 bold",
                       text="RULES")
    # Rules
    rules = [ "1. Cows and bulls is a word game.",
              "2. One player thinks of a word that the other player has to guess.",
              "3. BULLS: Guessed characters in the right position",
              "4. COWS: Correct characters but in the wrong position",
              "5. Once the player guesses the word, the roles switch.",
              "6. Play in 2-player, arena, or computer modes.",
              "7. Use the keyboard or webcam to input the word."
            ]
    # Drawing
    rowWMx = 1/15
    rowHMx = 11/30
    rowHDx = 2/23
    for i in range(len(rules)):
        canvas.create_text(data.width * rowWMx, data.height * (rowHMx + i * rowHDx),
                           font="Courier 20",
                           anchor=W,
                           text=rules[i])

def drawOptionScreen(canvas, data):
    # Panes
    if data.mousePane == 0: canvas.create_rectangle(0, 0, data.width//2, data.height, fill="gray94", width=0)
    elif data.mousePane == 1: canvas.create_rectangle(data.width//2, 0, data.width, data.height, fill="gray94", width=0)
    # Options
    drawPvPOption(canvas, data)
    drawPvCOption(canvas, data)

def drawPvPOption(canvas, data):
    # Load Image
    data.pvpPath = "./images/human.png"
    data.pvpIcon = ImageTk.PhotoImage(file=data.pvpPath)
    # Magic Numbers
    tileWMx = 1/4
    tileHMx = 1/2
    # Insert Image
    canvas.create_image(data.width * tileWMx, data.height * tileHMx, image=data.pvpIcon)

def drawPvCOption(canvas, data):
    # Load Image
    data.pvcPath = "./images/computer.png"
    data.pvcIcon = ImageTk.PhotoImage(file=data.pvcPath)
    # Magic Numbers
    tileWMx = 3/4
    tileHMx = 1/2
    # Insert Image
    canvas.create_image(data.width * tileWMx, data.height * tileHMx, image=data.pvcIcon)

def drawHumanScreen(canvas, data):
    if data.arena == None:
        # Panes
        if data.mousePane == 0: canvas.create_rectangle(0, 0, data.width//2, data.height, fill="gray94", width=0)
        elif data.mousePane == 1: canvas.create_rectangle(data.width//2, 0, data.width, data.height, fill="gray94", width=0)

        drawSingleOption(canvas, data)
        drawDoubleOption(canvas, data)
        return

    for player in [0, 1]:
        drawHumanPlayerTitle(canvas, data, player)
    drawHumanInstruction(canvas, data)
    if data.message != None: drawMessage(canvas, data)
    drawTiles(canvas, data)
    drawCowsAndBulls(canvas, data)
    drawAddOns(canvas, data)

def drawSingleOption(canvas, data):
    # Load Image
    data.singlePath = "./images/single.png"
    data.singleIcon = ImageTk.PhotoImage(file=data.singlePath)
    # Magic Numbers
    tileWMx = 1/4
    tileHMx = 1/2
    # Insert Image
    canvas.create_image(data.width * tileWMx, data.height * tileHMx, image=data.singleIcon)

def drawDoubleOption(canvas, data):
    # Load Image
    data.doublePath = "./images/double.png"
    data.doubleIcon = ImageTk.PhotoImage(file=data.doublePath)
    # Magic Numbers
    tileWMx = 3/4
    tileHMx = 1/2
    # Insert Image
    canvas.create_image(data.width * tileWMx, data.height * tileHMx, image=data.doubleIcon)

def drawHistoryScreen(canvas, data):
    # Magic Numbers
    titleWMx = 1/2
    titleHMx = 1/5
    rowHMx = 5/16
    rowHDx = 1/20
    space = " " * 4
    # Title
    canvas.create_text(data.width * titleWMx, data.height * titleHMx,
                       font="Gotham 40 bold",
                       text="HISTORY")
    # Scores
    for i in range(len(data.guesses)):
        guess = data.guesses[i]
        row = "".join(guess[0]) + space + str(guess[1]) + "C" + space + str(guess[2]) + "B"
        canvas.create_text(data.width * titleWMx, data.height * (rowHMx + i * rowHDx),
                           font="Courier 20",
                           text=row)

def drawAIScreen(canvas, data):
    drawHumanPlayerTitle(canvas, data, 0)
    drawAIPlayerTitle(canvas, data)
    drawAIInstruction(canvas, data)
    if data.message != None: drawMessage(canvas, data)
    drawTiles(canvas, data)
    drawCowsAndBulls(canvas, data)
    drawAddOns(canvas, data)

def drawHumanPlayerTitle(canvas, data, player):
    # Magic Numbers
    scoreBoxLMx = 3/26                  # length
    scoreBoxBMx = 1/11                  # breadth
    scoreBoxWMx = (1/2) * player + 1/4  # width
    scoreBoxHMx = 1/15                  # height
    # Score Box
    canvas.create_rectangle( data.width * (scoreBoxWMx - scoreBoxLMx),
                             data.height * scoreBoxHMx,
                             data.width * (scoreBoxWMx + scoreBoxLMx),
                             data.height * (scoreBoxHMx + scoreBoxBMx),
                             fill=colors.PLAYERSCORESBOX
                           )
    # Text
    if data.arena and data.pID == player: ticker = "YOU: %s" % (data.score[player])
    else: ticker = "PLAYER %d: %s" % (player + 1, data.score[player])
    canvas.create_text( data.width * scoreBoxWMx, data.height * (scoreBoxHMx + scoreBoxBMx/2),
                        text=ticker, fill=colors.PLAYERSCORESTEXT, font="Courier 22")

def drawAIPlayerTitle(canvas, data):
    # Magic Numbers
    scoreBoxLMx = 3/26         # length
    scoreBoxBMx = 1/11         # breadth
    scoreBoxWMx = (1/2) + 1/4  # width
    scoreBoxHMx = 1/15         # height
    # Score Box
    canvas.create_rectangle( data.width * (scoreBoxWMx - scoreBoxLMx),
                             data.height * scoreBoxHMx,
                             data.width * (scoreBoxWMx + scoreBoxLMx),
                             data.height * (scoreBoxHMx + scoreBoxBMx),
                             fill=colors.PLAYERSCORESBOX
                           )
    # Text
    ticker = "AI: %d" % (data.score[1])
    canvas.create_text( data.width * scoreBoxWMx, data.height * (scoreBoxHMx + scoreBoxBMx/2),
                        text=ticker, fill=colors.PLAYERSCORESTEXT, font="Courier 22")

def drawCowsAndBulls(canvas, data):
    for animal in [0, 1]: # 0 = cow; 1 = bull
        # Magic Numbers
        cowsAndBullsBoxLMx = 3/33                  # length
        cowsAndBullsBoxBMx = 1/11                  # breadth
        cowsAndBullsBoxWMx = (1/2) * animal + 1/4  # width
        cowsAndBullsBoxHMx = 10/15                 # height
        # Cows and Bulls Box
        canvas.create_rectangle( data.width * (cowsAndBullsBoxWMx - cowsAndBullsBoxLMx),
                                 data.height * cowsAndBullsBoxHMx,
                                 data.width * (cowsAndBullsBoxWMx + cowsAndBullsBoxLMx),
                                 data.height * (cowsAndBullsBoxHMx + cowsAndBullsBoxBMx),
                                 fill=colors.COWSANDBULLSBOX, width=0
                               )
        if data.mode == "human": score = data.pvpScore
        elif data.mode == "ai": score = getCowsAndBulls(data)
        # Text
        ticker = "%s: %s" % ((1 - animal) * "Cows" + animal * "Bulls", score[animal])
        canvas.create_text( data.width * cowsAndBullsBoxWMx, data.height * (cowsAndBullsBoxHMx + cowsAndBullsBoxBMx/2),
                            text=ticker, fill=colors.PLAYERSCORESTEXT, font="Courier 22")

def drawHumanInstruction(canvas, data):
    # Magic Numbers
    instructionWMx = 1/4 - 3/26
    instructionHMx = 2/9
    # Text
    if data.stage == 0: ticker = "Player %d: Choose a word for Player %d to guess!" % (1 + data.player, 1 + (not data.player))
    if data.stage == 1: ticker = "Player %d: Guess the word Player %d choose!" % (1 + (not data.player), 1 + data.player)
    # Draw
    canvas.create_text(data.width * instructionWMx, data.height * instructionHMx, anchor=W, text=ticker, font="Courier")

def drawAIInstruction(canvas, data):
    # Magic Numbers
    instructionWMx = 1/4 - 3/26
    instructionHMx = 2/9
    # Text
    if data.stage == 0 and data.player == 0:
        ticker = "Player 1: Think of a number for the AI to guess!"
        data.message = "Press 'Enter' when you are done."
    if data.stage == 0 and data.player == 1:
        if not data.wrongscores: ticker = "The AI guessed the number!"
        else: ticker = "The AI couldn't guess your number. Looks like someone messed up the scoring."
        data.message = "Press 'Enter' to start guessing the AI's number."
    if data.stage == 1 and data.player == 0:
        ticker = "The AI is guessing the number you are thinking."
    if data.stage == 1 and data.player == 1:
        ticker = "Player 1: Guess the number the AI choose!"
    canvas.create_text(data.width * instructionWMx, data.height * instructionHMx, anchor=W, text=ticker, font="Courier")

def drawMessage(canvas, data):
    # Magic Numbers
    messageWMx = 1/4 - 3/26
    messageHMx = 2/7
    # Text
    canvas.create_text(data.width * messageWMx, data.height * messageHMx, anchor=W, text=data.message, font="Courier")

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
        canvas.create_rectangle(x1, y1, x2, y2, fill="black")
        # Draw Character
        if data.arena and data.stage == 0 and data.player != data.pID: continue
        if data.curWord[i] != None:
            canvas.create_text((x1+x2)//2, (y1+y2)//2, text=data.curWord[i], fill="white", font="Courier 60")

def drawAddOns(canvas, data):
    # Restart
    # Magic Numbers
    escapeWMx = 1/6
    escapeHMx = 12/13
    # Text
    canvas.create_text(data.width * escapeWMx, data.height * escapeHMx, text="[Esc] Restart", font="Courier")
    # OCR
    # Magic Numbers
    upWMx = 3/6
    upHMx = 12/13
    # Text
    if data.mode != "ai": canvas.create_text(data.width * upWMx, data.height * upHMx, text="[Space] OCR", font="Courier")
    # History
    # Magic Numbers
    historyWMx = 5/6
    historyHMx = 12/13
    # Text
    canvas.create_text(data.width * historyWMx, data.height * historyHMx, text="[Up] History", font="Courier")

####################################
# Sound Helper Functions
####################################

'''
Plays sound when you change the option.
'''
def beep():
    sys.stdout.write('\a')
    sys.stdout.flush()

####################################
# Run Function
####################################

'''
Generic run function with added support for
* sockets
* OpenCV
* mouse motion
* multiple tkinter windows
http://www.cs.cmu.edu/~112/notes/events-example0.py
'''
def run(width=900, height=600):

    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height, fill="white", width=0)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def mouseMotionWrapper(event, canvas, data):
        mouseMotion(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)

    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)

    # create the root and the canvas
    data.root = Tk()
    data.root.title("Cows and Bulls!")
    canvas = Canvas(data.root, width=data.width, height=data.height)
    canvas.pack()

    # set up events
    data.root.bind("<Button-1>", lambda event: mousePressedWrapper(event, canvas, data))
    data.root.bind("<Key>", lambda event: keyPressedWrapper(event, canvas, data))
    data.root.bind('<Motion>', lambda event: mouseMotionWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)

    # and launch the app
    data.root.mainloop()  # blocks until window is closed
    print("42!")

def play():
    run()
