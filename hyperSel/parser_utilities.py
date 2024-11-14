
import requests
import time
import json
from autoscraper import AutoScraper

import re

import re

def build_flexible_car_regex(strings):
    """
    Generates a regex pattern that captures the structure of car titles across diverse examples.

    Parameters:
        strings (list of str): The list of car title strings to analyze.

    Returns:
        str: A regex pattern that generalizes the provided car titles.
    """
    if not strings:
        return ""

    # Split each string into tokens
    tokenized_strings = [s.split() for s in strings]
    num_tokens = max(len(tokens) for tokens in tokenized_strings)

    # List to store regex patterns for each token position
    patterns = []

    for i in range(num_tokens):
        token_samples = [tokens[i] for tokens in tokenized_strings if len(tokens) > i]
        
        # Identify the common structure of each token position
        if all(re.match(r'^\d{4}$', t) for t in token_samples):  # Year (e.g., "2012")
            patterns.append(r'\d{4}')
        elif all(re.match(r'^[A-Z][a-zA-Z]+$', t) for t in token_samples):  # Capitalized words (Make/Model)
            patterns.append(r'[A-Z][a-zA-Z]+')
        elif all(re.match(r'^\d+[a-zA-Z]*$', t) for t in token_samples):  # Numeric with possible suffix (e.g., "135i")
            patterns.append(r'\d+[a-zA-Z]*')
        elif all(re.match(r'^[a-zA-Z]+$', t) for t in token_samples):  # Alphanumeric words (Trims)
            patterns.append(r'[a-zA-Z]+')
        else:
            patterns.append(r'\S+')  # Fallback pattern for mixed/unknown formats

    # Join patterns with spaces and optional groups to handle missing parts
    final_pattern = r'\b' + r'\s+'.join(f'(?:{pat})?' for pat in patterns) + r'\b'
    return final_pattern

# Example usage with diverse car titles
strings = [
    "2012 BMW 1 Series 135i",
    "2011 BMW 1 Series",
    "2008 BMW 1 Series 128",
    "2010 BMW 1 Series 128i",
    "2012 BMW 1 Series M Sport",
    "2020 Audi A4 Allroad",
    "2019 Mercedes-Benz GLC 300 4MATIC",
    "2017 Honda Civic LX",
    "2015 Ford Mustang GT",
    "2018 Tesla Model 3 Performance"
]

pattern = build_flexible_car_regex(strings)
print("Generated regex pattern:", pattern)

# Test the pattern
for s in strings:
    print(f"Testing '{s}':", bool(re.match(pattern, s)))

exit()
try:
    from . import log_utilities
    from . import selenium_utilities
except ImportError:
    import selenium_utilities
    import log_utilities

# Fetch HTML content from the Kijiji Autos page using Selenium
url = "https://www.kijijiautos.ca/cars/bmw/1-series/#ms=3500%3B132&od=down&sb=rel"
driver = selenium_utilities.open_site_selenium(url)
html_content = str(selenium_utilities.get_driver_soup(driver))

def generate_wanted_list(data_dicts):
    wanted_list = []
    num_fields = 0
    if data_dicts:
        for data_dict in data_dicts:
            wanted_list.extend(data_dict.values())
        num_fields = len(data_dicts[0])
    return wanted_list, num_fields

# Example input data to generate the `wanted_list`
example_data = [
    {
        "title": "2012 BMW 1 Series 135i",
        "mileage": "125,800 km",
        "location": "-, NB",
        "price": "$14,950"
    },
    {
        "title": "2011 BMW 1 Series",
        "mileage": "230,000 km",
        "location": "-, ON",
        "price": "$4,500"
    }
]

# Generate the wanted list and determine the number of fields per dictionary
wanted_list, num_fields = generate_wanted_list(example_data)

# Initialize AutoScraper
scraper = AutoScraper()

print("\nRunning AutoScraper...")
start_time = time.time()

# Build the scraper using the generated wanted list
result = scraper.build(html=html_content, wanted_list=wanted_list)

# Function to categorize the items based on patterns
def categorize_items(result):
    titles = [item for item in result if "BMW" in item]
    mileages = [item for item in result if "km" in item and "km" in item]
    locations = [item for item in result if any(loc in item for loc in ["ON", "NB", "QC", "AB", "BC"])]
    prices = [item for item in result if "$" in item]
    return titles, mileages, locations, prices

# Categorize the extracted items
titles, mileages, locations, prices = categorize_items(result)

# Ensure that all lists have the same length
min_length = min(len(titles), len(mileages), len(locations), len(prices))
titles, mileages, locations, prices = titles[:min_length], mileages[:min_length], locations[:min_length], prices[:min_length]

# Combine the data into structured JSON format
cars = []
for i in range(min_length):
    car_entry = {
        "title": titles[i],
        "mileage": mileages[i],
        "location": locations[i],
        "price": prices[i]
    }
    cars.append(car_entry)

# Log the structured data
log_utilities.log_data(cars)

# Print structured data for verification
print("Structured Car Data:", json.dumps(cars, indent=4))

# Print execution time
print("Execution Time:", time.time() - start_time)

# Optional: Save the model for reuse
scraper.save("kijiji_car_scraper")