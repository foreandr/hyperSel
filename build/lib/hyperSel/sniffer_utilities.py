import re
from playwright.sync_api import sync_playwright
import time

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

def playwright_network_capture(url, wait_time):
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
        time.sleep(wait_time)
        try:
            page.wait_for_load_state('networkidle')  # Ensures all network requests finish
        except Exception as e:
            pass
        browser.close()

    return requests  # Return the list of URLs instead of logging

    
def main(url, wait_time=5):
    captured_urls = playwright_network_capture(url, wait_time)
    
    # Print each URL one by one
    for request_url in captured_urls:
        print(request_url)

    return captured_urls

if __name__ == "__main__":
    main("https://podcasts.apple.com/us/podcast/lex-fridman-podcast/id1434243584")
    pass