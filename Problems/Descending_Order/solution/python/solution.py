def descending_order(num):
    return int(''.join([sorted(str(num))[(-int(x) - 1)] for x in range(len(str(num)))]))