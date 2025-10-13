#!/usr/bin/python3 -B

import os

# style is "twee" or "kbc"
STYLE = "kbc"

def tokenize(s):
    l = s.replace("\t", " ").replace("(", " ( ").replace(")", " ) ").strip().split(" ")
    l = [x for x in l if x]
    return l

if STYLE == "kbc":
    const = lambda x: x.upper()
    var = lambda x: x.lower()
elif STYLE == "twee":
    const = lambda x: x.lower()
    var = lambda x: x.upper()
else:
    raise "oh no"

def reformat_atom(a):
    if a.startswith("?"): return var(a[1:].upper())
    elif a.isnumeric(): return const("num" + a)
    elif a == "-" and a[1:].isnumeric(): return const("numneg" + a)
    elif a == "<": return const("lt")
    elif a == "<=": return const("le")
    elif a == ">": return const("gt")
    elif a == ">=": return const("ge")
    elif a == "&&": return const("and")
    elif a == "-": return const("minus")
    elif a == "%": return const("mod")
    elif a == "*": return const("mul")
    elif a == "+": return const("plus")
    elif a == "||": return const("or")
    elif a == "==": return const("eq")
    elif a == "/": return const("div")
    elif a == "!=": return const("ne")
    elif a == "!": return const("not")
    else: return const(a)

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

def mk_rules():
    def rule_lines():
        folder_path = "/home/ml47/caviar/src/rules"
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        yield line.strip()

    outstr = ""
    for line in rule_lines():
        line = line.split("//")[0]
        if "rw!(" not in line: continue

        # so far we ignore side-conditions
        if "if" in line: continue

        elems = line.split("\"")
        name = elems[1].replace("-", "_").lower()
        lhs, [] = reformat_term(tokenize(elems[3]))
        rhs, [] = reformat_term(tokenize(elems[5]))
        if STYLE == "twee":
            outstr += "cnf(" + name + ",axiom," + lhs + " = " + rhs + ").\n"
        elif STYLE == "kbc":
            outstr += lhs + " = " + rhs + "\n"
        else:
            raise "oh no"
    return outstr

def eval_terms():
    file = "/home/ml47/caviar/data/prefix/evaluation.csv"
    for line in open(file, "r", encoding="utf-8").readlines()[1:]:
        [num, term, hal, i] = line.split(",")
        t, [] = reformat_term(tokenize(term))
        yield t, hal

def gen_data():
    for (i, (t, hal)) in enumerate(eval_terms()):
        i = i+1
        open(f"data/{i}_{hal}.txt", "w").write(t)
