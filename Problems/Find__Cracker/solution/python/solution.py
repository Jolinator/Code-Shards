def find_hack(arr):
    hacked = []
    point = {"A":30,"B":20,"C":10,"D":5}
    for x in arr:
        total = 0
        for y in x[-1]:
            if y not in point:
                total += 0
                continue
            total+=point[y]
        if len(x[-1])>= 5 and all(p == 'A' or p=='B' for p in x[-1]):
            total += 20 if total < 180 else 200-total
        if total != x[1] or x[1] > 200:
            hacked.append(x[0])
            
    return hacked