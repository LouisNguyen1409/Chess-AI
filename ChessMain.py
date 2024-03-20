# Handle user input and display current GameState object
import math
import pygame as p
import ChessEngine
import ChessAI as ai

# CONSTANT
WIDTH = HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 290
MOVE_LOG_PANEL_HEIGHT = HEIGHT
# dimensions of a chess board are 8x8
DIMENSION = 8
# 512/8 = 64, each square is 64 pixels
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 240
IMAGES = {}

def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():
    # setup screen
    p.init()
    screen = p.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    gameOver = False
    playerOne = True
    playerTwo = False
    load_images()
    # store user input
    # (tuple: (row, col))
    sqSelected = ()
    # [original, destination]
    playerClicks = []

    running = True
    while running:
        humanTurn = (gs.whiteTurn and playerOne) or (not gs.whiteTurn and playerTwo)
        # handle event
        for e in p.event.get():
            # press cross
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    # (x,y) coordinate
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    # select same square -> unselected, reset
                    if sqSelected == (row, col) or col >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else: # select diff square
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    # make move when have 2 diff square
                    print(playerClicks)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        # for i in range(len(validMoves)):
                        #     # make move if valid
                        if move in validMoves:
                            move = validMoves[validMoves.index(move)]
                            gs.makeMove(move, humanTurn)
                            moveMade = True
                            animate = True
                            sqSelected = ()
                            playerClicks = []
                            print(move.getChessNotation())
                        else:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when pressed z
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    playerOne = True
                    playerTwo = True
                elif e.key == p.K_r: # reset game when pressed r
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    moveMade = False
                    animate = False
                    gameOver = False
                    playerOne = True
                    playerTwo = True
                    sqSelected = ()
                    playerClicks = []
                elif e.key == p.K_q: # switch player when pressed q
                    playerOne = False
                    playerTwo = True
                elif e.key == p.K_e: # switch player when pressed e
                    playerOne = True
                    playerTwo = False
                elif e.key == p.K_f:
                    if gs.whiteTurn:
                        playerOne = False
                    else:
                        playerTwo = False

        ''' AI move finder '''
        if not humanTurn:
            white = 1
            if (not gs.whiteTurn):
                white = -1
                
            depth = 2
            move = ai.minimax(gs, 2 * depth, white)
            if not (move == None):                   
                moveMade = True
                animate = True
                gs.makeMove(move, not humanTurn)

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False


        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate or gs.staleMate:
            gameOver = True
            if gs.staleMate:
                gameOver = True
                drawEndGameText(screen, "DRAW")
            else:
                if gs.whiteTurn:
                    drawEndGameText(screen, "BLACK WIN")
                else:
                    drawEndGameText(screen, "WHITE WIN")


        clock.tick(MAX_FPS)
        p.display.flip()

def highlightMove(screen, gs, validMoves, sqSelected):
    sq = p.Surface((SQ_SIZE, SQ_SIZE))
    sq.set_alpha(100)
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteTurn else 'b'): # sqSelected is a piece that can be moved
            # highlight selected square
            sq.fill(p.Color("blue"))
            screen.blit(sq, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight validmoves
            sq.fill(p.Color("cyan"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(sq, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

    if gs.inCheck:
        if gs.whiteTurn:
            sq.fill(p.Color("red"))
            screen.blit(sq, (gs.whiteKingLocation[1] * SQ_SIZE, gs.whiteKingLocation[0] * SQ_SIZE))
        else:
            sq.fill(p.Color("red"))
            screen.blit(sq, (gs.blackKingLocation[1] * SQ_SIZE, gs.blackKingLocation[0] * SQ_SIZE))

    if len(gs.moveLog) != 0:
        sq.fill(p.Color("yellow"))
        screen.blit(sq, (gs.moveLog[-1].startCol * SQ_SIZE, gs.moveLog[-1].startRow * SQ_SIZE))
        screen.blit(sq, (gs.moveLog[-1].endCol * SQ_SIZE, gs.moveLog[-1].endRow * SQ_SIZE))

def animateMove(move, screen, board, clock):
    colors = [p.Color("white"), p.Color("grey")]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    sqDistance = math.sqrt(abs(move.endRow - move.startRow)*abs(move.endRow - move.startRow) + abs(move.endCol - move.startCol)*abs(move.endCol - move.startCol))
    sqDistance = int(sqDistance)
    framesPerSquare = 12 // sqDistance
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        row, col = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enPassantRow = (move.endRow + 1) if move.pieceCaptured[0] == 'b' else (move.endRow - 1)
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        if move.pieceMoved != "--":
            screen.blit(IMAGES[move.pieceMoved], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(144)

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightMove(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)
    drawEval(screen, gs)
    drawMoveLog(screen, gs)

def drawBoard(screen):
    colors = [p.Color("bisque2"), p.Color("darkolivegreen4")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawEndGameText(screen, text):
    font = p.font.SysFont("Verdana", 32, True, False)
    textObject = font.render(text, False, p.Color("black"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color("red"))
    screen.blit(textObject, textLocation.move(2, 2))

def drawEval(screen, gs):
    moveLogRect = p.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, 20)
    p.draw.rect(screen, p.Color("black"), moveLogRect)

    font = p.font.SysFont("Verdana", 13, True, False)

    textObject = font.render(str(gs.evaluate()), False, p.Color("white"))
    textLocation = moveLogRect.move(5, 5)
    screen.blit(textObject, textLocation)

def drawMoveLog(screen, gs):
    moveLogRect = p.Rect(WIDTH, 20, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i+1]) + "   "
        moveTexts.append(moveString)

    padding = 5
    movesPerRow = 3
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        font = p.font.SysFont("Verdana", 13, True, False)
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, False, p.Color("white"))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


if __name__ == "__main__":
    main()