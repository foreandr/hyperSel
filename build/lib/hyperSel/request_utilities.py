import requests
import random
from bs4 import BeautifulSoup
import general_util

def get_soup(url):

    # Headers
    headers = {
        'User-Agent': general_util.generate_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None
    
if __name__ == '__main__':
    for i in range(100):
        get_soup(url='https://snse.ca/')