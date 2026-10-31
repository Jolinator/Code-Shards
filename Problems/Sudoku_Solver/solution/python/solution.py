class Sudoku:
    def __init__(self, grid):
        self.grid = grid
        self.total = set(range(1, 10))
        self.possible = None
        self.possible_per_number_line = None
        self.possible_per_number_column = None
        self.possible_per_number_square = None
        self.ignore_per_number = None
    
    def get_all_possible_values_cells(self, cell):
        """
        Get all possible cells for each empty cell in the Sudoku grid.
        """

        cx = cell[0]
        cy = cell[1]
        occupied = set()
        for it in range(9):
            occupied.add(self.grid[cy][it]) # Check row
            occupied.add(self.grid[it][cx]) # Check column
        
        # Check 3x3 grid
        x0 = cx // 3
        y0 = cy // 3
        for incy in range(3):
            y = y0 * 3 + incy
            if y == cy:
                continue
            for incx in range(3):
                x = x0 * 3 + incx
                if x == cx:
                    continue
                occupied.add(self.grid[y][x])
                
                    
        return self.total - occupied



    def get_all_possible_numbers(self):
        """
        Get all possible numbers for each empty cell in the Sudoku grid.
        """

        self.possible = []
        for y in range(9):
            self.possible.append([])
            for x in range(9):
                if self.grid[y][x] == 0:
                    self.possible[y].append(self.get_all_possible_values_cells((x,y)))
                else:
                    self.possible[y].append(None)
            
        self.get_possible_per_number_slc()
        self.remove_certain_linecol_possible()
        self.merge_same_possibilities()
        self.get_possible_per_number_slc()


        
        

    def sub_all_trivial_line_square(self):
        found_one = False
        for y in range(9):
            for x in range(9):
                s = self.possible[y][x]

                if s!= None and len(s) == 1:
                    self.grid[y][x] = next(iter(s))
                    s = None
                    found_one = True
        return found_one





    def get_possible_per_number_slc(self):
        
        self.possible_per_number_line = []
        self.possible_per_number_column = []


        for y in range(9):
            temp_line = {1:set(),2:set(),3:set(),4:set(),5:set(),6:set(),7:set(),8:set(),9:set()}
            
            for x in range(9):
                s = self.possible[y][x]
                if s != None:
                    for number in s:
                        temp_line[number].add((x,y))
            self.possible_per_number_line.append(temp_line.copy())
        
        for x in range(9):
            temp_column = {1:set(),2:set(),3:set(),4:set(),5:set(),6:set(),7:set(),8:set(),9:set()}
            for y in range(9):
                s = self.possible[y][x]
                if s != None:
                    for number in s:
                        temp_column[number].add((x,y))
            self.possible_per_number_column.append(temp_column.copy())
        
        self.possible_per_number_square = []
        for ysq in range(3):
            for xsq in range(3):
                temp_square = {1:set(),2:set(),3:set(),4:set(),5:set(),6:set(),7:set(),8:set(),9:set()}
                for incy in range(3):
                    for incx in range(3):
                        x = xsq*3+incx
                        y = ysq*3+incy
                        
                        s = self.possible[y][x]
                        if s != None:
                            for number in s:
                                temp_square[number].add((x,y))
                self.possible_per_number_square.append(temp_square.copy())
        
        
        

    
    def remove_certain_linecol_possible(self):

        for sq in range(9):
            for number in range(1, 10):
                num_dic = self.possible_per_number_square[sq]
                cells = num_dic[number]
                if 1 < len(cells) < 3:
                    
                    xst = next(iter(cells))[0]
                    yst = next(iter(cells))[1]
                    xlmb = lambda x: x[0] == xst
                    ylmb = lambda y: y[1] == yst
                    if all(map(xlmb, cells)):

                        ylist = [cell[1] for cell in cells]
                        for y in range(9):
                            if y in ylist:
                                continue
                            if self.grid[y][xst] == 0:
                                self.possible[y][xst].discard(number)
                    if all(map(ylmb, cells)):

                        xlist = [cell[0] for cell in cells]
                        for x in range(9):
                            if x in xlist:
                                continue
                            if self.grid[yst][x] == 0:
                                self.possible[yst][x].discard(number)

                 

    def merge_cells(self,number,num_dic):
        cells = num_dic[number]
        if len(cells) < 2:
            return
        eq_s = set()
        for x in num_dic:
            if cells == num_dic[x]:
                eq_s.add(x)
        
        if len(eq_s) == len(cells):
            for cell in cells:
                self.possible[cell[1]][cell[0]] = eq_s

    def merge_same_possibilities(self):
        
        for c in range(9):
            for number in range(1, 10):
                
                num_dic = self.possible_per_number_square[c]
                self.merge_cells(number, num_dic)
                num_dic = self.possible_per_number_line[c]
                self.merge_cells(number, num_dic)
                num_dic = self.possible_per_number_column[c]
                self.merge_cells(number, num_dic)


           

    def sub_only_possible_square_line(self):
        """
        Check if there is only one valid spot for a given number in a 3x3 square.
        """
        #{1:set(),2:set(),3:set(),4:set(),5:set(),6:set(),7:set(),8:set(),9:set()}
        found_one = False
        
        for c in range(9):
            for number in range(1, 10):
                if len(self.possible_per_number_square[c][number]) == 1:
                    cell = next(iter(self.possible_per_number_square[c][number]))
                    self.grid[cell[1]][cell[0]] = number
                    found_one = True
                if len(self.possible_per_number_line[c][number]) == 1:
                    cell = next(iter(self.possible_per_number_line[c][number]))
                    self.grid[cell[1]][cell[0]] = number
                    found_one = True
                if len(self.possible_per_number_column[c][number]) == 1:
                    cell = next(iter(self.possible_per_number_column[c][number]))
                    self.grid[cell[1]][cell[0]] = number
                    found_one = True
        
        return found_one
                    
    #def 

    def sub_until_stale(self):
        """
        Keep applying the sub_all_trivial and sub_only_possible_square functions until no more changes can be made.
        """
        found_change = True
        while found_change:
            found_change = False
            self.get_all_possible_numbers()
            found_change = self.sub_all_trivial_line_square() or self.sub_only_possible_square_line()
            
    
    def __str__(self):
        """
        Print the Sudoku grid in a readable format.
        """
        result = ""
        for y in range(9):
            for x in range(9):
                result += str(self.grid[y][x]) + " "
            result += "\n"
        return result
    
    def __repr__(self):
        return self.__str__()


              


def sudoku(puzzle):
    """return the solved puzzle as a 2d array of 9 x 9"""
    s = Sudoku(puzzle)
    s.sub_until_stale()
    return s.grid