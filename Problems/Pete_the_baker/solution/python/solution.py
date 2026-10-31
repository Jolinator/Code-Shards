def cakes(recipe, available):
    l = []
    for x in recipe:
        if x not in available: return False
        l.append(int(available[x]/recipe[x]))
    return min(l)