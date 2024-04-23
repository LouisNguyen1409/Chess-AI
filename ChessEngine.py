# Storing the information about the current state of a chess game and determine the valid moves at the current state.
import copy

class GameState():
    def __init__(self):
        # The board is an 8x8 2D List, each element of the list has 2 characters.
        # The first character represents the color of the piece (b or w)
        # The second character represents the type of the piece (King, Queen, Rook, Bishop, Knight, Pawn)
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.piecesMove = {
            "p": self.PawnMoves,
            "R": self.RookMoves,
            "N": self.KnightMoves,
            "B": self.BishopMoves,
            "K": self.KingMoves,
            "Q": self.QueenMoves,
        }
        self.pieceValue = {
            "bp": -1,
            "bR": -5,
            "bN": -3,
            "bB": -3,
            "bQ": -9,
            "bK": 0,
            "wp": 1,
            "wR": 5,
            "wN": 3,
            "wB": 3,
            "wQ": 9,
            "wK": 0,
            "--": 0
        }
        self.whiteTurn = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.checkMate = False
        self.staleMate = False
        self.enpassant = ()
        self.enpassantLog = [self.enpassant]
        self.pins = []
        self.checks = []
        self.currentCastleRight = castleRight(True, True, True, True)
        self.castleRightLog = [castleRight(self.currentCastleRight.wK, self.currentCastleRight.wQ, self.currentCastleRight.bK, self.currentCastleRight.bQ)]

    def makeMove(self, move, humanTurn):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # store history of move
        self.whiteTurn = not self.whiteTurn

        # update king's location
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # promotion
        if move.isPawnPromotion:
            if humanTurn:
                promotedPiece = input("Enter the piece you want to promote to (Q, R, B, N): ")
                promotedPiece = promotedPiece.upper()
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece
            else:
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + move.promotedPiece

        # Enpassant Move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"  # capturing the pawn

        # enpassant update
        if move.pieceMoved[1] == 'p' and (abs(move.startRow - move.endRow) == 2):  # only 2 squares pawn move
            self.enpassant = ((move.startRow + move.endRow) // 2, move.endCol)
        else:
            self.enpassant = ()  # not en passant move

        self.enpassantLog.append(self.enpassant)

        # update castling right - whenever king move or rook move
        self.updateCastleRight(move)
        self.castleRightLog.append(castleRight(self.currentCastleRight.wK, self.currentCastleRight.wQ, self.currentCastleRight.bK, self.currentCastleRight.bQ))

        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteTurn = not self.whiteTurn

            # update king's location
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            if move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            # undo enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--" # leave the landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantLog.pop()
            self.enpassant = copy.deepcopy(self.enpassantLog[-1])

            # undo castling right
            self.castleRightLog.pop()
            self.currentCastleRight = copy.deepcopy(self.castleRightLog[-1])

            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

            self.checkMate = False
            self.staleMate = False

    def updateCastleRight(self, move):
        if move.pieceMoved == "wK":
            self.currentCastleRight.wK = False
            self.currentCastleRight.wQ = False
        elif move.pieceMoved == "bK":
            self.currentCastleRight.bK = False
            self.currentCastleRight.bQ = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastleRight.wQ = False
                elif move.startCol == 7:
                    self.currentCastleRight.wK = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastleRight.bQ = False
                elif move.startCol == 7:
                    self.currentCastleRight.bK = False

        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastleRight.wQ = False
                elif move.endCol == 7:
                    self.currentCastleRight.wK = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastleRight.bQ = False
                elif move.endCol == 7:
                    self.currentCastleRight.bK = False

    def getValidMoves(self):
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
                self.checkMate = True
            else:
                self.staleMate = True

        return moves

    def getAllPossibleMoves(self):
        moves = []
        dimension = len(self.board)
        for row in range(dimension):
            for col in range(dimension):
                turnColor = self.board[row][col][0] # the color of piece
                if (turnColor == "w" and self.whiteTurn) or (turnColor == "b" and not self.whiteTurn):
                    piece = self.board[row][col][1]
                    self.piecesMove[piece](row, col, moves)
        return moves

    def PawnMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteTurn:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.whiteTurn:
            if self.board[row - 1][col] == "--":
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((row, col), (row - 1, col), self.board))
                    if row == 6:
                        if self.board[4][col] == "--":
                            moves.append(Move((row, col), (4, col), self.board))
            if col - 1 >= 0:
                if self.board[row - 1][col - 1][0] == "b":
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((row, col), (row - 1, col - 1), self.board))
                elif (row - 1, col - 1) == self.enpassant:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < col:
                            insideRange = range(kingCol + 1, col - 1)
                            outsideRange = range(col + 1, 8)
                        else:
                            insideRange = range(kingCol - 1, col, -1)
                            outsideRange = range(col - 2, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == 'b' and (square[1] == 'R' or square[1] == 'Q'):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, col), (row - 1, col - 1), self.board, isEnpassantMove=True))
            if col + 1 <= 7:
                if self.board[row  - 1][col + 1][0] == "b":
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((row, col), (row - 1, col + 1), self.board))
                elif (row - 1, col + 1) == self.enpassant:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < col:
                            insideRange = range(kingCol + 1, col)
                            outsideRange = range(col + 2, 8)
                        else:
                            insideRange = range(kingCol - 1, col + 1, -1)
                            outsideRange = range(col - 1, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == 'b' and (square[1] == 'R' or square[1] == 'Q'):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, col), (row - 1, col + 1), self.board, isEnpassantMove=True))
        else:
            if self.board[row + 1][col] == "--":
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((row, col), (row + 1, col), self.board))
                    if row == 1:
                        if self.board[3][col] == "--":
                            moves.append(Move((row, col), (3, col), self.board))
            if col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == "w":
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((row, col), (row + 1, col - 1), self.board))
                elif (row + 1, col - 1) == self.enpassant:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < col:
                            insideRange = range(kingCol + 1, col - 1)
                            outsideRange = range(col + 1, 8)
                        else:
                            insideRange = range(kingCol - 1, col, -1)
                            outsideRange = range(col - 2, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == 'w' and (square[1] == 'R' or square[1] == 'Q'):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, col), (row + 1, col - 1), self.board, isEnpassantMove=True))

            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == "w":
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((row, col), (row + 1, col + 1), self.board))
                elif (row + 1, col + 1) == self.enpassant:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < col:
                            insideRange = range(kingCol + 1, col)
                            outsideRange = range(col + 2, 8)
                        else:
                            insideRange = range(kingCol - 1, col + 1, -1)
                            outsideRange = range(col - 1, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == 'w' and (square[1] == 'R' or square[1] == 'Q'):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, col), (row + 1, col + 1), self.board, isEnpassantMove=True))

    def RookMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        straightDirections = ((-1, 0), (1, 0), (0, -1), (0, 1))
        enemyColor = 'b' if self.whiteTurn else 'w'
        for d in straightDirections:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if (0 <= endRow < 8) and (0 <= endCol < 8):
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def KnightMoves(self, row, col, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightDirections = ((-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1))
        allyColor = 'w' if self.whiteTurn else 'b'
        for d in knightDirections:
            endRow = row + d[0]
            endCol = col + d[1]
            if (0 <= endRow < 8) and (0 <= endCol < 8):
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((row, col), (endRow, endCol), self.board))

    def BishopMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        diagonalDirections = ((-1, -1), (1, 1), (1, -1), (-1, 1))
        enemyColor = 'b' if self.whiteTurn else 'w'
        for d in diagonalDirections:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if (0 <= endRow < 8) and (0 <= endCol < 8):
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def QueenMoves(self, row, col, moves):
        tempPieces = ["R", "B"]
        for char in tempPieces:
            self.piecesMove[char](row, col, moves)

    def KingMoves(self, row, col, moves):
        kingDirections = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (1, -1), (-1, 1))
        allyColor = 'w' if self.whiteTurn else 'b'
        for i in range(8):
            endRow = row + kingDirections[i][0]
            endCol = col + kingDirections[i][1]
            if (0 <= endRow < 8) and (0 <= endCol < 8):
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    # place king on the end of square to check
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    # place king back
                    if allyColor == 'w':
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)
        self.getCastleMoves(row, col, moves, allyColor)

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteTurn:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        directions = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, 1), (1, -1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePins = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePins == ():
                            possiblePins = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        pieceType = endPiece[1]
                        if (0 <= j <= 3 and pieceType == 'R') or \
                                (4 <= j <= 7 and pieceType == 'B') or \
                                (i == 1 and pieceType == 'p' and ((enemyColor == 'b' and 4 <= j <= 5) or (enemyColor == 'w' and 6 <= j <= 7))) or \
                                (pieceType == 'Q') or (i == 1 and pieceType == 'K'):
                            if possiblePins == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePins)
                                break
                        else:
                            break
                else:
                    break

        knightDirections = ((-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1))
        for m in knightDirections:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if (endPiece[0] == enemyColor) and (endPiece[1] == 'N'):
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
                    break

        return inCheck, pins, checks

    def getCastleMoves(self, row, col, moves, allyColor=""):
        if self.inCheck:
            return  #can't castle while be checked
        if (self.whiteTurn and self.currentCastleRight.wK) or (not self.whiteTurn and self.currentCastleRight.bK):
            self.getKingsideCastleMove(row, col, moves, allyColor)
        if (self.whiteTurn and self.currentCastleRight.wQ) or (not self.whiteTurn and self.currentCastleRight.bQ):
            self.getQueensideCastleMove(row, col, moves, allyColor)

    def getKingsideCastleMove(self, row, col, moves, allyColor=""):
        if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--":
            if allyColor == 'w':
                self.whiteKingLocation = (row, col + 1)
            else:
                self.blackKingLocation = (row, col + 1)
            inCheck1, pins, checks = self.checkForPinsAndChecks()
            if allyColor == 'w':
                self.whiteKingLocation = (row, col + 2)
            else:
                self.blackKingLocation = (row, col + 2)
            inCheck2, pins, checks = self.checkForPinsAndChecks()
            if allyColor == 'w':
                self.whiteKingLocation = (row, col)
            else:
                self.blackKingLocation = (row, col)

            if not inCheck1 and not inCheck2:
                moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove=True))

    def getQueensideCastleMove(self, row, col, moves, allyColor=""):
        if self.board[row][col - 1] == "--" and self.board[row][col - 2] == "--" and self.board[row][col - 3] == "--":
            if allyColor == 'w':
                self.whiteKingLocation = (row, col - 1)
            else:
                self.blackKingLocation = (row, col - 1)
            inCheck1, pins, checks = self.checkForPinsAndChecks()
            if allyColor == 'w':
                self.whiteKingLocation = (row, col - 2)
            else:
                self.blackKingLocation = (row, col - 2)
            inCheck2, pins, checks = self.checkForPinsAndChecks()
            # if allyColor == 'w':
            #     self.whiteKingLocation = (row, col - 3)
            # else:
            #     self.blackKingLocation = (row, col - 3)
            # inCheck3, pins, checks = self.checkForPinsAndChecks()
            if allyColor == 'w':
                self.whiteKingLocation = (row, col)
            else:
                self.blackKingLocation = (row, col)

            if not inCheck1 and not inCheck2:
                moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove=True))
    
    def evaluate(self):
        score = 0
        b_pawns = [0,0,0,0,0,0,0,0]
        w_pawns = [0,0,0,0,0,0,0,0]  
        development = 0
        space = 0
        b_safety = 0
        w_safety = 0
        b_queen_alive = False
        w_queen_alive = False
        for row, row_list in enumerate(self.board):  
            for col, piece in enumerate(row_list):
                # piece evaluation
                score += self.pieceValue[piece]

                # count queens alive:
                if piece == "wQ":
                    w_queen_alive = True
                if piece == "bQ":
                    b_queen_alive = True

                if piece == "wp":
                    space += (7-row)
                    w_pawns[col] += 1
                    # centre
                    if row in range(2,6) and col in range(3,5):
                        score += 0.2
                    # pawn structure                      
                    if self.board[max(0, row-1)][max(0,col-1)] == "wp" or self.board[max(0,row-1)][min(7, col+1)] == "wp":
                        score += 0.05

                    

                            
                elif piece == "bp":
                    space -= row
                    b_pawns[col] += 1
                    # centre
                    if row in range(2,6) and col in range(3,5):
                        score -= 0.2
                    # pawn structure    
                    if self.board[min(7, row+1)][max(0,col-1)] == "wp" or self.board[min(7,row+1)][min(7,col+1)] == "wp":
                        score -= 0.05
                else:
                    #development
                    if piece[1] != 'K' or piece[1] != 'R':
                        if piece[0] == "w" and row < 6:
                            development += 0.15
                        elif piece[0] == "b" and row > 1:
                            development -= 0.15

                        # Prevent early queen moves
                        if piece[0] == "Q" and len(self.moveLog) < 10:
                            development -= 0.15
                        elif piece[0] == "Q" and len(self.moveLog) < 10:
                            development += 0.15

                    elif piece[1] == "R":
                        if piece[0] == "w" and col in range(3,7):
                            development += 0.15
                        elif piece[0] == "b" and col in range(3,7):
                            development -= 0.15
                    elif piece[1] == "K":
                        if piece[0] == "w" and col in (0,1,2,6,7):
                            w_safety += 0.4

                            # King safety
                            castling_side_list = [(0,1,2), (5,6,7)]
                            # king_pawns[a,b], where a is one square away from king, b is two squares away 
                            for castling_side in castling_side_list:
                                king_pawns = [0,0]
                                if col in castling_side:
                                    for i in col:
                                        if self.board[i][6] == "wp":
                                            king_pawns[0] += 1
                                        if self.board[i][5] == "wp":
                                            king_pawns[1] += 1
                                
                                # evaluate safety
                                if king_pawns[0] < 2:
                                    if king_pawns[0] == 0:
                                        w_safety -= 0.5
                                    elif king_pawns[1] == 2:
                                        w_safety -= 0.05
                                    elif king_pawns[1] == 1:
                                        w_safety -= 0.1
                                    elif king_pawns[1] == 0:
                                        w_safety -= 0.3                     

                        elif piece[0] == "b" and col in (0,1,2,6,7):
                            b_safety += 0.4

                            # King safety
                            castling_side_list = [(0,1,2), (5,6,7)]
                            # king_pawns[a,b], where a is one square away from king, b is two squares away 
                            for castling_side in castling_side_list:
                                king_pawns = [0,0]
                                if col in castling_side:
                                    for i in col:
                                        if self.board[i][1] == "wp":
                                            king_pawns[0] += 1
                                        if self.board[i][2] == "wp":
                                            king_pawns[1] += 1
                                
                                # evaluate safety
                                if king_pawns[0] < 2:
                                    if king_pawns[0] == 0:
                                        b_safety -= 0.5
                                    elif king_pawns[1] == 2:
                                        b_safety -= 0.05
                                    elif king_pawns[1] == 1:
                                        b_safety -= 0.1
                                    elif king_pawns[1] == 0:
                                        b_safety -= 0.3    
                    
                    # Knight on edge case
                    if piece[1] == 'N':
                        if piece[0] == "w" and col in (0,7):
                            development -= 0.05
                        elif piece[0] == "b" and col in (0,7):
                            development += 0.05

        # Check doubled pawns
        for stacked_pawns in w_pawns:
            score -= max(0, stacked_pawns - 1) * 0.5
        for stacked_pawns in b_pawns:
            score += max(0, stacked_pawns - 1) * 0.5

        # Check passed pawns:
        for i in range(8):
            if w_pawns[i] > 0 and b_pawns[max(i-1, 0)] == 0 and b_pawns[max(i, 0)] == 0 and b_pawns[min(i+1, 7)] == 0:
                score += 0.3
            if b_pawns[i] > 0 and w_pawns[max(i-1, 0)] == 0 and w_pawns[max(i, 0)] == 0 and w_pawns[min(i+1, 7)] == 0:
                score -= 0.3

        # Add developement and space
        score += (development + 0.05 * space)

        # Add king safety
        if b_queen_alive:
            score += w_safety
        if w_queen_alive:
            score += b_safety
        return score

class Move():
    # row start from 1->8 (bottom left to top left)
    rankToRow = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowToRank = {v: k for k, v in rankToRow.items()}

    # col start from a->h (bottom left to bottom right)
    alphaToCol = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colToAlpha = {v: k for k, v in alphaToCol.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False, promotedPiece = ''):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        self.isCastleMove = isCastleMove
        self.promotedPiece = promotedPiece
        self.isCapture = (self.pieceCaptured != "--")
        self.moveId = self.startCol * 1000 + self.startRow * 100 + self.endCol * 10 + self.endRow

    # override function
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveId == other.moveId
        return False

    # printing to console the move from xx to yy
    def getChessNotation(self):
        return self.getFileRank(self.startRow, self.startCol) + self.getFileRank(self.endRow, self.endCol)

    def getFileRank(self, row, col):
        return str(self.colToAlpha[col] + self.rowToRank[row])

    # override function
    def __str__(self):
        # castleMove:
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"
        endSquare = self.getFileRank(self.endRow, self.endCol)
        # pawn move
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colToAlpha[self.startCol] + "x" + endSquare
            else:
                return endSquare

        # piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare

class castleRight():
    def __init__(self, wK, wQ, bK, bQ):
        self.wK = wK
        self.bK = bK
        self.wQ = wQ
        self.bQ = bQ