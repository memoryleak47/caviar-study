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

def reformat_atom(a):
    if a.startswith("?"): return a[1:].upper()
    elif a == "<": return "lt"
    elif a == "<=": return "le"
    elif a == ">": return "gt"
    elif a == ">=": return "ge"
    elif a == "&&": return "and"
    elif a == "-": return "minus"
    elif a == "%": return "mod"
    elif a == "*": return "mul"
    elif a == "+": return "plus"
    elif a == "||": return "or"
    elif a == "0": return "zero"
    elif a == "1": return "one"
    elif a == "2": return "two"
    elif a == "-1": return "minus_one"
    elif a == "==": return "eq"
    elif a == "/": return "div"
    elif a == "!=": return "ne"
    elif a == "!": return "not"
    else: return a

def reformat_list(l):
    return l[0] + "(" +  ", ".join(l[1:]) + ")"

def reformat_term(s):
    while len(s) > 2 and s[0] == "(" and s[2] == ")":
        s = [s[1]] + s[3:]
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
        return reformat_list(l), s
    else:
        return reformat_atom(s[0]), s[1:]
        return s[0], s[1:]

for line in lines():
    line = line.split("//")[0]
    if "rw!(" not in line: continue

    # so far we ignore side-conditions
    if "if" in line: continue

    elems = line.split("\"")
    name = elems[1].replace("-", "_").lower()
    lhs, [] = reformat_term(tokenize(elems[3]))
    rhs, [] = reformat_term(tokenize(elems[5]))
    print("cnf(" + name + ",axiom," + lhs + " = " + rhs + ").")
print("cnf(a,axiom, fff != ggg).")
