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
    
# rotates block 90deg counterclockwise
def rotate_block(self, block, num_rotations):
    return [offset.rotate(num_rotations) for offset in block]

class GameState (object):
    grid = []
    blocks = [[], [], [], []]
    player = -1
    dimension = -1
    turn = -1
    bonus_squares = []

    def __init__(self, grid, dim, blocks, t, p):
        self.grid = grid
        self.dimension = dim
        self.blocks = blocks
        self.turn = t
        self.player = p

    def inc_player(self):
        self.player = (self.player + 1) % 4

    def dec_player(self):
        self.player = (self.player - 1) % 4

    # Return a list of all valid moves from this board state
    # Might optimize to get rid of useless moves (ones that don't look very useful)
    def valid_moves(self):
        moves = []
        N = self.dimension
        for index, block in enumerate(self.blocks[self.player]):
            for i in range(0, N * N):
                x = i / N
                y = i % N
                for rotations in range(0, 4):
                    new_block = rotate_block(block, rotations)
                    if self.can_place(new_block, Point(x, y)):
                        moves.append(index, rotations, x, y)
        return moves

    # Checks if a block can be placed at the given point
    def can_place(self, block, point):
        onAbsCorner = False
        onRelCorner = False
        N = self.dimension - 1

        corners = [Point(0, 0), Point(N, 0), Point(N, N), Point(0, N)]
        corner = corners[self.player]

        for offset in block:
            p = point + offset
            x = p.x
            y = p.y
            if (x > N or x < 0 or y > N or y < 0 or self.grid[x][y] != -1 or
                (x > 0 and self.grid[x - 1][y] == self.player) or
                (y > 0 and self.grid[x][y - 1] == self.player) or
                (x < N and self.grid[x + 1][y] == self.player) or
                (y < N and self.grid[x][y + 1] == self.player)
            ): return False

            onAbsCorner = onAbsCorner or (p == corner)
            onRelCorner = onRelCorner or (
                (x > 0 and y > 0 and self.grid[x - 1][y - 1] == self.player) or
                (x > 0 and y < N and self.grid[x - 1][y + 1] == self.player) or
                (x < N and y > 0 and self.grid[x + 1][y - 1] == self.player) or
                (x < N and y < N and self.grid[x + 1][y + 1] == self.player)
            )

        if self.grid[corner.x][corner.y] < 0 and not onAbsCorner: return False
        if not onAbsCorner and not onRelCorner: return False

        return True


    def apply_move(self, move, player):
        locs = rotate_block(self.blocks[player][move[0]], move[1])
        center = Point(move[2], move[3])
        for offset in locs:
            p = center + offset
            self.state[p.x][p.y] = player
        self.turn += 1
        return self.blocks[player].pop(move[0])
    
    def undo_move(self, move, player, block):
        self.apply_move(state, move, -1)
        self.blocks[player].insert(move[0], block)
        self.turn -= 1

    # The move that got you to current state
    def estimate(move):
        return 0

class Game (object):
   """ all_blocks = []
    blocks = []
    grid = []
    bonus_squares = []
    my_number = -1
    dimension = -1 # Board is assumed to be square
    turn = -1
    max_depth = 1
"""

    state = None
    my_number = -1
    turn = -1

    def __init__(self, args):
        self.interpret_data(args)
        
    def next_player(self, player):
        return (player + 1)  % 4

    # find_move is your place to start. When it's your turn,
    # find_move will be called and you must return where to go.
    # You must return a tuple (block index, # rotations, x, y)
    def find_moves(self):
        moves = self.get_valid_moves()
        best_move, best_score = self.search(self.grid, moves, self.max_depth, self.my_number)
        return best_move

    def search(self, state, moves, depth):
        best_seen = 0
        best_move = (0,0,0,0)
        for move in moves:
            block_played = state.apply_move(move, state.player)
            state.inc_player()
            board_val = self.evaluate3(state, move, depth)
            if board_val > best_seen:
                best_seen = board_val
                best_move = move
            state.dec_player()
            state.undo_move(move, state.player, block_played)
            state.dec_player()

        return best_seen, best_move

    def evaluate3(self, state, move, depth):
        if not depth:
            return state.estimate(move)
        blocks_played = []
        moves_played = []
        enemy_scores = []
        for i in xrange(3):
            currently_playing = state.player
            his_score, his_move = self.search(state, state.valid_moves(), depth - 1)
            blocks_played.append(state.apply_move(his_move, currently_playing))
            moves_played.append(his_move)
            enemy_scores.append(his_score)
            state.inc_player()

        # Could do some magic here about the his_score list

        my_score, my_move = self.search(state, state.valid_moves(), depth - 1)
        for i in xrange(3):
            state.dec_player()
            state.undo_move(moves_played[2 - i], state.player, blocks_played[2 - i])
        return my_score

    # updates local variables with state from the server
    def interpret_data(self, args):
        if (('move' not in args) or (args['move'] != 1)):
            return
            
        if 'error' in args:
            debug('Error: ' + args['error'])
            return

        if 'number' in args:
            self.my_number = args['number']

        if 'board' in args:
            dimension = args['board']['dimension']
            turn = args['turn']
            grid = args['board']['grid']
            allblocks = args['blocks']
            bonus_squares = args['board']['bonus_squares']

        for blocks in allblocks:
            for index, block in enumerate(blocks):
                blocks[index] = [Point(offset) for offset in block]

        self.state = GameState(grid, dimension, allblocks, turn, bonus_squares, self.my_number)

        send_command(" ".join(str(x) for x in self.find_move()))

    def is_my_turn(self):
        return self.turn == self.my_number

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
