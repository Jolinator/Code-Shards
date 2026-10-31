def determinant(matrix):
    if len(matrix)==1:
        return matrix[0][0]
    elif len(matrix)==2:
        return matrix[0][0]*matrix[1][1] - matrix[1][0]*matrix[0][1]
    else:
        sub_m = []
        for z in range(len(matrix[0])):
            sub_m.append([])
            for y in range(1,len(matrix)):
                sub_m[z].append([])
                for x in range(len(matrix[y])):
                    if x != z:
                        sub_m[z][y-1].append(matrix[y][x]) 
        sig = False
        total = 0
        for x in range(len(sub_m)):         
            if matrix[0][x] != 0:
                total = total + (matrix[0][x] * determinant(sub_m[x])) if sig == False else total - (matrix[0][x] * determinant(sub_m[x]))
                sig = not sig     
            else:
                sig = not sig                     
                continue

        return total