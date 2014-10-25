def bestSpacialMove(self, moves):
    bestSpacialScore = 0
    bestMove = None
    for cBlock, idx, rotations, x, y in moves:
        farthestX = 0
        farthestY = 0
        for offset in cBlock:
            px = offset.x + x
            py = offset.y + y
            if farthestX * farthestY < px * py:
                farthestX = x
                farthestY = y
        cScore = farthestX * farthestY
        if bestSpacialScore <= cScore:
            bestSpacialScore = cScore
            bestMove = (idx, rotations, x, y)
    return bestMove


def chooseBestMove(self, moves):
    bestScore = 0
    bestMoves = []
    tolerance = 3
    scores = map(self.scoreOfMove, moves)
    maxScore = max(scores)
    for i in xrange(len(moves)):
        if scores[i] + tolerance >= maxScore:
            bestMoves.append(moves[i])
    #debug(bestMoves)
    return bestSpacialMove(self, bestMoves)
