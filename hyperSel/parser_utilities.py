from autoscraper import AutoScraper
import os
import time
from collections import Counter
import html_to_json # html-to-json
from bs4 import BeautifulSoup
try:
    from . import log_utilities
    from . import selenium_utilities
    from . import regex_utilities
except:
    import log_utilities
    import selenium_utilities
    import regex_utilities


def generate_wanted_list(demo_objects):
    wanted_list = []
    num_fields = 0
    if demo_objects:
        for data_dict in demo_objects:
            wanted_list.extend(data_dict.values())
        num_fields = len(demo_objects[0])
    return wanted_list, num_fields

def get_data(demo_objects, html_content, save_scraper=False):
    scraper = AutoScraper()
    scraper_name="scraper"
    scraper_path = f"{scraper_name}.json"

    # Check if the scraper is already saved in the filesystem
    if os.path.exists(scraper_path):
        scraper.load(scraper_name)
    else:
        wanted_list, num_fields = generate_wanted_list(demo_objects)
        result = scraper.build(html=html_content, wanted_list=wanted_list)

        if save_scraper:
            scraper.save(scraper_name)

    # Return results after loading or building
    return scraper.get_result_similar(html_content)

def foo(soup, wanted_list):
    scraper = AutoScraper()
    result = scraper.build(html=str(soup), wanted_list=wanted_list)
    return result

def get_demo_soup():
    driver = selenium_utilities.open_site_selenium(site='https://toronto.craigslist.org/search/cta#search=1~gallery~0~0')
    time.sleep(2)
    log_utilities.log_function(log_string=selenium_utilities.get_driver_soup(driver))
    
def testing_auto_scraper():
    soup = log_utilities.load_file_as_soup("./logs/test_soup.txt")
    print("soup:", len(str(soup)))

    wanted_list = ['2010 Lexus gs 350 AWD']
    res = foo(soup, wanted_list)
    for i in range(len(res)):
        print(i, res[i])

    print(len(res))

'''
47 2022 FORD MUSTANG MACH 1 PREMIUM 5.0L 470HP MANUAL |HANDLING/ELITEPKG
48 2019 JAGUAR F-TYPE R AWD 550HP |NAV|PANO|BLINDSPT|MERIDIAN|SELFPARK
49 2010 DODGE CHALLENGER SRT8 MANUAL 425HP |RAREB5BLUE|ROOF|BLUETOOTH


# MISSING 2020 HYUNDAI TUCSON PREFERRED AWD
'''

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
    print("NEED LEN 120 OL HERE, how can I know which is correct?")
    tag_skippers = ['svg', 'head', 'body', 'footer','g']
    tags_to_go_through = []
    total_tags = soup.find_all(True)
    print("total_tags:", len(total_tags))
    for tag in total_tags:
        # 1  
        if len(tag) != 120:#<5
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
    
    go_through_filtered_tags(tags_to_go_through)

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

def go_through_filtered_tags(tags_to_go_through):
    '''
        One of the big ones gotte in cl-search-results

        and the other is the ol which is inside it, im not sure if it makes more sense to grab the inner or the outer..
            - my guess rn is the inner but im not sure if it makes the most sense on other sites
            - run some experiments on other sites to test

        - then we also need some tooling for guessing what the data that comes back means
            - should be eaiser enough for dates, time,s addresses, postal codes, prices, 
    '''
    print("tags_to_go_through", len(tags_to_go_through))
    for i, tag in enumerate(tags_to_go_through):
        for item in tag:
            print(item)
            data = extract_attributes(item)
            print("data:", data)
            for j in data:
                print(j)
            print("==")
            input("---------------")
        exit()
        input("==")



def bar():
    soup = log_utilities.load_file_as_soup("./logs/test_soup.txt")
    print_all_tag_children_counts(soup)

if __name__ == '__main__':
    bar()
    exit()
    testing_auto_scraper()

    '''
    STEPS FOR WRITING ME OWN

    1. FIRST TEST BY PUTTING IN TITLE SAME FUNCTIONALITY
        - IT SHOULD FIRST GO FIND ALL THE TAGS WITH THAT TITLE
        - THEN GET ANYTHING ELSE THAT HAS THOSE TAGS,
        - HOWEVER ELSE IT NEEDS TO GET THAT DATA
            - TAGS, TEXT, INNARDS, WHATEVER
        - THEN RETURN THE ONE THAT GETS THE MOST

    2. NEXT VERSION
        - GO THROUGHT HE PAGE AND DO IT AUTOMATIALLY SOMEHOW 
            (THIS SHOULD TAKE A LONG TIME)
        - THEN IT SHOULD LIKKE, SEE WHERE THERE ARE LARGE AMOUNTS OF SIMILAR SIZE DATA
        - TAKE THOSE
    '''