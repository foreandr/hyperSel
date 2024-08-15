import re
from urllib.parse import urlparse,parse_qs
import json

def extract_url_properties(link):
    try:
        parsed_link = urlparse(link)
        domain_parts = parsed_link.netloc.split('.')
        
        if len(domain_parts) > 2:
            subdomain = '.'.join(domain_parts[:-2])
            domain = domain_parts[-2]
            tld = domain_parts[-1]
        else:
            subdomain = None
            domain = domain_parts[0]
            tld = domain_parts[1] if len(domain_parts) > 1 else None

        result = {
            "subdomain": subdomain,
            "domain": domain,
            "tld": tld
        }
        
        return json.dumps(result)
    except Exception as e:
        return None

def construct_foundation_url(url):
    try:
        data = json.loads(extract_url_properties(url))
        domain = data['domain']
        tld = data['tld']
        subdomain = data.get('subdomain')

        if subdomain:
            foundation_url = f"{subdomain}.{domain}.{tld}"
        else:
            foundation_url = f"{domain}.{tld}"

        return foundation_url
    except Exception as e:
        return None

def get_all_hrefs(soup):
    hrefs = []
    for link in soup.find_all('a'):
        try:
            href = link.get('href')
            hrefs.append(href)
        except Exception as e:
            continue
    return hrefs

def get_all_new_wanted_urls(soup, root_url):
    new_hrefs = get_all_hrefs(soup)
    urls = []
    for href in new_hrefs:
        urls.append(f"https://{construct_foundation_url(root_url)}.com{href}")
    return urls

if __name__ == "__main__":
    pass