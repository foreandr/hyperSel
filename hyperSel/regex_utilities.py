import re

# Define regex patterns for major data types
data_types = {
    "ALPHABETIC": r"^[a-zA-Z]+$",
    "ALPHANUMERIC": r"^[a-zA-Z0-9]+$",
    "BINARY_NUMBER": r"^[01]+$",
    "BASE64": r"^[A-Za-z0-9+/=]+$",
    "HEX_COLOR": r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$",
    "EMAIL": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "URL": r"^(https?|ftp)://[^\s/$.?#].[^\s]*$",
    "DATE_ISO": r"^\d{4}-\d{2}-\d{2}$",
    "US_DATE": r"^\d{2}/\d{2}/\d{4}$",
    "TIME_24H": r"^([01]\d|2[0-3]):([0-5]\d)$",
    "CREDIT_CARD": r"^\d{4}-\d{4}-\d{4}-\d{4}$",
    "IPV4": r"^((25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$",
    "IPV6": r"^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|::)$",
    "UUID": r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
    "PHONE_NUMBER": r"^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$",
    "ZIP_CODE": r"^\d{5}(-\d{4})?$",
    "MONEY": r"^\$\d+(\.\d{2})?$",
    "LAT_LONG_COORDINATES": r"^-?\d{1,3}\.\d+,\s?-?\d{1,3}\.\d+$",
    "ISBN": r"^(97(8|9))?\d{9}(\d|X)$",
    "HTML_TAG": r"<[^>]+>",
    "ADDRESS": r"^\d+\s\w+(\s\w+)*,\s?\w+,\s?[A-Z]{2}\s\d{5}$",  # Simplistic US address pattern
}

# Function to infer the type of a given string
def infer_data_type(input_string):
    # Match known patterns
    for data_type, pattern in data_types.items():
        if re.fullmatch(pattern, input_string):
            return data_type

    return "RAW_STRING"

# Test cases
test_strings = [
    "hello",                      # ALPHABETIC
    "123abc",                     # ALPHANUMERIC
    "010101",                     # BINARY_NUMBER
    "YWJjZA==",                   # BASE64
    "#FF5733",                    # HEX_COLOR
    "test@example.com",           # EMAIL
    "https://example.com",        # URL
    "2024-11-15",                 # DATE_ISO
    "11/15/2024",                 # US_DATE
    "14:30",                      # TIME_24H
    "1234-5678-9876-5432",        # CREDIT_CARD
    "192.168.1.1",                # IPV4
    "2001:0db8::1",               # IPV6
    "550e8400-e29b-41d4-a716-446655440000", # UUID
    "(123) 456-7890",             # PHONE_NUMBER
    "12345",                      # ZIP_CODE
    "$19.99",                     # MONEY
    "37.7749,-122.4194",          # LAT_LONG_COORDINATES
    "978-3-16-148410-0",          # ISBN
    "<div>Hello</div>",           # HTML_TAG
    "123 Main St, Springfield, IL 62704", # ADDRESS
    "This is a very long text that seems to be a description, not just a short phrase.", # DESCRIPTION
    "Some unstructured address like 456 Elm St, Boston MA, 02110", # ADDRESS_LIKE
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 5,  # LONG_TEXT
    
    # Edge cases
    "11/15/2024",                 # DATE but might match BASE64
    "ABC1234567890123456789012345678901234567890", # Long ALPHANUMERIC
    "https://a.very.long.domain.name.com/with/a/long/path", # Long URL
    "2001:0db8:85a3:0000:0000:8a2e:0370:7334",    # Valid IPV6
    "1234.56",                   # Ambiguous: MONEY or DECIMAL_NUMBER
    "Lorem ipsum dolor sit amet consectetuer adipiscing elit sed diam nonummy.", # DESCRIPTION
    "123 Fake Street, Springfield, USA",          # ADDRESS but less structured
    "YWJjZA!@",                   # Invalid BASE64-like string
    "370000000000002",            # Valid but simplified CREDIT_CARD
    "abcdef123456",               # HEX_COLOR-like but invalid length
    "99999",                      # Ambiguous: ZIP_CODE or numeric
    "<html><body></body></html>", # HTML_TAG but long
    "notareal.email@",            # Invalid EMAIL
    "ftp://example.com/resource", # URL but with FTP
    "123 Main St Springfield IL 62704",           # ADDRESS missing commas
    "123-456",                    # Ambiguous: PHONE_NUMBER-like
    "55:55",                      # TIME-like but invalid
]
## Run inference
#for string in test_strings:
#    result = infer_data_type(string)
#    print(f"'{string[:50]}...' -> {result}")
