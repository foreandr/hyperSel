#AGAIN
import subprocess
import psutil
import string
import random
from screeninfo import get_monitors
import time
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from html.parser import HTMLParser
from lxml.html import fromstring
import html5lib

valid_html_tags = [
    # Comprehensive list of tags
    "a", "abbr", "address", "area", "article", "aside", "audio", "b", "base",
    "bdi", "bdo", "blockquote", "body", "br", "button", "canvas", "caption",
    "cite", "code", "col", "colgroup", "data", "datalist", "dd", "del", "details",
    "dfn", "dialog", "div", "dl", "dt", "em", "embed", "fieldset", "figcaption",
    "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "head",
    "header", "hr", "html", "i", "iframe", "img", "input", "ins", "kbd", "label",
    "legend", "li", "link", "main", "map", "mark", "meta", "meter", "nav", "noscript",
    "object", "ol", "optgroup", "option", "output", "p", "picture", "pre", "progress",
    "q", "rb", "rp", "rt", "rtc", "ruby", "s", "samp", "script", "section", "select",
    "small", "source", "span", "strong", "style", "sub", "summary", "sup", "svg",
    "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "time",
    "title", "tr", "track", "u", "ul", "var", "video", "wbr", "selected", "loading", 
    "dot", "meta-line", "swipe", "icom-", "cl-favorite-button", "icon-only", 
    "cl-banish-button", "bd-button", "ng-container", "ng-template", "custom-element", 
    "my-component", "react-fragment", "vue-slot", "angular-directive", "web-component", 
    "slider-back-arrow", "gallery-inner", "cl-gallery", "icon", "separator", 
    "posting-title", "text-only", "cl-app-anchor", "app-root", "app-header", "app-footer", 
    "dynamic-content", "shadow-root", "swipe-wrap", "slider-forward-arrow", "gallery-card", "dots",
]

start = time.time()
things_to_add_in_multiple_of_n = [
    # Bullet-like Symbols
    '•', '○', '●', '▪', '▫', '▲', '▼', '◇', '◆', '⁂',

    # List Indicators
    '*', '-', '–', '—', '~', '+', '>',

    # Separators/Dividers
    '_', '=', '/', '\\', '|', ':', ';',

    # Box-like Symbols
    '█', '▌', '▐', '▀', '▄',

    # Arrows
    '→', '←', '↑', '↓', '↔',

    # Punctuation Marks
    '.', ',', "'", '"', '!', '?',

    # Mathematical Symbols
    '±', '×', '÷', '∞', '≈',

    # Emojis and Miscellaneous
    '✔', '✖', '❤', '★', '☀', '⚫', '⚪'
]
for item in things_to_add_in_multiple_of_n:
    for i in range(30):
        valid_html_tags.append(f"{item*i}")



def get_similarity_ratio(str1, str2):
    """
    Returns the similarity ratio between two strings using difflib's SequenceMatcher.
    
    :param str1: First string to compare
    :param str2: Second string to compare
    :return: Similarity ratio as a float between 0.0 and 1.0
    """
    return SequenceMatcher(None, str1, str2).ratio()

def get_display_dimensions():
    # Get the primary monitor or the first monitor in the list
    monitor = get_monitors()[0]
    
    # Return width and height of the monitor
    return {"width": monitor.width, "height": monitor.height}

def get_all_alphabet_chars():
    alphabet = list(string.ascii_lowercase)
    return alphabet

def get_ram_percentage():
    return int(str(psutil.virtual_memory().percent).split(".")[0])

def ram_under_threshold(threshold):
    if get_ram_percentage() <= threshold:
        return True
    return False

def random_pause(n):
    # Generate a random float between 0 and n
    pause_time = random.uniform(0, n)
    
    # Pause the program for the generated random time
    time.sleep(pause_time)
    
    # Optional: Return the pause time if you want to track it
    return pause_time


def list_chrome_instances():
    chrome_processes = []
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == 'chrome.exe':
            chrome_processes.append(process.info)
    return chrome_processes

def kill_chrome_instances():
    '''NOTE: ASSUMES WINDOWS'''
    try:
        # Run the command to kill Chrome instances
        result = subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True, text=True, check=True)
        print(text="KILLED ALL CHROME INSTANCES", color='green')

    except subprocess.CalledProcessError as e:
        print(text=f"Command failed with return code {e.returncode}", color='red')
        print(text=f"Error output: {e.stderr}", color='red')
    except FileNotFoundError:
        print(text="The 'taskkill' command was not found. Is it available on your system?", color='red')
        
def kill_process_by_pid(pid):
    try:
        result = subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(text=f"Command failed with return code {e.returncode}", color='red')
        print(text=f"Error output: {e.stderr}", color='red')
    except FileNotFoundError:
         print(text="The 'taskkill' command was not found. Is it available on your system?", color='red')
    except Exception as e:   
        print(text=f"An error occurred while trying to kill process with PID: {pid} - {e}", color='red')
        
        
def generate_random_user_agent():
    # Define possible components for user agents
    os_list = [
        "Windows NT 10.0; Win64; x64",
        "Macintosh; Intel Mac OS X 10_15_7",
        "X11; Linux x86_64"
    ]
    
    browser_list = [
        ("Chrome/{version}", "AppleWebKit/537.36 (KHTML, like Gecko)"),
        ("Firefox/{version}", "Gecko/20100101"),
        ("Safari/{version}", "AppleWebKit/537.36 (KHTML, like Gecko) Version/{version}")
    ]
    
    # Define versions
    chrome_versions = [f"{major}.{minor}.{patch}.0" for major in range(90, 105) for minor in range(0, 100, 10) for patch in range(0, 5000, 100)]
    firefox_versions = [f"{major}.{minor}" for major in range(70, 100) for minor in range(0, 10)]
    safari_versions = [f"{major}.{minor}" for major in range(15, 18) for minor in range(0, 10)]
    
    versions = {
        'Chrome': chrome_versions,
        'Firefox': firefox_versions,
        'Safari': safari_versions
    }
    
    # Choose random components
    os = random.choice(os_list)
    browser_name, browser_template = random.choice(browser_list)
    version = random.choice(versions[browser_name.split('/')[0]])
    
    # Format the user-agent string
    user_agent = f"Mozilla/5.0 ({os}) {browser_template.format(version=version)}"
    
    return user_agent

def data_string_cleaner():
    '''THIS WILL BASICALLY GO THROUGH AND FIX SHIT THAT U WANT'''

import os
import csv

def load_us_cities():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'cities_us.csv')
    
    us_cities = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            us_cities.append({
                'city': row['city'],
                'city_ascii': row['city_ascii'],
                'state_id': row['state_id'],
                'state_name': row['state_name'],
                'county_fips': row['county_fips'],
                'county_name': row['county_name'],
                'lat': row['lat'],
                'lng': row['lng'],
                'population': row['population'],
                'density': row['density'],
                'source': row['source'],
                'military': row['military'],
                'incorporated': row['incorporated'],
                'timezone': row['timezone'],
                'ranking': row['ranking'],
                'zips': row['zips'].split(),
                'id': row['id']
            })
    
    return us_cities

def load_canadian_cities():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'cities_can.csv')
    
    canadian_cities = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            canadian_cities.append({
                'city': row['city'],
                'city_ascii': row['city_ascii'],
                'province_id': row['province_id'],
                'province_name': row['province_name'],
                'lat': row['lat'],
                'lng': row['lng'],
                'population': row['population'],
                'density': row['density'],
                'timezone': row['timezone'],
                'ranking': row['ranking'],
                'postal': row['postal'].split(),
                'id': row['id']
            })
    
    return canadian_cities

def get_country_by_city(city_name):
    us_cities = load_us_cities()
    canadian_cities = load_canadian_cities()
    
    for city in us_cities:
        if city['city'].lower() == city_name.lower():
            return 'United States'
    
    for city in canadian_cities:
        if city['city'].lower() == city_name.lower():
            return 'Canada'
    
    return 'City not found'

def is_html_tag_name2(string, verbose=False):
    """
    Check if a string is a valid HTML tag using BeautifulSoup.
    """
    soup = BeautifulSoup(f"<{string}></{string}>", "html.parser")
    result = soup.find(string) is not None
    #if verbose and not result:
    #    print(f"Flagged in: is_html_tag_name2")
    return result


class TagValidator(HTMLParser):
    """
    Validator using HTMLParser to ensure valid tags.
    """
    def __init__(self):
        super().__init__()
        self.valid_tags = set()

    def handle_starttag(self, tag, attrs):
        self.valid_tags.add(tag)


def is_html_tag_name3(string, verbose=False):
    """
    Check if a string is a valid HTML tag using html.parser.
    """
    parser = TagValidator()
    parser.feed(f"<{string}></{string}>")
    result = string in parser.valid_tags
    #if verbose and not result:
    #    print(f"Flagged in: is_html_tag_name3")
    return result


def is_html_tag_name4(string, verbose=False):
    """
    Check if a string is a valid HTML tag using lxml.
    """
    try:
        tree = fromstring(f"<{string}></{string}>")
        result = tree.tag == string
    except Exception:
        result = False
    #if verbose and not result:
    #    print(f"Flagged in: is_html_tag_name4")
    return result


def is_html_tag_name5(string, verbose=False):
    """
    Check if a string is a valid HTML tag using html5lib.
    """
    try:
        html = f"<{string}></{string}>"
        parsed = html5lib.parse(html, treebuilder="dom")
        result = True
    except Exception:
        result = False
    #if verbose and not result:
    #    print(f"Flagged in: is_html_tag_name5")
    return result


def full_html_tag_check(string, verbose=False):
    global valid_html_tags
    """
    Perform all checks for an HTML tag.
    """
    string = str(string)
    res = False
    if string in valid_html_tags:
        res = True

    #if string == "posting-title":
    #    print("res:", res , string)
    #    input("-")
    if res == True:
        return True

    checks = [
        ("is_html_tag_name2", is_html_tag_name2(string, verbose)),
        # ("is_html_tag_name", is_html_tag_name(string, verbose)),
        ("is_html_tag_name3", is_html_tag_name3(string, verbose)),
        ("is_html_tag_name4", is_html_tag_name4(string, verbose)),
        ("is_html_tag_name5", is_html_tag_name5(string, verbose))
    ]

    
    for check_name, result in checks:
        if not result:
            #if verbose:
            #    print(f"{string} failed at {check_name}")
            return False

    if verbose:
        print(f"{string} passed all checks")
    return True