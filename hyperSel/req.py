import requests
from bs4 import BeautifulSoup

try:
    from . import util
except:
    import hyperSel.util as util

def get_soup(url, extra_headers=None, tor=False):
    """
    Fetch and parse a URL into a BeautifulSoup object, with optional Tor or proxy routing.
    """
    # Headers
    headers = {
        'user-agent': util.generate_random_user_agent(),
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    if extra_headers:
        headers.update(extra_headers)

    if tor:
        proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        print("Routing requests through Tor...")

    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.exceptions.RequestException as e:
        # Simplified error handling
        print(f"Error fetching URL: {e}")
        return None

if __name__ == '__main__':
    soup = get_soup(url='https://snse.ca/', tor=True)
    if soup:
        print("Page fetched successfully.")
    else:
        print("Failed to fetch the page.")
