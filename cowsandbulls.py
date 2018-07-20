'''
This file contains functions that help calculate the score and check word
validity in the game.
'''

####################################
# Global Variables
####################################

WORDLENGTH = 4

####################################
# Cows and Bulls Counter
####################################

def returnCowsAndBulls(guess, target):
    bullCount, cowCount = 0, 0

    # Iterate through the guess
    for i in range(WORDLENGTH):
        if guess[i] == target[i]: bullCount += 1
        elif guess[i] in target: cowCount += 1

    return (bullCount == WORDLENGTH, cowCount, bullCount)

####################################
# Formatted Score Tuple
####################################

def getCowsAndBulls(data):
    if data.mode == "ai" and data.player == 0 and data.stage == 1:
        score = [ "_" if animal == None else animal for animal in data.pvcScore]
    else:
        if data.guesses == []: score = ("??", "??")
        else: score = (str(data.guesses[-1][1]), str(data.guesses[-1][2]))
    return score

####################################
# Word Validity
####################################

def wordContainsRepeats(word):
    letterCount = 0
    for c in word:
        if c != None: letterCount += 1
    wordSet = set(word)
    wordSet.discard(None)
    return letterCount != len(wordSet)
