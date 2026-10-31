def tri(scales,t):
    w = scales.get_weight([t[0]],[t[1]])
    return t[0] if w == -1 else t[1] if w != 0 else t[2]

def find_ball(scales):
    hs = scales.get_weight([0,1,2],[3,4,5])
    if hs == 0:
        return 7 if scales.get_weight([6],[7]) == 1 else 6
    if hs == 1:
        return tri(scales,[3,4,5])
    else:
        return tri(scales,[0,1,2])