def path_go_up(p):
    k = ""
    for i in range(len(p)-1, -1, -1):
        if p[i] == "/":
            k += p[i]
            break
        k += p[i]

    if len(k) == len(p):
        res = ""
    else:
        res = p[:-(len(k))]
    if len(p) == 3:
        res = ""
    if len(res) == 2:
        res += "/"
    return (res)


print(path_go_up("E:/dsa/dsadasdasd"))
