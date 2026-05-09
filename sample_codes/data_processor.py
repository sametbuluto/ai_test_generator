"""
Sample Python Code: Data Processor
Used for demonstration and testing of the AI Test Generator.
"""

def clean_data(data_list):
    """Clean a list of mixed data types by keeping only valid numbers."""
    if not isinstance(data_list, list):
        raise TypeError("Input must be a list")
        
    cleaned = []
    for item in data_list:
        if item is None:
            continue
            
        if isinstance(item, (int, float)):
            cleaned.append(float(item))
        elif isinstance(item, str):
            item = item.strip()
            if not item:
                continue
            try:
                # Remove common currency symbols and commas
                clean_str = item.replace('$', '').replace('€', '').replace(',', '')
                cleaned.append(float(clean_str))
            except ValueError:
                pass
                
    return cleaned


def calculate_statistics(numbers):
    """Calculate basic statistics from a list of numbers."""
    if not isinstance(numbers, list):
        raise TypeError("Input must be a list")
        
    if not numbers:
        return {"mean": 0, "min": None, "max": None, "count": 0}
        
    # Ensure all items are numbers
    if not all(isinstance(x, (int, float)) for x in numbers):
        raise ValueError("All elements must be numbers")
        
    count = len(numbers)
    total = sum(numbers)
    
    return {
        "mean": total / count,
        "min": min(numbers),
        "max": max(numbers),
        "count": count
    }


def filter_outliers(numbers, threshold=2.0):
    """Filter out values that are too far from the mean."""
    stats = calculate_statistics(numbers)
    if stats["count"] == 0:
        return []
        
    mean = stats["mean"]
    
    # Calculate standard deviation
    variance = sum((x - mean) ** 2 for x in numbers) / stats["count"]
    std_dev = variance ** 0.5
    
    if std_dev == 0:
        return numbers.copy()
        
    # Keep numbers within threshold standard deviations
    filtered = [x for x in numbers if abs(x - mean) <= threshold * std_dev]
    
    return filtered
