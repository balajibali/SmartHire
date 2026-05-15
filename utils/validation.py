import re


# 📧 EMAIL VALIDATION
def is_valid_email(email):
    if not email:
        return False

    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return re.match(pattern, email) is not None


# 📱 PHONE VALIDATION
def is_valid_phone(phone):
    if not phone:
        return False

    pattern = r"^\d{10}$"
    return re.match(pattern, phone) is not None


# 🔍 REQUIRED FIELD CHECK
def is_not_empty(value):
    return value is not None and value.strip() != ""