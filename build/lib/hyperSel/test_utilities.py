import soup_utilities
import asyncio
import spider_universal

def t1():
    list_of_urls = [
        'https://toronto.craigslist.org/tor/cto/d/downtown-toronto-1967-lincoln/7770117042.html',
        'https://toronto.craigslist.org/bra/cto/7773425815.html',
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
    
    recrusion_url_structure = ''
    crawl_struct = {
        "list_of_urls": list_of_urls,
        "num_threads": None,
        "ram_cap": None,
        "wanted_data_format": wanted_data_format,
        "recrusion_url_structure": recrusion_url_structure,
        "total_time": None,
        "random": False
    }
    
    asyncio.run(spider_universal.start_crawler(crawl_struct))

def run_tests():
    t1()

if __name__ == "__main__":
    run_tests()