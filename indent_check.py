with open("cobra_ops.py") as f:
    for i, line in enumerate(f, 1):
        if "\t" in line:
            print(f"Tab character found on line {i}")
