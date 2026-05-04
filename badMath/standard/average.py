from .sum import sum as sum_func

def average(numbers):
    if not numbers:
        return 0
    return sum_func(numbers) / len(numbers)
