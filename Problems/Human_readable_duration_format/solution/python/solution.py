def format_duration(sec):
    if sec == 0: return "now"
    con = [1,60,3600,86400,31536000]
    lang = ['year','day','hour','minute','second']
    st = []
    for x in range(len(con),0,-1):
        st.append((sec - sum(st)) // con[x-1] * con[x-1])
    st = [st[x] // con[len(con)-x-1] for x in range(len(con))]
    total = [f'{st[x]} {lang[x]}{"s" if st[x]>1 else ""}' for x in range(len(con)) if st[x]!= 0]
    return ", ".join(total[:-1]) + ' and ' + total[-1] if len(total) > 1 else total[0]