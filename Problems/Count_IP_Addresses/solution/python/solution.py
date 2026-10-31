def ips_between(start, end):
    def arrange(l):
        arr = [int(x) for x in l.split(".")]
        return sum([arr[x]*256**(3-x) for x in range(len(arr))])
    return arrange(end) - arrange(start)