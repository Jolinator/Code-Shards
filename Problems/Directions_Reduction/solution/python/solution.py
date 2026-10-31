def opposite(d):
    if d == "NORTH":
        return "SOUTH"
    if d == "SOUTH":
        return "NORTH"
    if d == "EAST":
        return "WEST"
    if d == "WEST":
        return "EAST"

def dir_reduc(arr):
    ldir = None
    c = 0
    while c != len(arr):
        if ldir == opposite(arr[c]):
            arr.pop(c-1)
            arr.pop(c-1)
            c = 0
            ldir = None
        else:
            ldir = arr[c]
            c += 1
        
    return arr