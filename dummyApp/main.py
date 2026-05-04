import math

def compute(values):
    return sum(values), math.sqrt(sum(values))

def main():
    values = [1, 4, 9, 16]
    total, root = compute(values)
    print(f"values={values}")
    print(f"total={total}")
    print(f"sqrt(total)={root}")

if __name__ == "__main__":
    main()
