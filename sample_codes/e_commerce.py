"""
Sample Python Code: E-Commerce Cart System
Used for demonstration and testing of the AI Test Generator.
"""

class ShoppingCart:
    def __init__(self, user_id):
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Invalid user ID")
        self.user_id = user_id
        self.items = {}  # Format: {item_id: {'price': float, 'quantity': int}}
        self.discount_code = None

    def add_item(self, item_id, price, quantity=1):
        """Add an item to the cart."""
        if not isinstance(item_id, str) or not item_id:
            raise ValueError("Invalid item ID")
        if price < 0:
            raise ValueError("Price cannot be negative")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        if item_id in self.items:
            self.items[item_id]['quantity'] += quantity
        else:
            self.items[item_id] = {'price': float(price), 'quantity': quantity}
        
        return True

    def remove_item(self, item_id, quantity=None):
        """Remove an item or decrease its quantity."""
        if item_id not in self.items:
            return False

        if quantity is None or self.items[item_id]['quantity'] <= quantity:
            del self.items[item_id]
        else:
            if quantity <= 0:
                raise ValueError("Quantity to remove must be positive")
            self.items[item_id]['quantity'] -= quantity
            
        return True

    def apply_discount(self, code):
        """Apply a discount code."""
        valid_codes = {"SAVE10": 0.10, "SAVE20": 0.20, "HALF": 0.50}
        
        if not code or not isinstance(code, str):
            return False
            
        code = code.upper()
        if code in valid_codes:
            self.discount_code = code
            return True
        return False

    def calculate_total(self):
        """Calculate the total price of the cart."""
        subtotal = sum(item['price'] * item['quantity'] for item in self.items.values())
        
        if subtotal == 0:
            return 0.0
            
        discount = 0.0
        if self.discount_code:
            discount_rates = {"SAVE10": 0.10, "SAVE20": 0.20, "HALF": 0.50}
            discount = subtotal * discount_rates.get(self.discount_code, 0)
            
        total = subtotal - discount
        
        # Apply tax
        tax_rate = 0.08
        total = total * (1 + tax_rate)
        
        return round(total, 2)
