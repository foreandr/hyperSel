import requests
from bs4 import BeautifulSoup

try:
    from . import util as util
    from . import log as log
except:
    import util as util
    import log as log

def get_soup(url, extra_headers=None, tor=False, soup_only=True):
    """
    Fetch and optionally parse a URL into a BeautifulSoup object, with optional Tor routing.

    Args:
        url (str): The URL to fetch.
        extra_headers (dict, optional): Additional headers to include.
        tor (bool): Whether to use Tor proxy.
        soup_only (bool): If True, return BeautifulSoup object. If False, return full response.

    Returns:
        BeautifulSoup | requests.Response | None
    """
    # Headers
    headers = {
        'user-agent': util.generate_random_user_agent(),
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    if extra_headers:
        headers.update(extra_headers)

    # Only set proxies if using Tor
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    } if tor else None

    try:
        response = requests.get(url, headers=headers, proxies=proxies if tor else None, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser') if soup_only else response
    except requests.exceptions.RequestException as e:
        return None

if __name__ == '__main__':
    result = get_soup(url='https://www.zillow.com/toronto-on/', tor=True, soup_only=True)
    log.log_function(result)
