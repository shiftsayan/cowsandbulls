'''
This file deals with the keyboard inputs of the words.
'''

####################################
# Modules
####################################

import string

from cowsandbulls import *
from ai import *

####################################
# Character Input
####################################

def characterInput(char, data):
    # Move and check
    data.curWord[data.curWord.index(None)] = char.upper()
    # Undo move for illegal moves
    if wordContainsRepeats(data.curWord):
        data.message = "The word cannot contain repeated letters!"
        try:    index = data.curWord.index(None) - 1
        except: index = -1
        data.curWord[index] = None
    # Completed word
    if data.curWord[-1] != None:
        data.message = "Press 'Enter' to confirm this word."

def backspaceInput(data):
    try:
        data.curWord[data.curWord.index(None) - 1] = None
    except:
        data.message = None
        data.curWord[-1] = None

def enterInput(data):
    if None in data.curWord: return
    data.stage = not data.stage
    data.message = ""
    data.curWord, data.curTarget = [ None ] * WORDLENGTH, data.curWord
    if data.mode == "ai": data.curWord, data.aiGuesses, data.aiChoices = nextGuess(None)

####################################
# Human Inputs
####################################

# state = 0
def humanWordInput(char, data):
    if char in string.ascii_letters and data.curWord[-1] == None: characterInput(char, data)
    elif char == "BackSpace": backspaceInput(data)
    elif char == "Return": enterInput(data)

# state = 1
def humanWordGuess(char, data):
    if ((char in string.ascii_letters and data.mode == "human") or (char in string.digits and data.mode == "ai")) and data.curWord[-1] == None: characterInput(char, data)
    elif char == "BackSpace": backspaceInput(data)
    elif char == "Return":
        if None in data.curWord: return
        # Calculate cowsandbulls and append to guesses
        winState, cowCount, bullCount = returnCowsAndBulls(data.curWord, data.curTarget)
        data.guesses.append( [ data.curWord, cowCount, bullCount ] )
        data.pvpScore = getCowsAndBulls(data)
        # Decrement turnsLeft
        data.turnsLeft -= 1
        # Lose State
        if not winState:
            if not data.betweenRounds:
                # Incorrect guess but turns left
                if data.turnsLeft > 0:
                    data.message = "You got %d cow(s) and %d bull(s). You have %d turn(s) left." % (cowCount, bullCount, data.turnsLeft)
                    data.curWord = [ None ] * WORDLENGTH
                # Incorrect guess and turns not left
                else:
                    data.message = "You are out of turns! Press 'Enter' to continue."
                    data.curWord = data.curTarget
                    # Change to betweenRounds
                    data.betweenRounds = 1
            # betweenRounds Mode
            elif data.betweenRounds:
                data.message = ""
                data.betweenRounds = 0
                # Reset player
                data.stage = not data.stage
                # Reset
                data.curWord, data.curTarget = [ None ] * WORDLENGTH, [ None ] * WORDLENGTH
        # Win State
        elif winState:
            if not data.betweenRounds:
                data.message = "You guessed the word! Press 'Enter' to continue."
                # Increment score
                if data.arena: data.score[data.pID] += 1
                else: data.score[1 - data.player] += 1
                # Change to betweenRounds
                data.betweenRounds = 1
            # betweenRounds Mode
            elif data.betweenRounds:
                data.message       = ""
                data.betweenRounds = 0
                # Reset player, stage, turns, and guesses
                data.stage     = not data.stage
                data.player    = not data.player
                data.turnsLeft = data.maxTurns
                data.guesses   = []
                data.pvpScore  = getCowsAndBulls(data)
                # Reset word
                data.curWord, data.curTarget = [ None ] * WORDLENGTH, [ None ] * WORDLENGTH

####################################
# AI Inputs
####################################

# state = 0
def aiWordInput(char, data):
    if data.player == 0:
        if char == "Return":
            data.stage   = not data.stage
            data.curWord = data.aiGuess
            data.message = "Enter the number of cows and bulls."
    elif data.player == 1:
        data.curTarget = returnRandomWord()
        data.stage     = not data.stage
        data.message   = ""

# state = 1
def aiWordGuess(char, data):
    if data.player == 0:   aiScoreInput(char, data)
    elif data.player == 1: humanWordGuess(char, data)

def aiScoreInput(char, data):
    if char in string.digits and data.pvcScore[-1] == None:
        # Move and check
        data.pvcScore[data.pvcScore.index(None)] = int(char)
        # Undo move for illegal moves
        if sum([i if i != None else 0 for i in data.pvcScore]) > 4:
            data.message = "The word cannot have more than 4 cows and bulls!"
            try:    index = data.pvcScore.index(None) - 1
            except: index = -1
            data.pvcScore[index] = None
        # Completed Score
        if data.pvcScore[-1] != None:
            data.message = "Press 'Enter' to confirm this score."
    elif char == "BackSpace":
        try:
            data.pvcScore[data.pvcScore.index(None) - 1] = None
        except:
            data.message      = None
            data.pvcScore[-1] = None
    elif char == "Return":
        data.guesses.append( [ data.curWord, data.pvcScore[0], data.pvcScore[1] ] )
        if data.pvcScore == [0, 4]:
            data.message  = "The AI guessed the word!"
            data.stage    = not data.stage
            data.player   = not data.player
            data.curWord  = [ None ] * WORDLENGTH
            data.pvcScore = [ None, None ]
            data.guesses  = []
            data.aiGuess, data.aiGuesses, data.aiChoices = nextGuess(None)
            data.score[1] += 1
        elif None not in data.pvcScore:
            data.message = "Enter the number of cows and bulls."
            data.curWord, data.aiGuesses, data.aiChoices = nextGuess(tuple(data.pvcScore), data.aiGuesses, data.aiChoices)
            if data.curWord == -1:
                data.wrongscores = 1
                data.stage       = not data.stage
                data.player      = not data.player
                data.curWord     = [ None ] * WORDLENGTH
                data.guesses     = []
            data.pvcScore = [ None , None ]
