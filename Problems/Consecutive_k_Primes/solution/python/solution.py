from math import sqrt
prime_memo = [2,3,5]
checked_until = 5

def is_prime_memo(n):
    sq = int(sqrt(n))
    for p in prime_memo:
        if p > sq:
            return True
        if n % p == 0:
            return False
        

def update_primes(n):
    global checked_until
    global prime_memo
    if n <= checked_until:
        return
    for i in range(checked_until+1, n+1):
        if is_prime_memo(i):
            prime_memo.append(i)
    checked_until = n

def kprime(n):
    sqr = int(sqrt(n))
    update_primes(sqr+1)
    ktimes = 0
    

    while n>1:

        for p in prime_memo:
            if n % p == 0:
                ktimes += 1
                n //= p
                break
        else:
            return ktimes+1

    return ktimes


def consec_kprimes(k,arr):
    lastk = False
    count = 0
    for n in arr:
        kn = kprime(n)
        isk = k == kn
        if isk and lastk:
            count += 1
        lastk = isk
    return count