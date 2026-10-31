def perimeter(n):
	sto = 1
	sto2 = 0
	f = 0
	l =1
	for x in range(n):
		f = sto + sto2
		l += f
		sto2 = sto
		sto = f		
	return l * 4