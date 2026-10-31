import math
def add_new_batch(num_array:list[int], loaded:int, l_sum:int|None, l_exp:int|None) -> int:

    if l_exp:
        mult = loaded*l_exp
        num_array += list(range(loaded+1,mult+1))
        loaded =mult
    elif l_sum:
        add = loaded+l_sum
        num_array += list(range(loaded+1,add+1))
        loaded=add
        
    return loaded

def remove_value_step(num_array:list[int],step:int,start_index:int,caught_up=False):
    if start_index >= len(num_array):
        return

    array_index = start_index
    array_value = num_array[array_index]
    step_value = (array_value//step * step) if not caught_up else step
    while array_index < len(num_array):
        array_value = num_array[array_index]
        if array_value == step_value:
            num_array.pop(array_index)
            step_value+=step
        elif array_value > step_value:
            step_value+=step
        else:
            array_index+=1
            
def delete_until_loaded(num_array:list[int],before_is_prime:int, loaded:int) -> int:
    sindex = 0
    inc_after_catchup = 0
    last_prime = num_array[before_is_prime]
    stepping = num_array[sindex]
    stop_at = math.sqrt(loaded)+1
    while stepping <= stop_at:
        stepping = num_array[sindex]
        if stepping < last_prime:
            caught_up = False
            remove_value_step(num_array,stepping,before_is_prime+1, caught_up)
        else:
            caught_up = True
            remove_value_step(num_array,stepping,before_is_prime+inc_after_catchup+1, caught_up)
            inc_after_catchup+=1
        sindex+=1
    return len(num_array)-1


def primes_until_n(n:int,load_start:int|None = 1000,load_exponent:int|None = None) -> list[int]:
    if n < load_start:
        load_start = n
    elif load_exponent and load_exponent <= 1:
        raise ValueError("load_exponent must be greater than 1")
    
    loaded: int = load_start
    before_is_prime: int = 0
    num_array: list[int] = list(range(2,load_start+1))
    while loaded <= n:
        before_is_prime=delete_until_loaded(num_array,before_is_prime,loaded)
        if loaded==n:
            break
        
        add = load_start
        exp = load_exponent
        if load_exponent == None and n<loaded+load_start:
            add = n-loaded
        elif load_exponent and loaded*load_exponent>n:
            exp=None
            add=n-loaded

        loaded = add_new_batch(num_array,loaded,add,exp)

    return num_array



    







