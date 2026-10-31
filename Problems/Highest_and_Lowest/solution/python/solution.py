def high_and_low(numbers):
    return f'{sorted([int(x) for x in numbers.split(" ")])[-1]} {sorted([int(x) for x in numbers.split(" ")])[0]}' 