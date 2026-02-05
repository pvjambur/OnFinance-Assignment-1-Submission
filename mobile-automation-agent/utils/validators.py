import re

def validate_email(email: str) -> bool:
    if not email: return False
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def validate_pin(pin: str) -> bool:
    """Check if PIN is 4-6 digits"""
    if not pin: return False
    return pin.isdigit() and 4 <= len(pin) <= 6

def validate_package_name(package: str) -> bool:
    """Basic checkout for com.example.app"""
    if not package: return False
    return len(package.split('.')) >= 2
