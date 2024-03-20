import math
import ChessEngine

def minimax( gs, depth ):
    return alphabeta( gs, depth, -math.inf, math.inf )

def alphabeta( gs, depth, a, b ):
    if gs.checkMate or gs.staleMate or depth == 0:
        return gs.evaluate()

    for move in gs.getValidMoves():
        gs.makeMove(move)
        a = max( a, -alphabeta(gs, depth-1, -b, -a ))
        gs.undoMove()
        if a >= b:
            return a
    return a