'''
This file is the main AI for the player v computer mode in the game. It gets
fairly close to the optimal number of tries and can guess most numbers in upto
8 tries, with the modes at 6 and 7.
'''

####################################
# Modules
####################################

import string
from random import shuffle

from cowsandbulls import WORDLENGTH, returnCowsAndBulls

####################################
# Global Variables
####################################

DIGITS = string.digits

####################################
# Generate substrings of length WORDLENGTH
####################################

'''
I wrote this function myself after I had learned it for the midterm from the
course website. This was modified to only return subsets of the required length.
http://www.cs.cmu.edu/~112/notes/notes-recursion-part2.html
'''
def substrings(s):
    result = []
    def powerset(s):
        if len(s) == 0:
            return [ [] ]
        else:
            subsets = [ ]
            for subset in powerset(s[1:]):
                subsets += [subset]
                subsets += [[s[0]] + subset]
            return subsets
    subsets = powerset(list(s))
    for subset in subsets:
        if len(subset) == WORDLENGTH: result.append("".join(subset))
    return result

####################################
# Generate permutations of DIGITS
####################################

'''
I wrote this function myself after I had learned it for the midterm from the
course website.
http://www.cs.cmu.edu/~112/notes/notes-recursion-part2.html
'''
def permute(s):
    if len(s) == 1:
        return s
    else:
        result = []
        permutations = permute(s[1:])
        for permutation in permutations:
            for index in range(len(permutation)+1):
                result.append(permutation[:index] + s[0] + permutation[index:])
        return result

####################################
# Initialize guesses (empty list) and all possible words
####################################

'''
This function is used to generate the first guess for the AI. Uses the random
library.
'''
def init():
    guesses, choices = [], []

    # Find all substrings and permute
    for substring in substrings(DIGITS):
        choices += permute(substring)

    # Randomize list of choices
    shuffle(choices)

    return guesses, choices

####################################
# Return the next guess based on past scores
####################################

'''
This function is the heart of the AI. It returns the next guess of the AI
based on the previous guesses. It guesses the next number by pruning the list
of all possibilities to only those which match the latest score. I wrote the
entire function myself after reading strategies for the game online I had to
change several things to suit the variables I was using.
https://rosettacode.org/wiki/Bulls_and_cows
'''
def nextGuess(score=None, guesses=[], choices=[]):
    # Initialize guesses and choices
    if score == None: guesses, choices = init()

    # Update score and choices
    else:
        # Update score in guesses
        guesses[-1][1] = score
        # Update choices with strings that have score with last guess
        newChoices = []
        # Keep only those words which have the same score with the last guess
        for choice in choices:
            if returnCowsAndBulls(guesses[-1][0], choice)[1:] == score: newChoices.append(choice)
        choices = newChoices

    # Inconsistency (happens due to incorrect scores or letter repetition)
    if choices == []: return -1, [], []

    # New guess
    guess = choices[0]
    guesses.append([guess, (-1, -1,)])

    return list(guess), guesses, choices

####################################
# Return random word for player to guess
####################################

def returnRandomWord():
    return list(init()[1][1])
