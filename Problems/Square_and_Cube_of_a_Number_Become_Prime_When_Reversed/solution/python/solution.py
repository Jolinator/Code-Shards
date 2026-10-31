def reverse_number(n):

    return int(str(n)[::-1])

primes= {}


As = [2, 3, 5, 7, 11, 13, 17]
#Miller-Rabin primality test
#if n < 341,550,071,728,321, it is enough to test a = 2, 3, 5, 7, 11, 13, and 17.
def prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2

    for a in As:
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def check_rev_sq_cub(itr):
        
        chk = itr*itr
        if not prime(reverse_number(chk)):
            return False
        chk = chk*itr
        return prime(reverse_number(chk))

found = {1:89}

def sq_cub_rev_prime(n):
    if found.get(n) is not None:
        return found[n]
    ret = 0
    nth = list(found.keys())[-1]
    itr = found[nth] + 1
    
    while nth < n:

        if check_rev_sq_cub(itr):
            ret = itr
            nth += 1
            found[nth] = ret

        itr += 1
    return ret