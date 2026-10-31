import math
def populate_my_vault(dwell):
    ov = 0 if dwell == 0 else 1 if dwell <=50 else 2
    mal = dwell - ov if dwell < 3 else math.ceil(dwell/2) if ov < 2 else math.ceil(dwell/2) - 1
    wom = dwell -ov - mal
    return (ov, mal , wom)