import re
from z3 import *
import z3
import glob

twee_log = "run_log_twee_v1.txt"
with open(twee_log, "r") as f:
    content = f.read()

# find lines that are followed by empty line or "Failure"
# line is data/xxxx_y.txt => extract xxxx
pattern = re.compile(r"Starting with data/(\d+)_(0|1).txt:\n(\n|Failure)", re.DOTALL | re.MULTILINE)

failures = []
for match in pattern.finditer(content):
    id = int(match.group(1))
    failures.append(id)
    # print(id)


class Formula:
    def __init__(self, id, args):
        self.id = id
        self.args = args
        
    def __repr__(self):
        if len(self.args) == 0:
            return self.id
        else:
            return f"{self.id}({','.join(map(str, self.args))})"
        

def parse_formula(s):
    s = s.replace(" ","")
    word = ""
    while s[0] not in ['(',')',',']:
        word += s[0]
        s = s[1:]
    if s[0] == '(':
        s = s[1:]
        args = []
        while True:
            if s[0] == ')':
                s = s[1:]
                break
            else:
                arg, s = parse_formula(s)
                args.append(arg)
                if s[0] == ',':
                    s = s[1:]
        return Formula(word, args), s
    else:
        return Formula(word, []), s

filelist = glob.glob("data/*.txt")
# print(filelist)

formulas = []
for id in failures:
    file = [f for f in filelist if f.startswith(f"data/{id:04d}_")]
    assert len(file) == 1
    file = file[0]
    with open(file, "r") as f:
        content = f.read()
        formula, _ = parse_formula(content)
        if str(formula) != content.replace(" ",""):
            print(f"formula {id} is not parsed correctly")
            print(str(formula))
            print(content.replace(" ",""))
            sys.exit(1)
        formulas.append((id, formula))

print("Checking formulas...")

def get_variables(formula: Formula) -> list[str]:
    if len(formula.args) == 0 and formula.id.lower().startswith("v"):
        return [formula.id.lower()]
    else:
        return sum([get_variables(arg) for arg in formula.args], [])
    
def bool_args(args: list[ArithRef | BoolRef]) -> list[BoolRef]:
    new_args = []
    for arg in args:
        if isinstance(arg, BoolRef):
            new_args.append(arg)
        elif isinstance(arg, ArithRef) or isinstance(arg, int):
            new_args.append(arg != 0)
        else:
            raise Exception(f"unknown argument type: {type(arg)}")
    return new_args

def smt_formula(formula: Formula, variables: dict[str, ArithRef]) -> ArithRef | BoolRef:
    if len(formula.args) == 0:
        if formula.id.lower() in variables:
            return variables[formula.id.lower()]
        elif formula.id.startswith("NUMNEG"):
            return -int(formula.id[6:])
        elif formula.id.startswith("NUM"):
            return int(formula.id[3:])
        else:
            raise Exception(f"unknown constant: {formula.id}")
    else:
        args = [smt_formula(arg, variables) for arg in formula.args]
        id = formula.id
        if id == "EQ":
            return args[0] == args[1]
        elif id == "NE":
            return args[0] != args[1]
        elif id == "LT":
            return args[0] < args[1]
        elif id == "LE":
            return args[0] <= args[1]
        elif id == "GT":
            return args[0] > args[1]
        elif id == "GE":
            return args[0] >= args[1]
        elif id == "AND":
            return And(bool_args(args))
        elif id == "OR":
            return Or(bool_args(args))
        elif id == "NOT":
            return Not(bool_args(args)[0])
        elif id == "IF":
            return If(bool_args(args)[0], args[1], args[2])
        elif id == "PLUS":
            return args[0] + args[1]
        elif id == "MINUS":
            return args[0] - args[1]
        elif id == "MUL":
            return args[0] * args[1]
        elif id == "DIV":
            return args[0] / args[1]
        elif id == "MOD":
            return args[0] % args[1]
        elif id == "MAX":
            return If(args[0] > args[1], args[0], args[1])
        elif id == "MIN":
            return If(args[0] < args[1], args[0], args[1])
        elif id == "ABS":
            return abs(args[0])
        else:
            raise Exception(f"unknown operator: {id}")

true_formulas = []
false_formulas = []
ambiguous_formulas = []
unsolvable_formulas = []

for id, formula in formulas:
    # print("Checking formula:", id)
    # print("formula:", formula)
    variables = {v: Int(v) for v in get_variables(formula)}
    # print("variables:", variables)
    f = smt_formula(formula, variables)
    possible = []
    for result in [True, False]:
        s = Solver()
        # for v in variables.values():
        #     s.add(v >= 0)
        s.push()
        s.add(f == result)
        if s.check() == sat:
            possible.append(result)
        s.pop()
    if len(possible) == 0:
        unsolvable_formulas.append((id, formula))
    elif len(possible) == 1:
        if possible[0]:
            true_formulas.append((id, formula))
        else:
            false_formulas.append((id, formula))
    else:
        ambiguous_formulas.append((id, formula))
        
print("True:")
for id, formula in true_formulas:
    print(f"  {id}: {formula}")
print()
print("False:")
for id, formula in false_formulas:
    print(f"  {id}: {formula}")
print()
print("Ambiguous:")
for id, formula in ambiguous_formulas:
    print(f"  {id}: {formula}")
print()
print("Unsolvable:")
for id, formula in unsolvable_formulas:
    print(f"  {id}: {formula}")

    
# s = Solver()

# v0, v1 = Ints('v0 v1')

# formula_27 = ((v0-v1)+81)/68 != 0


# for result in [True, False]:
#     s.push()
#     s.add(formula_27 == result)
#     if s.check() == sat:
#         print(f"formula_27 is solvable for {result}")
#     else:
#         print(f"formula_27 is not solvable for {result}")
#     s.pop()


# cat rules.p data_twee/0005_0.txt | ./twee.sh 10 - 