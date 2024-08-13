import asyncio
import soup_utilities
import spider_universal
print("TODO: ALLOW MULTIPLE REGEX PATTERNS FOR RECURSION")

def t1():
    list_of_urls = [
        #'https://toronto.craigslist.org/tor/cto/d/downtown-toronto-1967-lincoln/7770117042.html',
        'https://toronto.craigslist.org/bra/cto/7773425815.html',
        'https://toronto.craigslist.org/tor/cto/7773356438.html',
        'https://toronto.craigslist.org/tor/cto/7773245516.html',
        'https://toronto.craigslist.org/tor/cto/7773269087.html',
        'https://toronto.craigslist.org/tor/cto/7773219905.html',
        'https://toronto.craigslist.org/tor/cto/7773171241.html',
    ]
    
    wanted_data_format = {
        'title': {
            "scrapers": [
                {"function": soup_utilities.get_text_by_id, "args": {"soup": None, "tag": "span", "id_name": "titletextonly"}}
            ],
            "multiple": False,
            "needed": True
        },
        'year': {
            "scrapers": [
                {"function": soup_utilities.get_text_by_id, "args": {"soup": None, "tag": "span", "id_name": "titletextonly", "regex_pattern": r'\b(\d{4})\b'}},
                {"function": soup_utilities.get_text_by_tag_and_class, "args": {"soup": None, "tag": "span", "class_name": "valu year"}}
            ],
            "multiple": False,
            "needed": True
        },
        'price': {
            "scrapers": [
                {"function": soup_utilities.get_text_by_tag_and_class, "args": {"soup": None, "tag": "span", "class_name": "price", "single": True, "regex_pattern": r'[^\d.]'}}
            ],
            "multiple": False,
            "needed": True
        },
        'images': {
            "scrapers": [
                {"function": soup_utilities.get_regex_items_from_soup, "args": {"soup": None, "single": False, "regex_pattern": r'<img[^>]+src=["\'](https?://[^"\']+)["\']'}}
            ],
            "multiple": True,
            "needed": False
        }
    }
    
    recursion_url_regex = r'https?://(?:www\.)?[\w.-]+(?:\.[a-zA-Z]{2,})+(?:/[\w./-]*)?\.html(?![^"]*/localStorage)'

    asyncio.run(
        spider_universal.continuous_crawl(
            list_of_urls=list_of_urls,
            wanted_data_format=wanted_data_format,
            recursion_url_regex=recursion_url_regex,
            num_threads=None,
            ram_cap=None,
            total_time=None,
            random=True,
            proxy=False,
            headless=True,
            max_recursions=3,
            site_time_delay=3,
        )
    )

def t2():
    list_of_urls = [
        'https://www.zillow.com/homedetails/30154106_zpid',
        'https://www.zillow.com/homedetails/2055079760_zpid',
        'https://www.zillow.com/homedetails/2082409198_zpid',
        'https://www.zillow.com/homedetails/30258798_zpid',
        'https://www.zillow.com/homedetails/30398040_zpid',
        'https://www.zillow.com/homedetails/30400280_zpid',
    ]
    
    wanted_data_format = {
        'address': {
            "scrapers": [
                {"function": soup_utilities.get_text_by_tag_and_class, "args": {"soup": None, "tag": "h1", "class_name": "Text-c11n-8-99-3__sc-aiai24-0 dFxMdJ"}},
                {"function": soup_utilities.get_text_by_tag_and_class, "args": {"soup": None, "tag": "h1", "class_name": "Text-c11n-8-100-2__sc-aiai24-0 bSfDch"}}
            ],
            "multiple": False,
            "needed": True
        },
    }
    
    recursion_url_regex = r'(\d+)_zpid'

    asyncio.run(
        spider_universal.continuous_crawl(
            list_of_urls=list_of_urls,
            wanted_data_format=wanted_data_format,
            recursion_url_regex=recursion_url_regex,
            max_recursions=2,
            site_time_delay=1,
            headless=False,
            proxy=True,
        )
    )
    
def t3():
    list_of_urls = [
        # "https://www.zillow.com/homedetails/175-Brockmoore-Dr-East-Amherst-NY-14051/30238291_zpid/",
        "https://snse.ca/",
        "https://snse.ca/",
        "https://snse.ca/",
        "https://snse.ca/",
        "https://snse.ca/",
        "https://snse.ca/",
        "https://snse.ca/",
        "https://snse.ca/",
        "https://snse.ca/",
        "https://snse.ca/",
        "https://snse.ca/",
        "https://snse.ca/",
        "https://snse.ca/",
        "https://snse.ca/",
        "https://snse.ca/",
        "https://snse.ca/",
        
        #'https://snse.ca/',
        #'https://realestate.snse.ca/',
        #'https://jailpdftocsv.snse.ca/',
        #'https://snse.ca/',
        #'https://realestate.snse.ca/',
        #'https://jailpdftocsv.snse.ca/',
        #'https://snse.ca/',
        #'https://realestate.snse.ca/',
        # 'https://jailpdftocsv.snse.ca/',
        
        
    ]
    
    wanted_data_format = {
        'address': {
            "scrapers": [
                {"function": soup_utilities.get_text_by_tag_and_class, "args": {"soup": None, "tag": "h1", "class_name": "Text-c11n-8-99-3__sc-aiai24-0 dFxMdJ"}},
            ],
            "multiple": False,
            "needed": True
        },
    }
    
    recursion_url_regex = r''

    asyncio.run(
        spider_universal.continuous_crawl(
            list_of_urls=list_of_urls,
            wanted_data_format=wanted_data_format,
            recursion_url_regex=recursion_url_regex,
            max_recursions=1,
            site_time_delay=20,
            headless=False,
            proxy=True,
            stealthy=False,
            
        )
    )
    

def run_tests():
    # t2()
    t3()

if __name__ == "__main__":
    run_tests()
