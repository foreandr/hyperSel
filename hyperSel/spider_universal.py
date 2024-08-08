import random
import re
import playwright_utilites
import soup_utilities
import asyncio

async def start_crawler(crawl_struct):
    new_urls = await crawl_urls(crawl_struct)
    return new_urls

async def crawl_single_url(playwright, url, wanted_data_format):
    soup = await playwright_utilites.playwright_get_soup_from_url(playwright, url, headlesss=True, proxy=False)
    extracted_data = {}
    
    for data_type, config in wanted_data_format.items():
        print("data_type", data_type)
        print("config", config)
        print("---")
        
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
                print(f"Error", e)
                print("data_type", data_type)
                print("config", config)
            
        print("*"*40)
    
    print("\n")
    print("Extracted Data for URL\n:", url, extracted_data)
    return extracted_data

async def crawl_urls(crawl_struct):
    print("Starting URL crawl with configuration:", crawl_struct)
    
    playwright = await playwright_utilites.create_playwright(using_proxies=False)
    # print("Playwright instance created")
    
    list_of_urls = crawl_struct['list_of_urls']
    wanted_data_format = crawl_struct['wanted_data_format']
    
    if crawl_struct['random']:
        # print("Shuffling URL list")
        random.shuffle(list_of_urls)
    
    all_extracted_data = []
    
    for url in list_of_urls:
        extracted_data = await crawl_single_url(playwright, url, wanted_data_format)
        all_extracted_data.append(extracted_data)
        # print("Data extracted from URL:", url, extracted_data)
        # Commented out to allow processing of all URLs
        break
    
    await playwright_utilites.playwright_stop(playwright)
    return all_extracted_data

if __name__ == "__main__":
    pass
