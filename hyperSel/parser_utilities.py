
import os
import time
from collections import Counter
from difflib import SequenceMatcher
from collections import Counter
from pprint import pprint
import re
import random
import string
import json
try:
    from . import log_utilities
    from . import selenium_utilities
    from . import classifier_utilities
except:
    import log_utilities
    import selenium_utilities
    import classifier_utilities


def generate_wanted_list(demo_objects):
    wanted_list = []
    num_fields = 0
    if demo_objects:
        for data_dict in demo_objects:
            wanted_list.extend(data_dict.values())
        num_fields = len(demo_objects[0])
    return wanted_list, num_fields

def most_frequent_item_percentage(items):
    # Count the occurrences of each item in the list
    item_counts = Counter(items)
    
    # Find the most common item and its count
    most_common_item, count = item_counts.most_common(1)[0]
    
    # Calculate the percentage of occurrences
    percentage = (count / len(items)) * 100
    
    # Return False if percentage is less than 80%
    if percentage < 80:
        return False, False
    
    # Otherwise, return the item and its percentage
    return most_common_item, percentage

def print_all_tag_children_counts(soup):
    # Iterate through every tag in the soup
    #print("NEED LEN 120 OL HERE, how can I know which is correct?")
    tag_skippers = ['svg', 'head', 'body', 'footer','g']
    tags_to_go_through = []
    total_tags = soup.find_all(True)
    #print("total_tags:", len(total_tags))
    for tag in total_tags:
        # 1  
        if len(tag) <= 5:# 120
            continue
        # 2
        if tag.name in tag_skippers:
            continue
        # 3
        inner_skipper = False
        for inner_tag in tag:
            if str(inner_tag.name) == 'None':
                inner_skipper= True
                break
        if inner_skipper:
            continue
        
        # print(len(str(tag)))
        #if len(str(tag)) >= 200000:
        #    log_utilities.log_function(tag)
        #    exit()

        # 4
        all_tag_names = []
        for inner_tag in tag:
            all_tag_names.append(str(inner_tag.name))
        most_common_item, percentage = most_frequent_item_percentage(all_tag_names)
        if percentage == False:
            continue

        tags_to_go_through.append(tag)
    
    data = go_through_filtered_tags(tags_to_go_through)
    return data

def extract_attributes(tag, single_class=True):
    """
    Extract attributes, text, and children recursively from a BeautifulSoup tag.

    Parameters:
    - tag (BeautifulSoup.Tag): The tag to extract data from.
    - single_class (bool): If True, simplifies single-class lists into strings.

    Returns:
    - dict: Dictionary representation of the tag.
    """
    if not tag.name:
        return None  # Skip non-tags (e.g., strings outside of tags)

    tag_info = {tag.name: {}}

    # Extract attributes
    for attr, value in tag.attrs.items():
        if attr == "class" and single_class and isinstance(value, list) and len(value) == 1:
            tag_info[tag.name][attr] = value[0]  # Simplify single-class to string
        else:
            tag_info[tag.name][attr] = value

    # Extract direct text content
    if tag.string and tag.string.strip():
        tag_info[tag.name]["text"] = tag.string.strip()

    # Extract children without flattening text
    children = []
    for child in tag.children:
        if child.name:  # Process nested tags
            child_info = extract_attributes(child, single_class)
            if child_info:
                children.append(child_info)
        elif isinstance(child, str) and child.strip():  # Include direct text nodes
            children.append({"text": child.strip()})
    if children:
        tag_info[tag.name]["children"] = children

    return tag_info

def extract_all_texts(data):
    try:
        texts = []

        if isinstance(data, dict):
            for key, value in data.items():
                if key == "text" and isinstance(value, str):
                    texts.append(value)
                else:
                    texts.extend(extract_all_texts(value))
        elif isinstance(data, list):
            for item in data:
                texts.extend(extract_all_texts(item))

        # Deduplicate while preserving order and avoiding unhashable types
        unique_texts = []
        seen = set()
        for text in texts:
            if isinstance(text, str) and text not in seen:
                unique_texts.append(text)
                seen.add(text)

        return unique_texts
    except Exception as e:
        print(e)
        # print(data)
        # input("PAUSE HERE")

def extract_all_urls(data):
    try:
        urls = []

        if isinstance(data, dict):
            for key, value in data.items():
                if key in ["href", "src", "data-url"] and isinstance(value, str):
                    urls.append(value)
                else:
                    urls.extend(extract_all_urls(value))
        elif isinstance(data, list):
            for item in data:
                urls.extend(extract_all_urls(item))

        # Deduplicate while preserving order and avoiding unhashable types
        unique_urls = []
        seen = set()
        for url in urls:
            if isinstance(url, str) and url not in seen:
                unique_urls.append(url)
                seen.add(url)

        return unique_urls
    except Exception as e:
        print(e)
        print(data)
        # input("PAUSE HERE")

def create_dict_from_list(items):
    tag_json = {}
    for i, item in enumerate(items, start=0):
        tag_json[f"item_{i}"] = item
    return tag_json

def skip_string(s):
    s = str(s)
    remove_list = ["\n", "/", "\\", "\t"]
    # Remove each character in the list from the string
    for char in remove_list:
        s = s.replace(char, "")
    
    try:
        if s[0] == "#":
            return True
    except Exception as e:
        return True
    try:
        if s[1] == "#":
            return True
    except Exception as e:
        return True
    
    # JUST EMPIRICAL 
    long_list_of_phrases_to_skip = [
        "+ taxes", "details", "features", "save", "read more", "other", "+ gst", 
        "no image"
    ]
    if s.lower() in long_list_of_phrases_to_skip:
        return True
    

    return len(s) <= 2

def go_through_filtered_tags(tags_to_go_through):    
    # print("tags_to_go_through", len(tags_to_go_through))
    all_tag_data = []
    skipped_data = []
    for i, tag in enumerate(tags_to_go_through):
        all_data_for_tag = []
        for item in tag:
            #print(item)
            data = extract_attributes(item)
            all_data = []
            
            text_data = extract_all_texts(data)
            for j in text_data:
                if skip_string(j):
                    skipped_data.append(f"SKIPPED: [{j}]")
                    # print("SKIPPING", j)
                    continue
                else:
                    all_data.append(j)

            for o in extract_all_urls(data):
                if skip_string(o):
                    skipped_data.append(f"SKIPPED: [{o}]")
                    continue
                else:
                    all_data.append(o)

            data_dict = create_dict_from_list(all_data)

            all_data_for_tag.append(data_dict)

        all_tag_data.append(all_data_for_tag)
    
    filtered_data = filter_valid_data(all_tag_data)
    
    second_filtered = size_filterer(filtered_data=filtered_data)
    # print("second_filtered:", len(second_filtered))

    return second_filtered

def size_filterer(filtered_data, min_size=3):
    # print("filtered_data:", len(filtered_data))
    all_data_filtered = []
    for i, data in enumerate(filtered_data, start=0):
        local_data = []
        # print(i, "data:", len(data))
        for j in data:
            if len(j) < min_size:
                # print("SKIP SMALL SIZE", len(j), j)
                continue
            else:
                local_data.append(j)

        all_data_filtered.append(local_data)
    # print("all_data_filtered:", len(all_data_filtered))

    data_filtered_for_size = []
    for i in all_data_filtered:
        if len(i) < 3:
            continue
        else:
            data_filtered_for_size.append(i)

    if len(data_filtered_for_size) == 1:
        final_data = data_filtered_for_size[0]
        # print("ONLY ONE SET OF DATA POINTS LEFT; RETURN", len(final_data))
        return final_data
    if len(data_filtered_for_size) == 0:
        # print("NO DATA AT ALL")
        return []
    
    return data_filtered_for_size

    # MULTIPLE DATA POINTS, GOTTA FIGURE OUT WHAT IS THE RIGHT STUFF

def filter_valid_data(all_tag_data):
    """
    Filters `all_tag_data` to remove entries where:
    1. The majority of elements are 0.
    2. The majority of elements have a length of 1.

    Args:
        all_tag_data (list of lists): A list where each item is a list of elements to process.

    Returns:
        list: A filtered list containing only the valid entries.
    """
    valid_data = []

    for data in all_tag_data:
        # Extract lengths of each item in `data`
        lengths = [len(item) for item in data]
        
        # Skip empty data
        if not lengths:
            continue

        # Count occurrences of each length
        length_counts = {length: lengths.count(length) for length in set(lengths)}
        most_common_length = max(length_counts, key=length_counts.get)  # Length with the highest count

        # Check if the most common length is 0 or 1
        majority_is_zero_or_one = most_common_length in [0, 1]

        # Exclude data if the majority of elements are 0 or 1
        if majority_is_zero_or_one:
            # log_utilities.log_function(f"MAJORITY ZERO OR 1 {data}")
            continue 

        valid_data.append(data)

    return valid_data

def  alpha_sort_objects(obj):
    ''' EXAMPLE
    {
        "title_0": "2019 Chrysler Pacifica Touring L Minivan",
        "datetime_0": "11/18",
        "distance_0": "175,000km",
        "price_0": "$9,500",
        "url_0": "https://syracuse.craigslist.org/cto/d/liverpool-2019-chrysler-pacifica/7803364992.html",
        "text_0": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAAtJREFUGFdjYAACAAAFAAGq1chRAAAAAElFTkSuQmCC",
        "original_scrape_time": "2024-11-19 11:04:34",
        "recent_scrape_time": "2024-11-19 11:04:34"
    },
    '''
    return dict(sorted(obj.items()))

def assign_types_to_data(data):
    #NOTE: THIS SEEMS, LIKE IT WOULD BE VERY INEFFICIENT LMAOOO 4 LOOPS
    finished_typed_data_sets = []
    for data_set in data:
        typed_data = []
        for item in data_set:
            new_type_items = {}
            for key, value in item.items():
                value_type = classifier_utilities.classify(value)
                value_type_indexed = 0
                while True:
                    value_type_full_string = f"{value_type}_{value_type_indexed}"
                    if value_type_full_string in new_type_items:
                        value_type_indexed+=1
                    else:
                        new_type_items[value_type_full_string] = value
                        break
            
            typed_sorted = alpha_sort_objects(new_type_items)
            typed_data.append(typed_sorted)
        finished_typed_data_sets.append(typed_data)

    return finished_typed_data_sets

def pull_data_from_soup(soup):
    data = print_all_tag_children_counts(soup)
    typed_data = assign_types_to_data(data)
    return typed_data

def calculate_regularity_score(data):
    """
    Calculate the regularity score for a list of objects.
    Structured and meaningful datasets will score higher.
    
    :param data: List of dictionaries
    :return: Regularity score (higher is better)
    """
    if not data:
        return 0

    # Step 1: Key Frequency Consistency
    key_prefixes = [key.rsplit("_", 1)[0] for obj in data for key in obj.keys()]
    prefix_counts = Counter(key_prefixes)
    total_keys = sum(prefix_counts.values())
    key_frequency_score = sum((count / total_keys) ** 2 for count in prefix_counts.values())

    # Step 2: Value Pattern Consistency
    url_pattern = re.compile(r'https?://[^\s]+')
    price_pattern = re.compile(r'^\$\d+(,\d{3})*(\.\d+)?$')
    date_pattern = re.compile(r'\d{1,2}/\d{1,2}')
    value_pattern_score = 0
    total_values = 0

    for obj in data:
        for key, value in obj.items():
            total_values += 1
            if url_pattern.match(str(value)):
                value_pattern_score += 1
            elif price_pattern.match(str(value)):
                value_pattern_score += 1
            elif date_pattern.match(str(value)):
                value_pattern_score += 1
            else:
                # Use SequenceMatcher to compare values across objects
                for other_obj in data:
                    if other_obj is not obj and key in other_obj:
                        similarity = SequenceMatcher(None, str(value), str(other_obj[key])).ratio()
                        value_pattern_score += similarity

    value_pattern_score /= total_values

    # Step 3: Combine Scores
    regularity_score = 0.5 * key_frequency_score + 0.5 * value_pattern_score
    return regularity_score

def decide_which_data_to_use(data_lists_of_objects):
    """
    Decide which list of objects to return based on size and regularity.
    """
    if len(data_lists_of_objects) == 1:
        return data_lists_of_objects[0]
    
    # Step 1: Calculate size percentages
    sizes = [len(lst) for lst in data_lists_of_objects]
    total_size = sum(sizes)
    percentages = [(size / total_size) * 100 for size in sizes]
    
    # Step 2: Calculate regularity scores
    regularity_scores = [calculate_regularity_score(lst) for lst in data_lists_of_objects]
    
    # Step 3: Combine size and regularity scores into a scoring system
    scoring = []
    for i, (size, percentage, regularity_score) in enumerate(zip(sizes, percentages, regularity_scores)):
        scoring.append({
            "index": i,
            "size_rank": None,  # Placeholder for ranking
            "percentage": percentage,
            "regularity_score": regularity_score
        })
    
    # Rank by regularity score and size percentage (weighted equally)
    scoring.sort(key=lambda x: (x["regularity_score"], x["percentage"]), reverse=True)
    for rank, score in enumerate(scoring, start=1):
        score["size_rank"] = rank
    
    # Print scoring system
    # print("Scoring system:", scoring)

    # exit()
    return data_lists_of_objects

def auto_pull_data_from_site(soup, data_index=None):
    data_lists_of_objects = pull_data_from_soup(soup) # [[{}{}}{}], [{}{}}{}]]
    data = decide_which_data_to_use(data_lists_of_objects)
    if data_index:
        try:
            return data[data_index]
        except Exception as e:
            print("ERROR", e)
            return data
            
    return data



def generate_random_person():
    """
    Generate a random person with mandatory and optional fields.
    """
    # Mandatory fields
    person = {
        "first_name": ''.join(random.choices(string.ascii_letters, k=random.randint(5, 10))).capitalize(),
        "last_name": ''.join(random.choices(string.ascii_letters, k=random.randint(5, 10))).capitalize(),
        "age": random.randint(18, 90)
    }

    # Optional fields
    optional_fields = {
        "address": f"{random.randint(100, 999)} {random.choice(['Main St', 'Elm St', 'Maple Ave'])}",
        "postal_code": f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}",
        "phone_number": f"({random.randint(100, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
        "email": f"{''.join(random.choices(string.ascii_letters, k=5))}@example.com",
        "occupation": random.choice(["Engineer", "Doctor", "Artist", "Teacher", "Developer"]),
        "hobbies": random.sample(
            ["reading", "sports", "coding", "painting", "gardening", "gaming"], 
            k=random.randint(0, 3)
        )
    }

    # Add a random subset of optional fields
    for key in random.sample(list(optional_fields.keys()), k=random.randint(0, len(optional_fields))):
        person[key] = optional_fields[key]
    
    return person

def generate_structured_data(num_objects):
    """
    Generate structured data with consistent core fields and optional random fields.
    """
    return [generate_random_person() for _ in range(num_objects)]

def generate_unstructured_data(num_objects):
    """
    Generate unstructured data with semi-sensible keys and random values.
    """
    categories = ["text", "string", "number", "address", "title", "url"]
    data = []
    
    for _ in range(num_objects):
        obj = {}
        for _ in range(random.randint(1, 10)):  # Random number of fields
            # Generate a random key with a sensible prefix
            prefix = random.choice(categories)
            key = f"{prefix}_{random.randint(0, 100)}"
            
            # Generate a random value
            value_type = random.choice(["text", "number", "url", "address"])
            if value_type == "text":
                value = ''.join(random.choices(string.ascii_letters + " ", k=random.randint(5, 20))).strip()
            elif value_type == "number":
                value = random.randint(0, 10000)
            elif value_type == "url":
                value = f"https://example.com/{random.randint(1, 1000)}"
            elif value_type == "address":
                value = f"{random.randint(1, 9999)} {random.choice(['Main St', '2nd Ave', 'Broadway'])}"
            
            obj[key] = value
        data.append(obj)
    return data

def test_structured_vs_unstructured_scoring():
    """
    Test the scoring system with a mix of structured and unstructured datasets.
    """
    datasets = []

    # Generate structured datasets
    for _ in range(3):  # Three structured datasets
        datasets.append(generate_structured_data(random.randint(5, 15)))

    # Generate unstructured datasets
    for _ in range(2):  # Two unstructured datasets
        datasets.append(generate_unstructured_data(random.randint(5, 15)))

    # Run the scoring system on the generated datasets
    print("Generated datasets and their scores:\n")
    for i, dataset in enumerate(datasets):
        print(f"Dataset {i}:")
        print(json.dumps(dataset, indent=2))  # Pretty-print the dataset
        score = calculate_regularity_score(dataset)
        print(f"Regularity Score: {score:.2f}\n{'-' * 50}\n")

    # Use the decision function to select the best dataset
    best_dataset = decide_which_data_to_use(datasets)
    print("Best dataset based on scoring:")
    print(json.dumps(best_dataset, indent=2))

# Run the test function
# test_structured_vs_unstructured_scoring()
if __name__ == '__main__':
    # Run the test function
    test_structured_vs_unstructured_scoring()
    exit()

    site_1 = 'https://peterborough.craigslist.org/search/cta?purveyor=owner#search=1~gallery~0~0'
    driver = selenium_utilities.open_site_selenium(site=site_1)
    selenium_utilities.maximize_the_window(driver)
    time.sleep(5)
    soup = selenium_utilities.get_driver_soup(driver)
    data = auto_pull_data_from_site(soup, data_index=None)
    print("WE WANT TO REMOVE DATA INDEX")
    print("data;", len(data))
    for i in data:
        log_utilities.log_function(i)
    exit()

    site_1 = 'https://www.kijijiautos.ca/cars/bmw/#c=EstateCar&c=Suv&c=Van&ms=3500&od=down&sb=rel&sc=5%3A'
    driver = selenium_utilities.open_site_selenium(site=site_1)
    soup = selenium_utilities.get_driver_soup(driver)
    data = auto_pull_data_from_site(soup, data_index=None)
    log_utilities.log_data(data)

    

