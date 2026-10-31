def make_readable(seconds):
    l = int(seconds/3600)
    d = int(seconds/60) - (l*60)
    f = seconds - (d*60) - (l*3600)
    return f"{l if len(str(l)) != 1 else f'0{l}' }:{d if len(str(d)) != 1 else f'0{d}'}:{f if len(str(f)) != 1 else f'0{f}'}"