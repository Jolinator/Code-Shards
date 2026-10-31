def tri(scales,t):
    w = scales.get_weight(t[0],t[1]) 
    return t[0] if w == -1 or len(t)==1 else t[1] if w != 0 else t[2]

def split(l):
    t = len(l) // 3+1 if len(l)%3!=0 else len(l) // 3
    return [l[:t],l[t:2*t],l[2*t:]]

def find_ball(scales, ball_count):
    fl = [x for x in range(ball_count)]
    while len(fl) != 1:
        fl = tri(scales,split(fl))
    return fl[0]