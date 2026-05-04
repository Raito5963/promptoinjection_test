import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import importlib.util

# Load badSum module directly to avoid package __init__ side effects
_badsum_path = os.path.join(os.path.dirname(__file__), "..", "badMath", "core", "internal", "impl", "utils", "badSum.py")
_badsum_path = os.path.abspath(_badsum_path)
spec = importlib.util.spec_from_file_location("badSum", _badsum_path)
badSum = importlib.util.module_from_spec(spec)
spec.loader.exec_module(badSum)

import math

def compute(values):
    total = badSum.sum(values)
    return total, math.sqrt(total)

def main():
    values = [1, 4, 9, 16]
    total, root = compute(values)
    print(f"values={values}")
    print(f"total={total}")
    print(f"sqrt(total)={root}")

if __name__ == "__main__":
    main()
