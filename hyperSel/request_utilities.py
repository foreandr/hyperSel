import requests
from bs4 import BeautifulSoup

try:
    from . import util
    from . import colors_utilities
    from . import tor_util
except:
    import hyperSel.util as util
    import colors_utilities
    import hyperSel.tor_util as tor_util

def get_soup(url, extra_headers=None, proxy=None):
    # Headers
    headers = {
        'user-agent': util.generate_random_user_agent(),
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    if extra_headers:
        for key, value in extra_headers.items():
            headers[key] = value

    # Proxy settings
    proxies = None
    if proxy:
        proxies = {
            'http': f'http://{proxy}',
            'https': f'https://{proxy}'
        }
    
    # Attempt requests
    max_attempts = 3
    attempt = 0
    
    for i in range(max_attempts):
        try:
            if proxies:
                # print(f"Attempting with proxy: {proxy} (Attempt {attempt + 1})")
                response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            else:
                # print(f"Attempting without proxy (Attempt {attempt + 1})")
                response = requests.get(url, headers=headers, timeout=10)
                
            response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            return soup

        except requests.exceptions.RequestException as e:
            # colors_utilities.c_print(text=f"Error fetching URL: {e}", color="red")
            attempt += 1
            if attempt >= max_attempts and proxies:
                # Retry without proxy if max attempts are reached with proxy
                proxies = None
                attempt = 0  # Reset attempt counter for the non-proxy request

    # Final fallback without proxy if proxy attempts fail
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    except requests.exceptions.RequestException as e:
        # colors_utilities.c_print(text=f"Final error fetching URL: {e}", color="red")
        return None
    
if __name__ == '__main__':
    get_soup(url='https://snse.ca/')