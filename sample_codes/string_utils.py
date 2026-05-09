"""
Sample Python Code: String Utilities
Used for demonstration and testing of the AI Test Generator.
"""


def count_words(text):
    """Count the number of words in a text."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    if not text.strip():
        return 0
    return len(text.split())


def capitalize_words(text):
    """Capitalize the first letter of each word."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    return " ".join(word.capitalize() for word in text.split())


def truncate(text, max_length, suffix="..."):
    """Truncate text to a maximum length."""
    if not isinstance(text, str):
        raise TypeError("Text must be a string")
    if not isinstance(max_length, int) or max_length < 0:
        raise ValueError("max_length must be a non-negative integer")
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_emails(text):
    """Extract email addresses from text."""
    import re
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)


def caesar_cipher(text, shift):
    """Encrypt text using Caesar cipher."""
    if not isinstance(text, str):
        raise TypeError("Text must be a string")
    if not isinstance(shift, int):
        raise TypeError("Shift must be an integer")
    
    result = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            shifted = (ord(char) - base + shift) % 26 + base
            result.append(chr(shifted))
        else:
            result.append(char)
    return "".join(result)
