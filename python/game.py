##############################################################################
# game.py - Responsible for generating moves to give to client.py            #
# Moves via stdout in the form of "# # # #" (block index, # rotations, x, y) #
# Important function is find_move, which should contain the main AI          #
##############################################################################

import sys
import json

# Simple point class that supports equality, addition, and rotations
class Point:
    x = 0
    y = 0

    # Can be instantiated as either Point(x, y) or Point({'x': x, 'y': y})
    def __init__(self, x=0, y=0):
        if isinstance(x, dict):
            self.x = x['x']
            self.y = x['y']
        else:
            self.x = x
            self.y = y

    def __add__(self, point):
        return Point(self.x + point.x, self.y + point.y)

    def __eq__(self, point):
        return self.x == point.x and self.y == point.y

    # rotates 90deg counterclockwise
    def rotate(self, num_rotations):
        if num_rotations == 1: return Point(-self.y, self.x)
        if num_rotations == 2: return Point(-self.x, -self.y)
        if num_rotations == 3: return Point(self.y, -self.x)
        return self

    def distance(self, point):
        return abs(point.x - self.x) + abs(point.y - self.y)


class Game(object):
    blocks = []
    grid = []
    bonus_squares = []
    my_number = -1
    dimension = -1 # Board is assumed to be square
    turn = -1
    strategy = None

    def __init__(self, args, strategy='spatial'):
        self.strategy = strategy
        self.interpret_data(args)

    # find_move is your place to start. When it's your turn,
    # find_move will be called and you must return where to go.
    # You must return a tuple (block index, # rotations, x, y)
    def find_move(self):
        moves = self.findLegalMove()
        if not moves:
            return (0, 0, 0, 0)

        try:
            module = __import__(self.strategy)
            return module.chooseBestMove(self, moves)
        except ImportError:
            return (0, 0, 0, 0)

    def findLegalMove(self):
        moves = []
        N = self.dimension
        for index, block in enumerate(self.blocks):
            for i in xrange(0, N * N):
                x = i / N
                y = i % N

                for rotations in xrange(0, 4):
                    new_block = self.rotate_block(block, rotations)
                    if self.can_place(new_block, Point(x, y)):
                        moves.append((new_block, index, rotations, x, y))
        return moves

    def scoreOfMove(self, move):
        cBlock, _, _, x, y = move
        size = len(cBlock)
        m = 1
        # check bonus square
        for offset in cBlock:
            px = x + offset.x
            py = y + offset.y
            if [px, py] in self.bonus_squares:
                m = 3
        cScore = m * size
        return cScore

    # Checks if a block can be placed at the given point
    def can_place(self, block, point):
        onAbsCorner = False
        onRelCorner = False
        N = self.dimension - 1

        corners = [Point(0, 0), Point(N, 0), Point(N, N), Point(0, N)]
        corner = corners[self.my_number]

        for offset in block:
            p = point + offset
            x = p.x
            y = p.y
            if (x > N or x < 0 or y > N or y < 0 or self.grid[x][y] != -1 or
                (x > 0 and self.grid[x - 1][y] == self.my_number) or
                (y > 0 and self.grid[x][y - 1] == self.my_number) or
                (x < N and self.grid[x + 1][y] == self.my_number) or
                (y < N and self.grid[x][y + 1] == self.my_number)
            ): return False

            onAbsCorner = onAbsCorner or (p == corner)
            onRelCorner = onRelCorner or (
                (x > 0 and y > 0 and self.grid[x - 1][y - 1] == self.my_number) or
                (x > 0 and y < N and self.grid[x - 1][y + 1] == self.my_number) or
                (x < N and y > 0 and self.grid[x + 1][y - 1] == self.my_number) or
                (x < N and y < N and self.grid[x + 1][y + 1] == self.my_number)
            )

        if self.grid[corner.x][corner.y] < 0 and not onAbsCorner: return False
        if not onAbsCorner and not onRelCorner: return False

        return True

    # rotates block 90deg counterclockwise
    def rotate_block(self, block, num_rotations):
        return [offset.rotate(num_rotations) for offset in block]

    # updates local variables with state from the server
    def interpret_data(self, args):
        if 'error' in args:
            debug('Error: ' + args['error'])
            return

        if 'number' in args:
            self.my_number = args['number']

        if 'board' in args:
            self.dimension = args['board']['dimension']
            self.turn = args['turn']
            self.grid = args['board']['grid']
            self.blocks = args['blocks'][self.my_number]
            self.bonus_squares = args['board']['bonus_squares']

            for index, block in enumerate(self.blocks):
                self.blocks[index] = [Point(offset) for offset in block]

        if (('move' in args) and (args['move'] == 1)):
            send_command(" ".join(str(x) for x in self.find_move()))

    def is_my_turn(self):
        return self.turn == self.my_number

    def chooseBestMove1(self, moves):
        debug("woofo!")
        maxDepth = 1
        bestScore = 0
        bestMove = None
        def bestScoreFn(moves, depth=maxDepth):
            debug("woofolo!")

            if depth == 0:
                return 0
            if not moves:
                return (0, 0, 0, 0)
            bestScoreLoc = 0
            bestMoveLoc = None
            for new_block, idx, rotations, x, y in moves:
                cBlock = new_block
                cScoreLoc = self.scoreOfMove(cBlock, x, y)
                # make move
                cScoreLoc += 0 if depth==1 else bestScoreFn(self.findLegalMove(), depth-1)
                # undo move
                if bestScoreLoc < cScoreLoc:
                    bestScoreLoc = cScoreLoc
            return bestScoreLoc

        for move in moves:
            cScore = bestScoreFn([move])
            if cScore > bestScore:
                bestScore = cScore
                bestMove = move
        return bestMove[1:]

def get_state():
    return json.loads(raw_input())

def send_command(message):
    print message
    sys.stdout.flush()

def debug(message):
    send_command('DEBUG ' + str(message))

def main():
    setup = get_state()
    game = Game(setup)

    while True:
        state = get_state()
        game.interpret_data(state)

if __name__ == "__main__":
    main()
