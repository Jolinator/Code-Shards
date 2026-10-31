def round(scores,players):
    
    scot = [sum(x) for x in scores]
    dupes = []
    if len(scot) != len(set(scot)):
        for x in range(len(scot)):
            if scot.count(scot[x]) > 1 and min(scot) == scot[x]:
                dupes.append([scores[x][0],x])
                
    
    if dupes == []:
        players.pop(scot.index(min(scot)))
        return players
    dupes = sorted(dupes, key = lambda x: x[0])
    if dupes[0][0] == dupes[1][0]:
        return players
    else:
        players.pop(dupes[0][1])
        return players

def dice_game(scores):
    players = ['p1','p2','p3','p4']
    buffer = 0
    while len(players) != 1:
        k = len(players)
        players = round(scores[buffer:buffer+k],players)
        buffer +=  k
        
    return players[0]