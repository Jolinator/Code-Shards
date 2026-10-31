**Task**

Imagine a lively dice game where four friends, affectionately known as `p1, p2, p3, and p4`, come together for an exciting gaming session. Here's how it unfolds: in each round, all players roll a pair of standard six-sided dice.

The player with the lowest total score is promptly eliminated from the game. But what if two or more players happen to share this dubious honor of the lowest score? In such cases, we introduce a tiebreaker: the player among them with the lowest score from their first dice roll gets the boot.

If, despite these measures, we still have players with identical rolls in the exact same order, **all players** should go for another round of rolls. This electrifying process of elimination keeps going until only one player emerges victorious as the undisputed winner.

Given a list of `scores`, documented meticulously in the order of each player's participation in every round, determine and declare the name of the triumphant player who stands as the last one standing.

**Example**

```python
([(6, 2), (4, 3), (3, 4), (5, 4), (3, 5), (1, 5), (4, 3), (1, 5), (1, 5), (5, 6), (2, 2)]) ➞ "p1"

             p1      p2      p3      p4
Round 1 -> (6, 2), (4, 3), (3, 4), (5, 4)  Player 3 removed.
Round 2 -> (3, 5), (1, 5),         (4, 3)  Player 2 removed.
Round 3 -> (1, 5),                 (1, 5)  No lowest score; players roll again.
Round 4 -> (5, 6),                 (2, 2)  Player 1 wins!
```

This thrilling game continues until one player emerges as the ultimate champion!

- 4 <= len(scores)