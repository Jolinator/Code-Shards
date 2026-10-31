dict = {'M':1000,'D':500,'C':100,'L':50,'X':10,'V':5,'I':1,}
rev_dict = {v: k for k, v in dict.items()}
def comb_ord(ord):

    lowest = int(ord / 10)
    mid = int(ord / 2)
    ordl = [rev_dict[lowest],rev_dict[lowest]*2,rev_dict[lowest]*3,rev_dict[lowest] + rev_dict[mid],rev_dict[mid],rev_dict[mid] + rev_dict[lowest], rev_dict[mid] + rev_dict[lowest] * 2, rev_dict[mid] + rev_dict[lowest] * 3, rev_dict[lowest] + rev_dict[ord],rev_dict[ord]]
    return ordl
class RomanNumerals:
    


    



    def to_roman(val):
        t_val = val
        f_str = ''

        order = int(10 ** (len(str(t_val))))
        if order == 10000 and t_val != 1000:
            for x in range(1,4):
                if t_val - (x*1000) <= 1000:
                    f_str += 'M' * x
                    t_val = t_val - (x*1000)
                    break
        if t_val in rev_dict:
            f_str += rev_dict[t_val]
            t_val = 0
            return f_str      
        order = int(10 ** (len(str(t_val))))
        while order != 10 and t_val >= 10:
            order = int(10 ** (len(str(t_val)))) 
            ref = comb_ord(order)
            for x in range(1,len(ref) + 1):
                if t_val in rev_dict:
                    f_str += rev_dict[t_val]
                    t_val = 0
                    break
                if len(str(t_val - (x * int(order/10)))) < len(str(t_val)):
                    f_str += ref[x - 1]
                    t_val = t_val - ( x * (int(order/10)))
        if t_val != 0:
            ref = comb_ord(int(10 ** (len(str(t_val)))))
            f_str += ref[t_val - 1]            
        return f_str

    def from_roman(roman_num):
        total = 0
        skip = 0
        for x in range(len(roman_num)):
            if skip == 1:
                skip = 0
                continue
            if x != len(roman_num) - 1  and dict[roman_num[x]] < dict[roman_num[x + 1]]:
                total += (dict[roman_num[x + 1]] - dict[roman_num[x]])
                skip = 1
                continue
            total += dict[roman_num[x]]
        return total