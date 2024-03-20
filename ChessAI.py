import math
import ChessEngine
import copy

def getMoves(gs):
    moves = gs.getValidMoves()
    underpromotions = []
    for move in moves:
        if move.isPawnPromotion:
            # Append underpromotion to list
            for piece in ['R', 'B', 'N']:
                newMove = copy.deepcopy(move)
                newMove.promotedPiece = piece
                underpromotions.append(newMove)
                
            move.promotedPiece = 'Q'

    moves.extend(underpromotions)
    return moves

def minimax( gs, depth, white ):
    a = -math.inf
    b = math.inf
    if gs.checkMate or gs.staleMate or depth == 0:
        return None

    bestMove = None
    for move in getMoves(gs):
        gs.makeMove(move, False)
        new_a = -alphabeta(gs, depth-1, white, -b, -a )
        if (new_a > a):
            bestMove = move
            a = new_a
        gs.undoMove()

    return bestMove

def alphabeta( gs, depth, white, a, b ):
    if gs.checkMate or gs.staleMate or depth == 0:
        return white * gs.evaluate()

    for move in getMoves(gs):
        gs.makeMove(move, False)
        a= max( a, -alphabeta(gs, depth-1, white, -b, -a ))
        gs.undoMove()
        if a >= b:
            return a
    return a