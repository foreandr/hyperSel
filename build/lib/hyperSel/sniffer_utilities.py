import re
from playwright.sync_api import sync_playwright

try:
    from . import log_utilities
except:
    import log_utilities


'''
TODO:
1. it sniffs a thing
2. set params (searching for)
    where you go to the site ahead of time, eg(https://www.amazon.com/Notebooks-Laptop-Computers/b?ie=UTF8&node=565108)
    givethe keyword apple, it will go throgh the json and see apple,
    and then gfind out how ot go back up through the tree
    eg = {
        'content':{
            'data':{
                'title':laptop,
                'title':apple laptop,

            }
        }
    }

    so it will see apple, and then figure out to go to the top level where ALL the laptops are
'''

# Function to check if the URL matches any of the skip patterns
def should_skip(url, skip_patterns):
    for pattern in skip_patterns:
        if re.search(pattern, url):
            return True
    return False

# Function to check if the response is JSON
def is_json(response):
    content_type = response.headers.get("content-type", "")
    return "application/json" in content_type

def playwright_network_capture(url):
    requests = []
    # Add patterns to skip (regex-friendly)
    skip_patterns = [
        r'\.png', r'\.jpg', r'\.css', r'\.webp', r'\.js', r'ads', r'google', r'jsdata'
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Intercept network requests and responses
        page.on("response", lambda response: requests.append(response.url) 
                if is_json(response) and not should_skip(response.url, skip_patterns) else None)

        page.goto(url)
        page.wait_for_load_state('networkidle')  # Ensures all network requests finish
        browser.close()

    return requests  # Return the list of URLs instead of logging

def main(url):
    captured_urls = playwright_network_capture(url)
    
    # Print each URL one by one
    for request_url in captured_urls:
        print(request_url)

    return captured_urls

if __name__ == "__main__":
    main("https://podcasts.apple.com/us/podcast/lex-fridman-podcast/id1434243584")
    pass