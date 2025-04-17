import re
from datetime import datetime

def is_number(s):
    try:
        float(s.replace(",", ""))
        return True
    except ValueError:
        return False

def is_price(s):
    s = s.strip().lower()

    # Define multiple regex patterns to match different price formats
    patterns = [
        # Pattern 1: "USD 1,000.00" or "1,000 USD"
        r'^(?:usd|ca|cad|eur|gbp|aud|jpy|inr)?\s*[\$€£¥₹]?\s*\d{1,3}(?:,\d{3})*\.\d{1,2}$',

        # Pattern 2: "$1,000" or "C$1,000"
        r'^[\$€£¥₹c]?(\d{1,3}(?:,\d{3})*)+(\.\d{1,2})?$',

        # Pattern 3: "100 dollars" or "100 CAD"
        r'^\d+\s*(dollars?|cad|usd|eur|gbp|inr|aud|jpy|canadian)$',

        # Pattern 4: Just number with symbol "$100" or "€100"
        r'^[\$€£¥₹]\d{1,3}(?:,\d{3})*(\.\d{1,2})?$',

        # Pattern 5: Number with currency suffix "100 USD" or "1,000 CAD"
        r'^\d{1,3}(?:,\d{3})*(\.\d{1,2})?\s*(usd|cad|eur|gbp|inr|jpy|aud|canadian|dollars?)$',

        # Pattern 6: "₹1000", "€1000", "$1000", or "$1,000"
        r'^[\$€£¥₹]\d{1,3}(?:,\d{3})*(\.\d{1,2})?$',

        # Pattern 7: A number with optional currency code at the end like "100 USD"
        r'^\d+\s*(usd|cad|ca|canadian|dollars?|eur|gbp|inr|jpy|aud)?$',

        # Pattern 8: Currency prefix before price with symbol "$979,000" or "C$979,000"
        r'^[a-zA-Z]{1,3}\$?\s*\d{1,3}(?:,\d{3})*(\.\d{1,2})?$'
    ]

    # Check each pattern
    for pattern in patterns:
        if re.match(pattern, s, re.IGNORECASE):
            return True

    # If no pattern matched, return False
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
    if not is_url(s):
        return False

    image_extensions = ("png", "jpg", "jpeg", "gif", "bmp", "webp", "svg")
    separators = [".", "-"]

    s = s.lower()
    for sep in separators:
        for ext in image_extensions:
            if s.endswith(f"{sep}{ext}"):
                return True
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

def classify(s, title_threshold=50):
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
        elif 9 <= s_len <= title_threshold:
            return "title"
        else:
            return "text"


if __name__ == "__main__":
    pass