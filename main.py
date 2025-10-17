#!/usr/bin/python3 -B

import os
import sys

# style is "twee" or "kbc"
# STYLE = "kbc"
# output_file = "rules.rule"
STYLE = "twee"
output_file = "rules.p"

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
    raise Exception("oh no")

def reformat_atom(a):
    a = a.strip()
    if a.startswith("?"): return var(a[1:].upper())
    elif a.isnumeric(): return const("num" + a)
    # elif a.isnumeric(): return const("'" + a + "'")
    elif a[0] == "-" and a[1:].isnumeric(): return const("numneg" + a[1:])
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

rf = reformat_atom

def mk_rules():
    def rule_lines():
        folder_path = "./caviar/src/rules"
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        yield line.strip()

    rules = []
    for line in rule_lines():
        line = line.split("//")[0]
        if "rw!(" not in line: 
            continue

        # so far we ignore side-conditions
        rhs_process = lambda lhs, rhs: rhs
        if "if" in line: 
            # crate::trs::compare_c0_c1("?b", "?a", "%0<")
            # crate::trs::is_not_zero("?a")
            # get test and arguments
            condition = line.split("if")[1].strip().rstrip(");")
            test = condition.split("(")[0].strip().split("::")[-1]
            args = condition.split("(")[1].strip().split(")")[0].strip().split(",")
            args = [a.strip(" \"") for a in args]
            test_func = None
            if test in ["is_const_pos", "is_const_neg", "is_not_zero"]:
                assert len(args) == 1
                test_func = f"{rf(test)}({reformat_atom(args[0])})"
            elif test == "compare_c0_c1":
                assert len(args) == 3
                op = args[2]
                if op == "<":
                    test_func = f"{rf('LT')}({rf(args[0])}, {rf(args[1])})"
                elif op == "<a":
                    test_func = f"{rf('LT')}({rf(args[0])}, {rf('ABS')}({rf(args[1])}))"
                elif op == "<=":
                    test_func = f"{rf('LE')}({rf(args[0])}, {rf(args[1])})"
                elif op == "<=+1":
                    test_func = f"{rf('LE')}({rf(args[0])}, {rf('PLUS')}({rf(args[1])}, {rf('1')}))"
                elif op == "<=a":
                    test_func = f"{rf('LE')}({rf(args[0])}, {rf('ABS')}({rf(args[1])}))"
                elif op == "<=-a":
                    test_func = f"{rf('LE')}({rf(args[0])}, {rf('NEG')}({rf('ABS')}({rf(args[1])})))"
                elif op == "<=-a+1":
                    test_func = f"{rf('LE')}({rf(args[0])}, {rf('MINUS')}({rf('1')}, {rf('ABS')}({rf(args[1])})))"
                elif op == ">":
                    test_func = f"{rf('GT')}({rf(args[0])}, {rf(args[1])})"
                elif op == ">a":
                    test_func = f"{rf('GT')}({rf(args[0])}, {rf('ABS')}({rf(args[1])}))"
                elif op == ">=":
                    test_func = f"{rf('GE')}({rf(args[0])}, {rf(args[1])})"
                elif op == ">=a":
                    test_func = f"{rf('GE')}({rf(args[0])}, {rf('ABS')}({rf(args[1])}))"
                elif op == ">=a-1":
                    test_func = f"{rf('GE')}({rf(args[0])}, {rf('MINUS')}({rf('ABS')}({rf(args[1])}), {rf('1')}))"
                elif op == "!=":
                    test_func = f"{rf('NE')}({rf(args[0])}, {rf(args[1])})"
                elif op == "%0":
                    test_func = f"{rf('AND')}({rf('NE')}({rf(args[1])}, {rf('0')}), {rf('EQ')}({rf('MOD')}({rf(args[0])}, {rf(args[1])}), {rf('0')}))"
                elif op == "!%0":
                    test_func = f"{rf('AND')}({rf('NE')}({rf(args[1])}, {rf('0')}), {rf('NE')}({rf('MOD')}({rf(args[0])}, {rf(args[1])}), {rf('0')}))"
                elif op == "%0<":
                    test_func = f"{rf('AND')}({rf('GT')}({rf(args[1])}, {rf('0')}), {rf('EQ')}({rf('MOD')}({rf(args[0])}, {rf(args[1])}), {rf('0')}))"
                elif op == "%0>":
                    test_func = f"{rf('AND')}({rf('LT')}({rf(args[1])}, {rf('0')}), {rf('EQ')}({rf('MOD')}({rf(args[0])}, {rf(args[1])}), {rf('0')}))"
                else:
                    # print("unknown operator:", op)
                    pass
            if test_func is None:
                print("ignoring side-condition:", test, args)
                continue
            rhs_process = lambda lhs, rhs: f"{rf('IF')}({test_func}, {rhs}, {lhs})"

        elems = line.split("\"")
        name = elems[1].replace("-", "_").replace("+","_").lower()
        lhs, [] = reformat_term(tokenize(elems[3]))
        try:
            rhs, [] = reformat_term(tokenize(elems[5]))
        except Exception as _e:
            print("element 5", elems[5])
            print("couldn't parse rule:", line)
            sys.exit(1)
        if STYLE == "twee":
            rules.append(f"cnf({name},axiom,{lhs} = {rhs_process(lhs, rhs)}).")
        elif STYLE == "kbc":
            rules.append(f"{lhs} = {rhs_process(lhs, rhs)}")
        else:
            raise Exception("oh no")
    rules = sorted(rules)
    if STYLE == "twee":
        rules.append(f"cnf(if_1,axiom,{rf('IF')}({rf('1')}, {rf('?a')}, {rf('?b')}) = {rf('?a')}).")
    else:
        rules.append(f"{rf('IF')}({rf('1')}, {rf('?a')}, {rf('?b')}) = {rf('?a')}")
    # rule for 0 not necessary
    return "\n".join(rules)

def eval_terms():
    file = "./caviar/data/prefix/evaluation.csv"
    for line in open(file, "r", encoding="utf-8").readlines()[1:]:
        [num, term, hal, i] = line.split(",")
        t, [] = reformat_term(tokenize(term))
        yield t, hal

def gen_data():
    output_folder = f"data_{STYLE}"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for (i, (t, hal)) in enumerate(eval_terms()):
        i = i+1
        if STYLE == "twee":
            t = f"cnf(goal,conjecture, {t} = {rf(str(hal))})."
        open(f"{output_folder}/{i:04}_{hal}.txt", "w").write(t)

gen_data()

with open(output_file, "w") as f:
    f.write(mk_rules())