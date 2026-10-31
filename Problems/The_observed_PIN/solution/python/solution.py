def get_pins(observed):
    l = {0:[8,0]}

    for x in range(1,10):
        l[x] = [x]
        if (x-1) % 3 != 0:
            l[x].append(x-1)
        if x%3 != 0:
            l[x].append(x+1)
        if x+3 < 10:
            l[x].append(x+3)
        if x-3 > 0:
            l[x].append(x-3)
    l[8].append(0)

    ob_l = [int(x) for x in observed]

    total = [str(x) for x in l[ob_l[0]]]


    for x in ob_l[1:len(ob_l)]:
        for y in range(len(total)):
            if total[y] == '':
                continue
            for z in l[x]:
                total.append(total[y] + str(z))
            total[y] = ''

    return [x for x in total if x != '']