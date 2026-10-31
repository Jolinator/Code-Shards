def pig_it(text):
    final = ''
    for x in [i[1:len(text)-1] + i[0] + "ay" for i in text.split(' ')] :
        if 64 < ord(x[0]) < 123:
            final += x + ' '
        else:
            final += x[0]        
    return final.strip()