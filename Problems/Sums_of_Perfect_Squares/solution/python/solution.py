import math
def sum_of_squares(n):
    tot = []
    raw = math.sqrt(n)
    for x in range(int(raw)-1):
        m = n
        l = raw - float(x)
        cn = 1
        while (math.ceil(l) == l) != True:
            m = m - (int(l)**2)
            l = math.sqrt(m)
            cn += 1
        tot.append(cn)
    return min(tot)