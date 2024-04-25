# A program to illustrate Zobrist Hashing Algorithm
# Taken from GeeksforGeeks
# at https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-5-zobrist-hashing/amp/


import random  
# Generates a Random number from 0 to 2^64-1

def randomInt():

    min = 0

    max = pow(2, 64)

    return random.randint(min, max)

  
# This function associates each piece with
# a number

def indexOf(piece):

    if (piece=='wp'):

        return 0

    elif (piece=='wN'):

        return 1

    elif (piece=='wB'):

        return 2

    elif (piece=='wR'):

        return 3

    elif (piece=='wQ'):

        return 4

    elif (piece=='wK'):

        return 5

    elif (piece=='bp'):

        return 6

    elif (piece=='bN'):

        return 7

    elif (piece=='bB'):

        return 8

    elif (piece=='bR'):

        return 9

    elif (piece=='bQ'):

        return 10

    elif (piece=='bK'):

        return 11

    else:

        return -1

  
# Initializes the table

def initTable():

    # 8x8x12 array

    ZobristTable = [[[randomInt() for k in range(12)] for j in range(8)] for i in range(8)]

    return ZobristTable

  
# Computes the hash value of a given board

def initHash(board, ZobristTable):

    h = 0

    for i in range(8):

        for j in range(8):

            if (board[i][j] != '--'):

                piece = indexOf(board[i][j])

                h ^= ZobristTable[i][j][piece]

    return h

# A function that hashes the current gs given previous hash and current move
def hashMove(move, previous, Zobrist):
    
    newHash = previous ^ Zobrist[move.startRow][move.startCol][indexOf(move.pieceMoved)]
    newHash = newHash ^ Zobrist[move.endRow][move.endCol][indexOf(move.pieceMoved)]
    if move.pieceCaptured != "--":
        newHash = newHash ^ Zobrist[move.endRow][move.endCol][indexOf(move.pieceCaptured)]

    return newHash
