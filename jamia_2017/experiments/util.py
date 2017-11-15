def hms(secs):
    m,s = divmod(secs, 60)
    h,m = divmod(m, 60)
    return (h,m,s)
