def frequencies(s):
    if type(s) != str:
        return None
    if s == '':
        return ''
    f = []
    for x in list(set(s)):
        f.append((x,s.count(x)))
    return f

def binlist(freqs):
    strl = {}
    L = 0
    

    while len(freqs)>1:
        freqs = sorted(freqs, key= lambda x: (freqs[freqs.index(x)][1], freqs[freqs.index(x)][0]))
        freqs = sorted(freqs[0:2], key= lambda x:freqs[freqs.index(x)][0]) + freqs[2:len(freqs)]
        if len(freqs[0][0]) > 1 and len(freqs[1][0]) == 1:
            freqs[0:2] = [freqs[1],freqs[0]]
        elif len(freqs[0][0]) > 1 and len(freqs[1][0]) > 1:
            if ord(freqs[0][0][0]) > ord(freqs[1][0][0]):
                freqs[0:2] = [freqs[1],freqs[0]]
        for x in freqs[0][0]:
            strl[x] = '0' if (x not in strl) else '0' + strl[x] 
        for x in freqs[1][0]:
            strl[x] = '1' if (x not in strl) else '1' + strl[x]

        freqs[0:2] = [(freqs[0][0] + freqs[1][0],freqs[0][1] + freqs[1][1])]
        #print(freqs)



    
    
    return strl



def encode(freqs,s):
    if len(freqs) < 2:
        return None
    if type(s) != str or  s == '':
        return ''
    strl = binlist(freqs)
    f = ''
    for x in s:
        f += strl[x]
    return f

def decode(freqs,bits):
    if len(freqs) < 2:
        return None
    if bits == ''  or type(bits) != str:
        return ''
    strl = binlist(freqs)
    strl = {v: k for k, v in strl.items()}
    f = ''
    while bits != '':
        for x in strl.keys():
            if bits.startswith(x):
                f += strl[x]
                bits = bits[len(x):len(bits)]
    return f