calc = {
    (1,1) : 1
}

def value(i,j):
    if i > j or i< 0 or j<0:
        return 0
    if (i,j) in calc:
        return calc[(i,j)]
    else:
        val = value(i-1,j) + value(i, j-1)
        calc[(i,j)] = val
        return val

def solve(n):
    return sum([value(i,n) for i in range(1,n+1)]) 