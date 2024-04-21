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
    return move_ordering(moves, gs)

def minimax( gs, depth, white ):
    a = -math.inf
    b = math.inf
    if gs.checkMate or gs.staleMate or depth == 0:
        return None

    bestMove = None
    for move in getMoves(gs):
        gs.makeMove(move, False)
        new_a = -alphabeta(gs, depth-1, white, -b, -a , -1)
        if (new_a > a):
            bestMove = move
            a = new_a
        gs.undoMove()

    return bestMove

def alphabeta( gs, depth, white, a, b, side):
    if gs.checkMate: 
        return white * side * (10000 + 100 * depth)
    if gs.staleMate:
        return 0
    if depth == 0:
        return white * side * gs.evaluate()

    for move in getMoves(gs):
        gs.makeMove(move, False)
        a= max( a, -alphabeta(gs, depth-1, white, -b, -a , -side))
        gs.undoMove()
        if a >= b:
            return a
    return a

def move_ordering(moves, gs):
    # Captures
    ordered = []
    for move in moves:
        if move.pieceCaptured != "--":
            ordered.append(move)
    
    for move in ordered:
        moves.remove(move)

    # Checks
    checks = []
    for move in moves:
        gs.makeMove(move, False)
        if gs.inCheck:
            checks.append(move)
        gs.undoMove()
    
    for move in checks:
        moves.remove(move)
        ordered.append(move)

    # Put rest of moves
    for move in moves:
        ordered.append(move)

    return ordered
