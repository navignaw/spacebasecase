# =======================================================
# Jamboree! Alpha beta pruning! hooray
# ------------------------------------------------------
# moves: list of moves
# player: 0-3 (counterclockwise)
# edge: (move, estimate) for how well move performs
# =======================================================

WIN_VALUE = 1000000 # big number to use as infinity
SEARCH_DEPTH = 2 # number of moves to calculate
PRUNE_PERCENTAGE = 0.8 # percentage of nodes to prune for jamboree
WHOAMI = 0

# Splits a list of moves into two
def splitMoves(moves, percentage):
    i = int(len(moves) * percentage)
    return (moves[:i], moves[i:])

# Returns appropriate value of alpha or beta
def choose(player, edges):
    if player == WHOAMI: return max(edges, key=lambda e: e[1])
    return min(edges, key=lambda e: e[1])

# Recursively searches for best edge
def search(depth, state, alpha, beta, abmoves, mmmoves):
    player = getPlayer(state)
    for m in abmoves:
        result = evaluate(depth - 1, makeMove(state, m), alpha, beta, m)
        if player == WHOAMI and result[1] > alpha[1]:
            alpha = result
        elif player != WHOAMI and result[1] < beta[1]:
            beta = result
        # If child has worse results, prune it
        if beta[1] <= alpha[1]: break

    # Return appropriate value
    abedge = alpha if player == WHOAMI else beta
    edges = map(lambda m: evaluate(depth - 1, makeMove(state, m), alpha, beta, m), mmmoves)
    return choose(getPlayer(state), [abedge] + edges)

# Evaluate current state, returning best edge
def evaluate(depth, state, alpha, beta, move):
    # Return estimate if game over or depth is 0
    gameStatus = status(state)[0]
    if gameStatus == "Win" or depth == 0: return (move, estimate(state))
    if gameStatus == "Tie": return (move, 0)

    # Otherwise, search deeper
    abmoves, mmmoves = splitMoves(moves(state), PRUNE_PERCENTAGE)
    return (move, search(depth, state, alpha, beta, abmoves, mmmoves)[1])

# Returns best possible move
def nextMove(state):
    moveset = moves(state)
    ab = ((moveset[0], -WIN_VALUE*10), (moveset[0], WIN_VALUE*10))
    abmoves, mmmoves = splitMoves(moveset, PRUNE_PERCENTAGE)
    return search(SEARCH_DEPTH, state, ab[0], ab[1], abmoves, mmmoves)[0]
