from autoscraper import AutoScraper
import os
import time
try:
    from . import log_utilities
    from . import selenium_utilities
except:
    import log_utilities
    import selenium_utilities


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

def bar():
    soup = log_utilities.load_file_as_soup("./logs/test_soup.txt")
    target_string = '2010 Lexus gs 350 AWD'

    occ = find_all_occurrences(soup, target_string)
    for i in range(len(occ)):
        print(i, occ[i])

def find_all_occurrences(soup, target_string):
    # Retrieve all tags in document order
    all_tags = soup.find_all(True)

    # Filter tags where the target string is in text or attributes
    matching_tags = [
        tag for tag in all_tags 
        if target_string in tag.get_text() or any(target_string in str(value) for value in tag.attrs.values())
    ]

    return matching_tags


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