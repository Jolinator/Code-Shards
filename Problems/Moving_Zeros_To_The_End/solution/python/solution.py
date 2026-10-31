def move_zeros(lst):
    copy = [x for x in lst]
    offset= 0
    for x in range(len(lst)):
        if lst[x] == 0:
            copy.pop(x - offset)
            copy.append(0)
            offset += 1
    return copy