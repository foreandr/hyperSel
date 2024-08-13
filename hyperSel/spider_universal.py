import random
import re
import playwright_utilites
import log_utilities
import colors_utilities
import asyncio

from urllib.parse import urlparse

async def start_crawler(crawl_struct):
    all_extracted_data, all_recursion_urls = await crawl_urls(crawl_struct)
    return all_extracted_data, all_recursion_urls

def extract_recursion_urls(soup, regex_pattern):
    html_content = str(soup)
    matching_urls = re.findall(regex_pattern, html_content)
    
    # Validate URLs
    valid_urls = []
    for url in matching_urls:
        parsed = urlparse(url)
        if all([parsed.scheme, parsed.netloc]):
            valid_urls.append(url)
    
    return list(set(valid_urls))

async def crawl_single_url(playwright, url, wanted_data_format, recursion_url_regex, headless, proxy, site_time_delay):
    soup = await playwright_utilites.playwright_get_soup_from_url(
        playwright=playwright,
        url=url, 
        headless=headless, 
        proxy=proxy,
        site_time_delay=site_time_delay,
    )
    recursion_urls = extract_recursion_urls(soup, recursion_url_regex)
    extracted_data = {}
    for data_type, config in wanted_data_format.items():
        for scraper in config.get("scrapers", []):
            func = scraper.get("function")
            args = scraper.get("args", {})
            args["soup"] = soup
            
            try:
                result = func(**args)
                if result:
                    if config.get("multiple"):
                        if data_type not in extracted_data:
                            extracted_data[data_type] = []
                        extracted_data[data_type].extend(result)
                    else:
                        extracted_data[data_type] = result
                        
            except Exception as e:
                colors_utilities.c_print(e, "red")
                pass
            
    return extracted_data, recursion_urls

async def crawl_urls(crawl_struct):
    headless = crawl_struct["headless"]
    proxy = crawl_struct["proxy"]
    playwright = await playwright_utilites.create_playwright(proxy=proxy)
    
    list_of_urls = crawl_struct['list_of_urls']
    wanted_data_format = crawl_struct['wanted_data_format']
    site_time_delay = crawl_struct['site_time_delay']
    # colors_utilities.c_print(wanted_data_format, "yellow")
    # log_utilities.log_function(wanted_data_format)
    
    recursion_url_regex = crawl_struct["recursion_url_regex"]
    
    if crawl_struct['random']:
        random.shuffle(list_of_urls)
    
    all_extracted_data = []
    all_recursion_urls = []
    for url in list_of_urls:
        try:
            extracted_data, recursion_urls = await crawl_single_url(playwright, url, wanted_data_format, recursion_url_regex, headless, proxy, site_time_delay)
            all_extracted_data.append(extracted_data)
            all_recursion_urls.extend(recursion_urls)
        except Exception as e:
            #print(f"=========================================================================================")
            colors_utilities.c_print(text=f"[url:{url}][e:{e}]", color='red')
            #input("STOP SOMETHING BROKE?")
            
    all_recursion_urls = list(set(filter(bool, all_recursion_urls)))
        
    await playwright_utilites.playwright_stop(playwright)
    return all_extracted_data, all_recursion_urls

async def continuous_crawl(
    list_of_urls,
    wanted_data_format,
    recursion_url_regex,
    num_threads=None,
    ram_cap=None,
    total_time=None,
    random=True,
    proxy=False,
    headless=True,
    max_recursions=None,
    site_time_delay=None
):
    crawl_struct = {
        "list_of_urls": list_of_urls,
        "num_threads": num_threads,
        "ram_cap": ram_cap,
        "wanted_data_format": wanted_data_format,
        "recursion_url_regex": recursion_url_regex,
        "total_time": total_time,
        "random": random,
        "proxy": proxy,
        "headless": headless,
        "site_time_delay":site_time_delay,
    }

    visited_urls = []  # To keep track of visited URLs
    recursion_count = 0  # Initialize recursion count

    while max_recursions is None or recursion_count < max_recursions:
        new_urls = []
        all_extracted_data, all_recursion_urls = await start_crawler(crawl_struct)
        for url in all_recursion_urls:
            print(f"all_recursion_urls: {url}")
            
            if url in visited_urls:
                print("1")
                continue
            elif url in list_of_urls:
                print("2")
                continue
            else:
                print("3")
                visited_urls.append(url)
                new_urls.append(url)
            print("*"*10)

        for url in new_urls:
            print("new_urls:", url)

        if not new_urls or len(new_urls) == 0:
            colors_utilities.c_print(text="No new URLs found, crawler will continue to wait for new ones", color="magenta")
            break
            await asyncio.sleep(10)  # Sleep to avoid tight loops when no new URLs are found
            continue
        
        # Update the crawl_struct with the new URLs
        crawl_struct["list_of_urls"] = new_urls
        
        # RESET THE SOUP
        for key, value in crawl_struct["wanted_data_format"].items():
            for scraper in value["scrapers"]:
                if "args" in scraper and "soup" in scraper["args"]:
                    scraper["args"]["soup"] = None
            
        for key, item in crawl_struct.items():
            log_utilities.log_function(f"[{key}]:{item}")
        
        # input("ANOTHER LOOP")

        recursion_count += 1  # Increment recursion count

    colors_utilities.c_print(f"Reached maximum recursions ({max_recursions}) or no more new URLs.", color='green')

if __name__ == "__main__":
    pass
