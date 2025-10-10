#!/usr/bin/python3 -B

import os

def lines():
    folder_path = "/home/ml47/caviar/src/rules"
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    yield line.strip()

def tokenize(s):
    l = s.replace("\t", " ").replace("(", " ( ").replace(")", " ) ").strip().split(" ")
    l = [x for x in l if x]
    return l

def reformat_term(s):
    if s[0] == "(":
        s = s[1:]
        l = []
        while True:
            if s[0] == ")":
                s = s[1:]
                break
            else:
                t, s = reformat_term(s)
                l.append(t)
        return l, s
    else:
        return s[0], s[1:]

for line in lines():
    if "rw!(" not in line: continue

    # so far we ignore side-conditions
    if "if" in line: continue

    elems = line.split("\"")
    lhs, [] = reformat_term(tokenize(elems[3]))
    rhs, [] = reformat_term(tokenize(elems[5]))
    print(str(lhs) + " ====> " + str(rhs))
