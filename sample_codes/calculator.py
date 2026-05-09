"""
Sample Python Code: Calculator
Used for demonstration and testing of the AI Test Generator.
"""


def add(a, b):
    """Add two numbers."""
    return a + b


def subtract(a, b):
    """Subtract b from a."""
    return a - b


def multiply(a, b):
    """Multiply two numbers."""
    return a * b


def divide(a, b):
    """Divide a by b with error handling."""
    if b == 0:
        return "error: division by zero"
    return a / b


def power(base, exp):
    """Calculate base raised to the power of exp."""
    if exp < 0:
        if base == 0:
            return "error: undefined"
        return 1 / (base ** abs(exp))
    return base ** exp


def factorial(n):
    """Calculate factorial of n."""
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)


def is_prime(n):
    """Check if n is a prime number."""
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def grade_calculator(score):
    """Calculate letter grade from score."""
    if not isinstance(score, (int, float)):
        raise TypeError("Score must be a number")
    if score < 0 or score > 100:
        raise ValueError("Score must be between 0 and 100")
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n < 0:
        raise ValueError("Input must be non-negative")
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def find_max(numbers):
    """Find the maximum value in a list."""
    if not numbers:
        return None
    if not isinstance(numbers, list):
        raise TypeError("Input must be a list")
    max_val = numbers[0]
    for num in numbers[1:]:
        if num > max_val:
            max_val = num
    return max_val


def reverse_string(s):
    """Reverse a string."""
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return s[::-1]


def is_palindrome(s):
    """Check if a string is a palindrome."""
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    cleaned = s.lower().replace(" ", "")
    return cleaned == cleaned[::-1]
