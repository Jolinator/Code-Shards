def rgb_to_hex(n):
    if n < 0:
        n = 0
    if n > 255:
        n = 255
    b16 = [str(x) for x in (range(0,10))] + ['A','B','C','D','E','F']
    resp = ''
    while n > 15:
        subdiv = n // 16
        resp += b16[subdiv]
        n = n % 16
    resp += b16[n]
    if len(resp) == 1:
        resp = '0' + resp
    return resp

def rgb(*args):
    resp = ''
    for n in args:
        resp += rgb_to_hex(n)
    return resp