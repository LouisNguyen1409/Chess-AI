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
    # Set checkmate/stalemate flags
    terminal, winner = isCheckmate(gs)
    if terminal: 
        if winner == 0:
            return 0
        else:
            return white * side * winner * (10000 + 100 * depth)
        
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

def isCheckmate(self):
    moves = []
    self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
    if self.whiteTurn:
        kingRow = self.whiteKingLocation[0]
        kingCol = self.whiteKingLocation[1]
    else:
        kingRow = self.blackKingLocation[0]
        kingCol = self.blackKingLocation[1]

    if self.inCheck:
        if len(self.checks) == 1:
            moves = self.getAllPossibleMoves()
            check = self.checks[0]
            checkRow = check[0]
            checkCol = check[1]
            pieceChecking = self.board[checkRow][checkCol]
            validSqs = []
            if pieceChecking[1] == 'N':
                validSqs = [(checkRow, checkCol)]
            else:
                for i in range(1, 8):
                    validSq = (kingRow + check[2] * i, kingCol + check[3] * i)
                    validSqs.append(validSq)
                    if validSq[0] == checkRow and validSq[1] == checkCol:
                        break
            for i in range(len(moves) - 1, -1, -1):
                if moves[i].pieceMoved[1] != 'K':
                    if not (moves[i].endRow, moves[i].endCol) in validSqs:
                        moves.remove(moves[i])
        else:
            self.KingMoves(kingRow, kingCol, moves)
    else:
        moves = self.getAllPossibleMoves()

    if len(moves) == 0:
        if self.inCheck:
            if not self.whiteTurn:
                return True, 1
            else:
                return True, -1
        else:
            return True, 0

    return False, 0