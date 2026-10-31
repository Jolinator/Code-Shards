def n_for_cycles(ranges,func,*args):
    #ranges is [(start1, end1, step1), (start2, end2, step2), ...]
    #first is outermoust loop
    cycle = []
    increments = []
    ends = []
    if not ranges or not func:
        raise ValueError("Ranges list and function cannot be empty")
    
    for r in ranges:
        start, end, step = r
        if not isinstance(step, int) or not isinstance(start, int) or not isinstance(end, int):
            raise ValueError("Start, end, and step must be integers")
        if step <= 0:
            raise ValueError("Step must be positive")
        if not (start < end):
            raise ValueError("Start must be less than end")
        
        cycle.append(start)
        increments.append(step)
        ends.append(end)
    
    while cycle[0] < ends[0]:
        func(*cycle, *args)
        cycle[-1] += increments[-1]
        carry_over = cycle[-1] >= ends[-1]
        carry_over_index = len(cycle) - 1
        while carry_over == True:

            cycle[carry_over_index] = ranges[carry_over_index][0]
            carry_over_index -= 1
            if carry_over_index < 0:
                return
            cycle[carry_over_index] += increments[carry_over_index]
            carry_over = cycle[carry_over_index] >= ends[carry_over_index]




    

        