'''
This file was used to test the AI for the game. Theoretically, it should be able
to guess the given number in upto 8 moves and within 5-6 guesses on average.
'''

####################################
# Modules
####################################

from cowsandbulls import WORDLENGTH, returnCowsAndBulls
from ai import init, nextGuess

####################################
# Test Function
####################################

def testAI():
    allWords = init()[1]
    allTries = []

    counts = dict()

    for word in allWords:
        winState = 0
        guess, guesses, choices = nextGuess(None)
        tries = 1

        while not winState:
            # Check current guess
            winState, cows, bulls = returnCowsAndBulls(guess, word)
            if winState: allTries.append(tries)

            # Get next guess
            guess, guesses, choices = nextGuess((cows, bulls,), guesses, choices)
            tries += 1

            # Oops
            if guess == -1: print("AI doesn't work.")

        counts[tries] = counts.get(tries, 0) + 1

    print(counts)

testAI()
