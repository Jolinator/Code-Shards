def validate_battlefield(field):
    ships = {4:0, 3:0, 2:0, 1:0}
    target = {4:1, 3:2, 2:3, 1:4}

    def surr(map,coords):

        total = 0
        x,y = coords
        if not (0<=x<10 and 0<=y<10):
            raise ValueError("NO SUCH COORDS")
        for a in range(x-1,x+2):
            for b in range(y-1,y+2):
                if (a != x or b != y) and 0<=a<10 and 0<=b<10:
                    if map[b][a] == 1:
                        total += 1
        return total

    def init_val(field):
        for y in range(10):
            for x in range(10):
                sor = surr(field,(x,y)) 
                if field[y][x] == 1:
                    if sor > 2:
                        return False
                    if sor == 2 and not ((y != 0 and y!= 9 and field[y+1][x] == 1 and field[y-1][x] == 1) or (x!=0 and x!= 9 and field[y][x+1] == 1 and field[y][x-1] == 1)):
                        return False
        return True

    def find_ship(field):
        for y in range(10):
            count = 0
            for x in range(10):
                if field[y][x]== 1:
                    y1 = y-1
                    y2 = y+1
                    if y1 >= 0: 
                        if field[y1][x] == 1:
                            continue
                    if y2  <= 9:
                        if field[y2][x] == 1:
                            continue
                    count += 1
                if field[y][x] == 0 or x == 9:
                    if count== 0:
                        continue
                    else:
                        if count > 4:
                            return False
                        ships[count] += 1
                        count = 0
                

        for x in range(10):
            count = 0
            for y in range(10):
                if field[y][x]== 1:
                    x1 = x-1
                    x2 = x+1
                    if x1 >= 0: 
                        if field[y][x1] == 1:
                            continue
                    if x2  <= 9:
                        if field[y][x2] == 1:
                            continue
                    count += 1
                if field[y][x] == 0 or y==9:
                    if count== 0:
                        continue
                    else:
                        if count > 4:
                            return False
                        ships[count] += 1
                        count = 0
        ships[1] //= 2

        return True
    
    
    if not init_val(field) or find_ship(field) == False:
        return False

    if target != ships:
        return False
    return True