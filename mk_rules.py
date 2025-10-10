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

for line in lines():
    if "rw!(" not in line: continue

    # so far we ignore side-conditions
    if "if" in line: continue

    elems = line.split("\"")
    lhs = elems[3]
    rhs = elems[5]
    print(lhs + " ===> " + rhs)
