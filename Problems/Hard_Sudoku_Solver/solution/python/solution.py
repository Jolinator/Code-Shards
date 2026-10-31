from itertools import combinations

class InvalidPuzzleException(Exception):
    pass

class NoSolutionException(Exception):
    pass

possible_values = frozenset(range(1, 10))

class Cell:
    def __init__(self):
        self.value : int = 0
        self.candidates : set[int] = set(range(1, 10))
        self.row: Row = None
        self.column: Column = None
        self.square: Square = None

    def substitute_candidates(self, values: set[int]):
        self.candidates = values.copy()

    def remove_candidate(self, value: int) -> bool:
        if value in self.candidates:
            self.candidates.remove(value)
            return True
        return False

    def assign_value(self, value: int):
        self.value = value
        self.candidates.clear()
        for domain in [self.row, self.column, self.square]:
            domain.remove_candidate_all_cells(value)
    
    def assign_row(self, row: 'Row'):
        self.row = row
    
    def assign_column(self, column: 'Column'):
        self.column = column
    
    def assign_square(self, square: 'Square'):
        self.square = square
    
    def is_solved(self) -> bool:
        return self.value != 0


class Domain:
    def __init__(self, cells : set[Cell]):
        self.cells : set[Cell] = cells
    
    def get_candidates(self) -> set[int]:
        candidates = set()
        for cell in self.cells:
            if not cell.is_solved():
                candidates |= cell.candidates
        return candidates

    def remove_candidate_all_cells(self, value: int):
        for cell in self.cells:
            if not cell.is_solved():
                cell.remove_candidate(value)
    
    
    def remove_naked_k(self, k: int) -> bool:
        changed = False                    

        if k == 1:
            for cell in self.cells:
                if not cell.is_solved() and len(cell.candidates) == 1:
                    value = next(iter(cell.candidates))
                    cell.assign_value(value)
                    changed = True
            return changed

        relevant_cells = [cell for cell in self.cells if len(cell.candidates) <= k and not cell.is_solved()]
        for combo in combinations(relevant_cells, k):
            union = set().union(*(cell.candidates for cell in combo))
            if len(union) == k:
                for cell in self.cells - set(combo):
                    if not cell.is_solved():
                        for value in union:
                            if cell.remove_candidate(value):
                                changed = True  
        return changed
    
    def remove_hidden_k(self, k: int) -> bool:
        changed = False

        if k == 1:
            for value in possible_values:
                cells_with_value = [cell for cell in self.cells if not cell.is_solved() and value in cell.candidates]
                if len(cells_with_value) == 1:
                    cells_with_value[0].assign_value(value)
                    changed = True
            return changed

        possible_subsets = set()

        seen_digits = self.get_candidates()

        for subset in combinations(seen_digits, k):
            possible_subsets.add(frozenset(subset))

        for subset in possible_subsets:
            subset = set(subset)
            cells_to_restrict: set[Cell] = set()
            for cell in self.cells:
                if not cell.is_solved():
                    for value in subset:
                        if value in cell.candidates:
                            cells_to_restrict.add(cell)

            if len(cells_to_restrict) == k:
                for cell in cells_to_restrict:
                    new_candidates = cell.candidates.intersection(subset)
                    if new_candidates != cell.candidates:
                        cell.substitute_candidates(new_candidates)
                        changed = True
        return changed

 


class Line(Domain):
    def __init__(self, cells: list[Cell]):
        super().__init__(set(cells))
        self.linecells = cells
    
    def check_k_1square(self, k: int) -> list[Cell] | None:
        cells = None
        square_ranges = [(0, 3), (3, 6), (6, 9)]
        for sranges in square_ranges:
            scells = [cell for cell in self.linecells[sranges[0]:sranges[1]]]
            for cell in scells:
                if k in cell.candidates:
                    if cells is not None:
                        return None
                    cells = scells
                    break  
        return cells
    
    def remove_claiming(self) -> bool:
        changed = False
        seen_digits = self.get_candidates()
        
        for digit in seen_digits:
            cells_in_square = self.check_k_1square(digit)
            if cells_in_square is not None:
                cell0 = cells_in_square[0]
                square = cell0.square
                for cell in square.cells - set(cells_in_square):
                    if not cell.is_solved() and cell.remove_candidate(digit):
                        changed = True
        return changed

    



class Row(Line):
    def __init__(self, cells: list[Cell]):
        super().__init__(cells)
        for cell in cells:
            cell.assign_row(self)
    
        
class Column(Line):
    def __init__(self, cells: list[Cell]):
        super().__init__(cells)
        for cell in cells:
            cell.assign_column(self)

class Square(Domain):
    def __init__(self, cells: list[list[Cell]]):
        super().__init__(set(cell for row in cells for cell in row))
        for cell in self.cells:
            cell.assign_square(self)
        self.gridcells = cells


    def check_k_1row(self, k: int) -> list[Cell] | None:
        cells = None
        for row in self.gridcells:
            for cell in row:
                if k in cell.candidates:
                    if cells is not None:
                        return None
                    cells = row
                    break
        return cells

    def check_k_1col(self, k: int) -> list[Cell] | None:
        cells = None
        for col in zip(*self.gridcells):
            for cell in col:
                if k in cell.candidates:
                    if cells is not None:
                        return None
                    cells = list(col)
                    break
        return cells
        
        
    def remove_pointing(self) -> bool:
        changed = False
        digits_in_square = self.get_candidates()
        for digit in digits_in_square:
            r_cells = self.check_k_1row(digit)
            if r_cells is not None:
                cell0 = r_cells[0]
                row = cell0.row
                for cell in row.cells - set(r_cells):
                    if not cell.is_solved() and cell.remove_candidate(digit):
                        changed = True
                        
            c_cells = self.check_k_1col(digit)
            if c_cells is not None:
                cell0 = c_cells[0]
                column = cell0.column
                for cell in column.cells - set(c_cells):
                    if not cell.is_solved() and cell.remove_candidate(digit):
                        changed = True
        
        return changed
        

class Sudoku:
    def validate_grid(self, input_: list[list[int]]):
        if len(input_) != 9:
            raise ValueError("Input grid must have 9 rows")
        for row in input_:
            if len(row) != 9:
                raise ValueError("Input grid must have 9 columns")
            for value in row:
                if not isinstance(value, int) or not (0 <= value <= 9):
                    raise ValueError("Grid values must be integers between 0 and 9 inclusive")

    def __init__(self, input_ : list[list[int]], validate: bool = False):
        if validate:
            self.validate_grid(input_)
        self.grid: list[list[Cell]] = []
        self.domains: set[Domain] = set()
        self.lines: set[Line] = set()
        self.rows: set[Row] = set()
        self.columns: set[Column] = set()
        self.squares: set[Square] = set()
        #Create cells
        for i in range(len(input_)):
            self.grid.append([Cell() for _ in range(len(input_[i]))])

        # Create horizontal lines
        for i in range(9):
            line = Row([self.grid[i][j] for j in range(9)])
            self.lines.add(line)
            self.domains.add(line)
            self.rows.add(line)
        # Create vertical lines
        for j in range(9):
            line = Column([self.grid[i][j] for i in range(9)])
            self.lines.add(line)
            self.domains.add(line)
            self.columns.add(line)

        # Create squares
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                cells = []
                for x in range(i, i + 3):
                    row = []
                    for y in range(j, j + 3):
                        row.append(self.grid[x][y])
                    cells.append(row)
                square = Square(cells)
                self.squares.add(square)
                self.domains.add(square)

        # Assign initial values
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if input_[i][j] != 0:
                    self.grid[i][j].assign_value(input_[i][j])
        if validate and not self.is_valid_solution():
            raise InvalidPuzzleException("Initial grid is invalid, violates Sudoku rules")

                        
    
    def is_solved(self) -> bool:
        return all(cell.is_solved() for row in self.grid for cell in row)

    def is_valid_candidate(self) -> bool:
        for row in self.grid:
            for cell in row:
                if not cell.is_solved() and len(cell.candidates) == 0:
                    return False

        return True
    
    def is_valid_solution(self) -> bool:
        if not self.is_valid_candidate():
            return False
        for domain in self.domains:
            seen_values = set()
            for cell in domain.cells:
                if cell.is_solved():
                    if cell.value in seen_values:
                        return False
                    seen_values.add(cell.value)
        return True
    
    def solve_trivial(self) -> bool:
        changed = False
        for row in self.grid:
            for cell in row:
                if cell.is_solved():
                    continue
                if len(cell.candidates) == 1:   
                    cell.assign_value(next(iter(cell.candidates)))
                    changed = True
        return changed

    def solve_naked_k(self, k: int) -> bool:
        changed = False
        for domain in self.domains:
            if domain.remove_naked_k(k):
                changed = True
        return changed

    def solve_hidden_k(self, k: int) -> bool:
        changed = False
        for domain in self.domains:
            if domain.remove_hidden_k(k):
                changed = True
        return changed

    def solve_pointing(self) -> bool:
        changed = False
        for square in self.squares:
            if square.remove_pointing():
                changed = True
        return changed
    
    def solve_claiming(self) -> bool:
        changed=False
        for line in self.lines:
            if line.remove_claiming():
                changed = True
        return changed
    
    def remove_kfish_col(self, k: int, d: int) -> bool:
        changed = False
        d_cols = set(col for col in self.columns if d in col.get_candidates())
        if len(d_cols) < k:
            return changed
        for colcombo in combinations(d_cols, k):
            rows = set()
            for col in colcombo:
                for cell in col.cells:
                    if not cell.is_solved() and d in cell.candidates:
                        rows.add(cell.row)
            if len(rows) == k: #found kfish
                for col in self.columns - set(colcombo):
                    for cell in col.cells:
                        if cell.row in rows and not cell.is_solved() and cell.remove_candidate(d):
                            changed = True
        return changed
        

    def remove_kfish_row(self, k: int, d: int) -> bool:
        changed = False
        d_rows = [row for row in self.rows if d in row.get_candidates()]
        if len(d_rows) < k:
            return changed
        for rowcombo in combinations(d_rows, k):
            cols = set()
            for row in rowcombo:
                for cell in row.cells:
                    if not cell.is_solved() and d in cell.candidates:
                        cols.add(cell.column)
            if len(cols) == k: #found kfish
                for row in self.rows - set(rowcombo):
                    for cell in row.cells:
                        if cell.column in cols and not cell.is_solved() and cell.remove_candidate(d):
                            changed = True
        return changed

    def solve_kfish(self, k: int) -> bool:
        changed = False
        for d in range(1, 10):
            if self.remove_kfish_col(k, d):
                changed = True
            if self.remove_kfish_row(k, d):
                changed = True
        return changed

    def strategy_until_change(self):
        changed = False
        changed = self.solve_naked_k(1)
        changed = changed or self.solve_hidden_k(1)
        changed = changed or self.solve_pointing()
        changed = changed or self.solve_claiming()
        for k in range(2, 4):
            changed = changed or self.solve_naked_k(k)
            changed = changed or self.solve_hidden_k(k)
        changed = changed or self.solve_kfish(2)
        changed = changed or self.solve_naked_k(4)
        for k in range(3, 5):
            changed = changed or self.solve_kfish(k)
        return changed

    def smallest_candidate_cell_index(self) -> tuple[int, int] | None:
        lowest = 10
        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                cell = self.grid[row][col]
                if not cell.is_solved() and len(cell.candidates) < lowest:
                    if len(cell.candidates) == 2:
                        return (row, col)
                    lowest = len(cell.candidates)
                    smallest = (row, col)
        return smallest


    def solve(self):
        while not self.is_solved():
            changed = False
            changed = self.strategy_until_change()
            if changed == False:
                raise NoSolutionException("No solution found with implemented strategies")
            elif not self.is_valid_candidate():
                raise InvalidPuzzleException("Puzzle is invalid, no candidates left for some cell")
            self.solve_trivial()
        
    def output(self) -> list[list[int]]:
        return [[cell.value for cell in row] for row in self.grid]
    
    def copy(self) -> 'Sudoku':
        s = Sudoku(self.output())
        for row in range(len(self.grid)):
            for cell in range(len(self.grid[row])):
                s.grid[row][cell].candidates = self.grid[row][cell].candidates.copy()
        return s
                    
    def __str__(self) :
        st = ''
        xsize = len(self.grid)
        ysize = len(self.grid[0])
        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                st += str(self.grid[x][y]) + ' '
                if (y + 1) % 3 == 0 and y != ysize - 1:
                    st += '| '
            st += '\n'
            if (x + 1) % 3 == 0 and x != xsize - 1:
                st += '-' * (xsize * 2 + (xsize // 3)) + '\n'
        return st
        

def sudoku_solver(input_) -> list[list[int]]:
    #dfs
    sols = set()
    s = Sudoku(input_, validate=True)
    stack = [s]
    while stack:
        s = stack.pop()
        try:
            s.solve()
            output = s.output()
            toutput = tuple(tuple(row) for row in output)
            sols.add(toutput)
            if len(sols) > 1:
                raise Exception("Multiple solutions found")
        except NoSolutionException:
            cell_index = s.smallest_candidate_cell_index()
            if cell_index is None:
                continue
            row, col = cell_index
            cell = s.grid[row][col]
            for candidate in cell.candidates:
                s_copy = s.copy()
                s_copy.grid[row][col].assign_value(candidate)
                stack.append(s_copy)
        except InvalidPuzzleException:
            continue
    if len(sols) == 0:
        raise Exception("No solutions found")
    return [list(row) for row in sols.pop()]