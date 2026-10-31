There are several difficulty of sudoku games, we can estimate the difficulty of a sudoku game based on how many cells are given of the 81 cells of the game.

- Easy sudoku generally have over 32 givens
- Medium sudoku have around 30–32 givens
- Hard sudoku have around 28–30 givens
- Very Hard sudoku have less than 28 givens

Note: The minimum of givens required to create a unique (with no multiple solutions) sudoku game is 17.

A hard sudoku game means that at start no cell will have a single candidates and thus require guessing and trial and error. A very hard will have several layers of multiple candidates for any empty cell.

# Task:

Write a function that solves sudoku puzzles of any difficulty.
The function will take a sudoku grid and it should return a 9x9 array with the proper answer for the puzzle.

Or it should raise an error in cases of: invalid grid (not 9x9, cell with values not in the range 1~9); multiple solutions for the same puzzle or the puzzle is unsolvable

```if:java
___Java users:___ throw an `IllegalArgumentException` for unsolvable or invalid puzzles or when a puzzle has mutliple solutions.
```