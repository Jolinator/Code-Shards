def check(dir,point_x,point_y,array):
    dir_c = [point_x + 1,point_y + 1,point_x - 1,point_y - 1]
    
    final = [0,0,0,0]
    for x in range(len(dir_c)):
        if dir == x + 1:
            continue
        if dir_c[x] == len(array) or dir_c[x]<0:
            final[x + 2 if x < 2 else -x-2 if x == 2 else -x] = 1

    for x in range(1,5):
        if ((x == 3 and point_x < len(array)-2 and dir != 1) or (x == 1 and point_x > 1 and dir != 3)) and array[point_y][point_x + int(2*x) - 4] == 1:
            final[x-1] = 1
        if ((x == 4 and point_y < len(array)-2 and dir != 2) or (x == 2 and point_y > 1 and dir != 4)) and array[point_y+ int(2*x) - 6][point_x] == 1:
            final[x-1] = 1
    return final


def over_l(dir):
    if dir > 4:
        return dir - 4
    else:
        return dir

def check_f(dir,point_x,point_y,array):
    dir = over_l(dir + 1)
    for x in range(1,5):
        if ((x == 3 and point_x < len(array)-3 and dir == 3) or (x == 1 and point_x > 2 and dir == 1)) and array[point_y][point_x + int(3*x) - 6] == 1:
            return True
        if ((x == 4 and point_y < len(array)-3 and dir == 4) or (x == 2 and point_y > 2 and dir == 2)) and array[point_y+ int(3*x) - 9][point_x] == 1:
            return True
    return False



def move(dir,point_x,point_y):
    if dir == 1:
        point_x -= 1
    if dir == 2:
        point_y -= 1
    if dir == 3:
        point_x += 1
    if dir == 4:
        point_y += 1
    return point_x,point_y


def spiralize(size):
    spiral = []
    point_x = 0
    point_y = 0
    dir = 3
    for x in range(size):
        spiral.append([])
        for y in range(size):
            spiral[x].append(0)
    c_list = check(dir,point_x,point_y,spiral)

    while (c_list.count(1)  != 3):
        c_list = check(dir,point_x,point_y,spiral)
        if (c_list.count(1) == 2 and check_f(dir,point_x,point_y,spiral) == True):
            spiral[point_y][point_x] = 1
            dir += 1
            point_x,point_y = move(dir,point_x,point_y)
            spiral[point_y][point_x] = 1
            break

        if c_list.count(1) == 2 and c_list[dir - 1] == 1:
            spiral[point_y][point_x] = 1
            dir = over_l(dir + 1)
        else:
            spiral[point_y][point_x] = 1
        

        point_x,point_y = move(dir,point_x,point_y)


    return spiral