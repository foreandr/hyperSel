import re
import numpy as np
from collections import Counter
from random_string_detector import RandomStringDetector

# Initialize Random String Detector
detector = RandomStringDetector(allow_numbers=True)

# Sample strings dataset
strings = [
    {'text_24': 'tnMbF'},
    {'title_7': 'Peterborough'},
    {'text_25': 'jzFoAc'},
    {'text_26': 'iOqfBW'},
    {'text_27': 'dURCJM'},
    {'url_1': 'https://www.kijiji.ca/v-cars-trucks/peterborough/2006-f250-crew-cab/1705413535'},
    {'text_1': 'foXMEw'},
    {'title_1': '2006 F250 Crew Cab'},
    {'text_2': 'kNSVXK'},
    {'title_2': 'Click to add to My Favourites'},
    {'text_3': 'jwgKQA'},
    {'text_4': 'hizdRN'},
    {'price_1': '$2,000'}
]

# Method 1: N-gram frequency analysis
def ngram_randomness(s):
    ngram_threshold = 0.1
    common_ngrams = {'th', 'he', 'in', 'er', 'an'}
    count = sum(1 for i in range(len(s) - 1) if s[i:i+2].lower() in common_ngrams)
    return count / max(len(s), 1) < ngram_threshold

# Method 2: Shannon entropy
def entropy_randomness(s):
    prob = [freq / len(s) for freq in Counter(s).values()]
    entropy = -sum(p * np.log2(p) for p in prob)
    return entropy < 3 or entropy > 5  # Adjusted range for short strings

# Method 3: Dictionary-based check
dictionary = {'Peterborough', 'Click', 'to', 'add', 'My', 'Favourites', 'Crew', 'Cab'}
def dictionary_check(s):
    words = re.findall(r'\w+', s)
    return all(word.lower() not in dictionary for word in words)

# Method 4: Frequency of repeated characters
def repeated_characters(s):
    return any(s.lower().count(ch) > 2 for ch in set(s.lower()))

# Method 5: Consonant clusters
def consonant_clusters(s):
    return re.search(r'[^aeiou]{4,}', s)

# Method 6: String length consistency
def length_randomness(s):
    return len(s) < 5 or len(s) > 50

# Method 7: Regex for typical identifiers
def identifier_check(s):
    return not re.match(r'[A-Za-z_]\w*$', s)

# Method 8: Case mix analysis
def case_mix(s):
    return not (any(c.islower() for c in s) and any(c.isupper() for c in s))

# Method 9: Random String Detector (pypi package)
def random_string_detector(s):
    return detector(s)

# Evaluate strings
results = {}
for entry in strings:
    key, value = list(entry.items())[0]
    results[key] = {
        "value": value,
        "ngram_randomness": ngram_randomness(value),
        "entropy_randomness": entropy_randomness(value),
        "dictionary_check": dictionary_check(value),
        "repeated_characters": repeated_characters(value),
        "consonant_clusters": bool(consonant_clusters(value)),
        "length_randomness": length_randomness(value),
        "identifier_check": identifier_check(value),
        "case_mix": case_mix(value),
        "random_string_detector": random_string_detector(value),
    }

# Improved Summary
print("String Analysis Results:")
for key, result in results.items():
    random_methods = [method for method, is_random in result.items() if is_random and method != "value"]
    print(f"{key}: {result['value']}")
    print(f"  Randomness Triggered by: {random_methods}")
    if random_methods:
        print("  - Reasons:")
        for method in random_methods:
            print(f"    -> {method}: {result[method]}")
    print("---")
