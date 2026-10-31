def sum_for_list(lst):
    final = []
    sum = []
    tem = []
    for x in lst:
        n = x
        if n < 0:
            n = -n
        while n != 1:
            
            for i in range(2,n+1):
                if n % i == 0:
                    n //= i
                    tem.append(i)
                    break
        sum.append(list(set(tem)))
        tem = []
    pr = {}
    for x in range(len(sum)): 
        for i in sum[x]:
            if i not in pr.keys():
                pr[i] = lst[x]
            else:
                pr[i] += lst[x]
    
    for x in pr:
        final.append([x,pr[x]])
    
    final = sorted(final,key = lambda x: x[0] )
    return final