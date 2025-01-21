import re
from datetime import datetime

def is_number(s):
    try:
        float(s.replace(",", ""))
        return True
    except ValueError:
        return False

def is_price(s):
    s = s.strip()
    s = re.sub(r'^[\$€£¥₹]', '', s)
    try:
        num = float(s.replace(",", ""))
        if num >= 0 and re.match(r'^\d{1,3}(,\d{3})*(\.\d{1,2})?$', s) or s.isdigit():
            return True
    except ValueError:
        pass
    return False

def is_datetime(s):
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%m/%d",  # For cases like "10/16"
    ]
    for fmt in formats:
        try:
            datetime.strptime(s, fmt)
            return True
        except ValueError:
            continue
    return False

def is_email(s):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, s) is not None

def is_url(s):
    url_regex = r'^(https?:\/\/)?(www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(\S*)$'
    return re.match(url_regex, s) is not None

def is_image_url(s):
    if is_url(s):
        image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg")
        return s.lower().endswith(image_extensions)
    return False

def is_distance(s):
    distance_regex = r'^\d{1,3}(,\d{3})*(\.\d+)?\s*(km|miles|kilometers|meters|mi|ft|feet)\b'
    return re.match(distance_regex, s.strip(), re.IGNORECASE) is not None

def is_postal_code(s):
    # Common formats for postal codes
    postal_code_regexes = {
        "zip_code": r'^\d{5}(-\d{4})?$',  # US ZIP codes (e.g., 12345 or 12345-6789)
        "postal_code": r'^[A-Za-z]\d[A-Za-z]\s?\d[A-Za-z]\d$',  # Canadian postal codes (e.g., K1A 0B1)
        "postal_code": r'^[A-Za-z]{1,2}\d{1,2}[A-Za-z]?\s?\d[A-Za-z]{2}$',  # UK postcodes (e.g., SW1A 1AA)
    }
    for postal_type, regex in postal_code_regexes.items():
        if re.match(regex, s.strip()):
            return postal_type
    return None

def classify(s):
    if is_email(s):
        return "email"
    elif is_image_url(s):
        return "image_url"
    elif is_url(s):
        return "url"
    elif postal_code_type := is_postal_code(s):
        if is_price(s):  # If it matches both ZIP code and price, return "number"
            return "number"
        return postal_code_type  # Return the specific postal code type
    elif is_price(s):
        return "price"
    elif is_distance(s):
        return "distance"
    elif is_datetime(s):
        return "datetime"
    elif is_number(s):
        return "number"
    else:
        s_len = len(s)
        if s_len >= 200:
            return "desc"
        elif 9 <= s_len <= 50:
            return "title"
        else:
            return "text"

if __name__ == "__main__":
    pass