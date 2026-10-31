from prime_sqrt import prime, naive_prime_until
from Sieve_Prime_List import primes_until_n
import timeit
class SieveListTestCase:
    def __init__(self, n, start, exp):
        self.n = n
        self.start = start
        self.exp = exp
        self.time = None
    def run_test(self):
        if not self.time:
            self.time = timeit.timeit(f"primes_until_n({self.n}, load_start={self.start}, load_exponent={self.exp})", globals=globals(), number=1)

class VsCase:
    def __init__(self, n):
        self.n = n
        self.primes = [2,3]
        self.naive_time = None
        self.list_time = None

    def run_naive(self):
        if not self.naive_time:
            self.naive_time = timeit.timeit(f"naive_prime_until({self.n}, {self.primes})", globals=globals(), number=1)

    def run_list(self):
        if not self.list_time:
            self.list_time = timeit.timeit(f"primes_until_n({self.n})", globals=globals(), number=1)

    def run_all(self):
        self.run_naive()
        self.run_list()

def find_best_params_sieve_list():
    cases: list[SieveListTestCase] = []
    n_values = [10,100,1000,10000,100000]
    start_values = [10,100,1000,10000]
    exp_values = [2,3,4,5]
    for n in n_values:
        for start in start_values:
            for exp in exp_values + [None]:
                cases.append(SieveListTestCase(n, start, exp))
    for case in cases:
        case.run_test()
    lowest_per_value = [None] * len(n_values)
    for case in cases:
        index = n_values.index(case.n)
        if lowest_per_value[index] is None or case.time < lowest_per_value[index].time:
            lowest_per_value[index] = case
        print(f"n={case.n}, start={case.start}, exp={case.exp}, time={case.time}")
    for i, lowest in enumerate(lowest_per_value):
        if lowest:
            print(f"Lowest time for n={n_values[i]}: start={lowest.start}, exp={lowest.exp}, time={lowest.time}")
        
    return cases

#Sieve list is slow because of pop() and moving indices
#A real sieve would use a byte array insted of a dynamic list
#However, it does not use any division,multiplication or modulo operations! 
#(Except in a few rarely ocurring small scale operations)
def naive_prime_vs_list_sieve():
    n_values = [10,100,1000,10000,100000,1000000,10000000]
    for n in n_values:
        case = VsCase(n)
        case.run_all()
        print(f"n={n}, naive_time={case.naive_time}, list_time={case.list_time}")

naive_prime_vs_list_sieve()