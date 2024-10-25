import random
import re
from urllib.parse import urlparse
import asyncio
import sys
import time

print("need to be able  to say, DO THIS X THING  BEFORE RUNNING THE SCRAPER AND GETTING THE DATA GAIN, LIKE, CLICK THIS BUTTON, OR TRY TO EXIT THIS THING ")
print("FOR ABOVE I HAVE IN MIND, CLICK TO SCROLL, PORNHBU PAGINATION, WAIT 20S")
print("LAST PIECE OF intermediate functionality")
print("1: TURN ITSELF bakc on iff it erros")
print("2: intermediate scroll actions, ^^")
try:
    from . import playwright_utilites
    from . import colors_utilities
    from . import soup_utilities
    from . import log_utilities
    
except:
    import playwright_utilites
    import colors_utilities
    import soup_utilities
    import log_utilities

def extract_recursion_urls(soup, recursion_url_regex):
    html_content = str(soup)
    matching_urls = re.findall(recursion_url_regex, html_content)
    
    # Validate URLs
    valid_urls = []
    for url in matching_urls:
        parsed = urlparse(url)
        if all([parsed.scheme, parsed.netloc]):
            valid_urls.append(url)
    
    return list(set(valid_urls))

async def crawl_single_url(
    playwright, 
    url, 
    wanted_data_format, 
    recursion_url_regex, 
    headless=True, 
    proxy=False, 
    site_time_delay=10, 
    stealthy=None, 
    full_screen=False
):
    """
    Main function to crawl a single URL. This coordinates the crawling process.
    """
    # Step 1: Get the page content as soup (parsed HTML)
    soup = await playwright_utilites.playwright_get_soup_from_url(
        playwright=playwright,
        url=url,
        headless=headless,
        proxy=proxy,
        site_time_delay=site_time_delay,
        stealthy=stealthy,
        full_screen=full_screen,
    )

    # Step 2: Extract the URLs for recursion
    recursion_urls = extract_recursion_urls(soup, recursion_url_regex)

    # Step 3: Extract the required data using the scrapers
    extracted_data = run_scrapers(wanted_data_format, soup)

    # Step 4: add root url to data for clarity
    for i in extracted_data:
        i['root_url'] = url

    # Step 5: Return the extracted data and recursion URLs
    return extracted_data, recursion_urls

def get_root_soups(wanted_data_format, soup):
    """
    Function to get all the base HTML elements (root soups) from the root section.
    """
    root_soups = []  # List to hold the base HTML elements

    # Get the root section scrapers
    root_tag = wanted_data_format['root_section']
    root_scrapers = root_tag['scrapers']

    # Iterate over each scraper in the root section
    for scraper in root_scrapers:
        func = scraper['function']  # The scraper function
        args = scraper['args']  # The arguments for the scraper function
        args["soup"] = soup  # Set the main soup into the scraper arguments

        # Execute the scraper function with the provided arguments
        result = func(**args)
        
        # Add each result (root soup) to the list of root soups
        if result:
            for element in result:
                root_soups.append(element)

    return root_soups  # Return the list of root soups

def run_scrapers(wanted_data_format, soup):
    extracted_data = []

    try:
        root_soups = get_root_soups(wanted_data_format, soup)
    except Exception:
        # print("NULL ROOT SECTION")
        root_soups = [soup]

    for root_soup in root_soups:
        root_soup_data = process_sub_sections(root_soup, wanted_data_format)
        extracted_data.append(root_soup_data)   

    return extracted_data

def single_crawl_sub_section(root_soup, var_scraper):
    scrapers = var_scraper['scrapers']
    final_result = None
    for scraper in scrapers:
        scraper['args']['soup'] = root_soup
        func = scraper["function"]
        args = scraper["args"]
        result = func(**args)
        if result != None:
            final_result = result

    return final_result
    
def process_sub_sections(root_soup, wanted_data_format):
    """
    Function to process a single root_soup and return the extracted data in a flat dictionary format.
    
    Example Output:
    {
        "title": "Title of the Episode",
        "root_url": "https://podcasts.apple.com/us/podcast/lex-fridman-podcast/id1434243584"
    }
    """
    # Define the result as a flat dictionary
    root_soup_data = {}

    # Loop through each entry in the wanted data format
    for var_name, var_scraper in wanted_data_format['sub_sections'].items():
        result_data = single_crawl_sub_section(root_soup, var_scraper)
        
        # Add to the dictionary directly with var_name as key
        root_soup_data[var_name] = result_data

    return root_soup_data

async def crawl_urls(crawl_struct):
    headless = crawl_struct["headless"]
    proxy = crawl_struct["proxy"]
    playwright = await playwright_utilites.create_playwright(proxy=proxy)
    list_of_urls = crawl_struct['list_of_urls']
    wanted_data_format = crawl_struct['wanted_data_format']
    site_time_delay = crawl_struct['site_time_delay']
    recursion_url_regex = crawl_struct["recursion_url_regex"]
    stealthy = crawl_struct["stealthy"]
    num_threads = crawl_struct["num_threads"]
    
    full_screen = crawl_struct["full_screen"]
   
    random.shuffle(list_of_urls) if crawl_struct.get('random') else None
    
    all_extracted_data = []
    all_recursion_urls = []
    for url in list_of_urls:
        try:
            extracted_data, recursion_urls = await crawl_single_url(
                playwright, 
                url, 
                wanted_data_format, 
                recursion_url_regex, 
                headless, 
                proxy, 
                site_time_delay,
                stealthy,
                full_screen,
                
                )
   

            all_extracted_data.extend(extracted_data)
            all_recursion_urls.extend(recursion_urls)
        except Exception as e:
            colors_utilities.c_print(text=f"[url:{url}][e:{e}]", color='red')
            
    all_recursion_urls = list(set(filter(bool, all_recursion_urls)))
    await playwright_utilites.playwright_stop(playwright)
    return all_extracted_data, list(set(all_recursion_urls))

async def continuous_crawl(
    list_of_urls,
    wanted_data_format,
    recursion_url_regex,
    num_threads=None,
    ram_cap=None,
    total_time=None,
    random=False,
    proxy=False,
    headless=True,
    max_recursions=None,
    max_time=None,
    site_time_delay=None,
    stealthy=None,
    full_screen=True,
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
        "stealthy":stealthy,
        "full_screen":full_screen,
    }

    visited_urls = []  # To keep track of visited URLs
    visited_urls.extend(list_of_urls) # add the root urls

    all_crawled_data = []
    recursion_count = 0  # Initialize recursion count
    start = time.time()
    iters = 0 
    while (max_recursions is None) or (recursion_count < max_recursions):
        print("ITER", iters)
        iters +=1


        if (time.time()-start > max_time):
            print("MAX TIME HIT BREAK")
            break

        if max_recursions != None:
            print("recursion_count:", recursion_count)
        
        new_urls = []
        all_extracted_data, all_recursion_urls = await crawl_urls(crawl_struct)
        all_crawled_data.extend(all_extracted_data)
        
        for url in all_recursion_urls:
            if url not in visited_urls:
                new_urls.append(url)
            visited_urls.append(url)

        # REPLACE OLD URLS WITH NEW URLS
        crawl_struct["list_of_urls"] = new_urls

        recursion_count += 1  # Increment recursion count
        if len(new_urls) == 0:
            break
        
    cleaned_data = clean_crawled_data(all_crawled_data)
    log_utilities.log_data(cleaned_data, file_name='data.json')
    colors_utilities.c_print(f"Reached maximum recursions (MAX={max_recursions}) or no more new URLs. Or time threshold ({time.time()-start})", color='green')

def clean_single_item(data):
    """
    Cleans each string in the input data dictionary by replacing or removing 
    non-ASCII characters.
    
    :param data: Dictionary containing the data to clean.
    :return: A cleaned dictionary with normalized ASCII text.
    """
    def normalize_text(value):
        """Normalize non-ASCII characters to ASCII equivalents or remove them."""
        replacements = {
            "\u2013": "-",  # En dash to ASCII hyphen
            "\u2014": "-",  # Em dash to ASCII hyphen
            "\u2018": "'",  # Left single quote to ASCII single quote
            "\u2019": "'",  # Right single quote to ASCII single quote
            "\u201c": '"',  # Left double quote to ASCII double quote
            "\u201d": '"',  # Right double quote to ASCII double quote
            "\xa0": " ",    # Non-breaking space to regular space
            "\n": " ",      # Newline to space
            "\t": " "       # Tab to space
        }
        
        # Replace known non-ASCII characters
        for char, replacement in replacements.items():
            value = value.replace(char, replacement)
        
        # Remove any remaining non-ASCII characters
        value = ''.join([ch if ord(ch) < 128 else '' for ch in value])
        
        return value.strip()

    # Initialize a single cleaned dictionary
    cleaned_data = {}
    
    # Loop through each key-value pair in the data dictionary
    for key, value in data.items():
        if isinstance(value, str):
            value = normalize_text(value)
        cleaned_data[key] = value

    return cleaned_data

def clean_crawled_data(all_data_raw):
    # print("all_data_raw:", all_data_raw)
    cleaned_data = []
    for data in all_data_raw:

        cleaned_data.append(clean_single_item(data))
    return cleaned_data

def create_scraping_config(fields):
    """
    Generates a scraping configuration dictionary, including a root_section field.
    
    Parameters:
    - fields: A dictionary where each key is a field name, including "root_section" as the root field.
      Each field value is a dictionary containing:
        - "function": The scraping function.
        - "args": Arguments dictionary to pass to the function.
        - "multiple": Whether multiple values are expected (bool).
        - "needed": Whether this field is required (bool).

    Returns:
    - A dictionary formatted as a scraping configuration.
    """
    # Initialize configuration with a sub_sections section
    scraping_config = {
        'sub_sections': {}
    }
    
    # Extract the root field and populate the root section
    root_field = fields.get("root_section")
    if root_field:
        scraping_config['root_section'] = {
            "scrapers": [
                {
                    "function": root_field["function"],
                    "args": root_field["args"]
                }
            ]
        }
    else:
        scraping_config['root_section'] = None

    # Populate sub_sections with other fields (excluding "root")
    for field_name, field_data in fields.items():
        if field_name == "root_section":
            continue
        scraping_config['sub_sections'][field_name] = {
            "scrapers": [
                {
                    "function": field_data["function"],
                    "args": field_data["args"]
                }
            ],
            "multiple": field_data.get("multiple", False),
            "needed": field_data.get("needed", False)
        }
    
    return scraping_config

def create_field_config(name, function, soup=None, tag=None, selector_name=None, single=True, 
                        index=None, regex_pattern=None, multiple=False, needed=False, **extra_args):
    """
    Generates a configuration dictionary for a specific field.
    
    Parameters:
    - name (str): The name of the field (e.g., "title", "description", "url").
    - function (function): The scraping function to use for this field.
    - soup: The soup object or None, to be passed to the scraping function.
    - tag (str): The HTML tag to search for (e.g., "span", "a").
    - selector_name (str): The class name of the HTML tag to match.
    - single (bool): Whether to scrape a single element or multiple (default: True).
    - index (int): Index of the element to select if multiple elements are found (default: None).
    - regex_pattern (str): Regex pattern for filtering text (default: None).
    - multiple (bool): Whether the field is expected to have multiple values (default: False).
    - needed (bool): Whether the field is required (default: False).
    - **extra_args: Any additional arguments for the function.

    Returns:
    - A dictionary for the field configuration.
    """
    return {
        f"{name}":{
            "function": function,
            "args": {
                "soup": soup,
                "tag": tag,
                "selector_name": selector_name,
                "single": single,
                "index": index,
                "regex_pattern": regex_pattern,
                **extra_args  # Include any other extra arguments
            },
            "multiple": multiple,
            "needed": needed
        }
    }

# Assuming `continuous_crawl`, `create_scraping_config`, and `soup_utilities` are imported

def crawl(list_of_urls, field_configs, recursion_url_regex, max_recursions=1, max_time=None, site_time_delay=8, headless=False):
    """
    Main crawl function that abstracts crawling logic.
    
    Arguments:
    - list_of_urls: List of URLs to start the crawling from.
    - field_configs: A dictionary of field configurations (how to extract data).
    - recursion_url_regex: Regex pattern for finding URLs to recurse into.
    - max_recursions: Maximum recursion depth for crawling.
    - site_time_delay: Delay between requests to avoid overwhelming the server.
    - headless: Boolean to run in headless browser mode (if using a browser for crawling).
    
    This function handles everything else.
    """
    # Convert field configs to the format needed by the scraper
    config = create_scraping_config(field_configs)

    # Internal function to run the crawl and handle Ctrl+C
    def run_crawler():
        try:
            asyncio.run(
                continuous_crawl(
                    list_of_urls=list_of_urls,
                    wanted_data_format=config,
                    recursion_url_regex=recursion_url_regex,
                    max_recursions=max_recursions,
                    max_time=max_time,
                    site_time_delay=site_time_delay,
                    headless=headless,
                )
            )
        except KeyboardInterrupt:
            print("\nCtrl+C detected.")
            user_input = input("Do you want to stop the program? (y/n): ").lower()
            if user_input == 'y':
                print("Exiting the program.")
                sys.exit(0)  # Exit the program
            else:
                print("Resuming crawling...")
                run_crawler()

    # Start the crawl
    run_crawler()

# Example user-provided field configurations
def main():
    # Example URLs (can be more dynamic in a real-world scenario)
    list_of_urls = [
        "https://podcasts.apple.com/us/podcast/lex-fridman-podcast/id1434243584",
        "https://podcasts.apple.com/us/podcast/modern-wisdom/id1347973549",
        "https://podcasts.apple.com/us/podcast/the-tim-ferriss-show/id863897795",

    ]
    
    # USER-DEFINED FIELD CONFIGURATIONS
    
    root_config = create_field_config(
        name="root_section",
        function=soup_utilities.get_full_soup_by_tag_and_class,
        tag="li",
        selector_name="svelte-8rlk6b",
        single=False
    )
    

    title_config = create_field_config(
        name="title",
        function=soup_utilities.get_text_by_tag_and_class,
        tag="span",
        selector_name="episode-details__title-text"
    )

    description_config = create_field_config(
        name="description",
        function=soup_utilities.get_text_by_tag_and_class,
        tag="span",
        selector_name="multiline-clamp__text svelte-73d2pa",
        single=False,
        index=1
    )

    url_config = create_field_config(
        name="url",
        function=soup_utilities.get_href_by_tag_and_class,
        tag="a",
        selector_name="link-action svelte-1wtdvjb",
        needed=True
    )

    # Combine all user-defined field configs
    # 
    field_configs = {**root_config, **title_config, **description_config, **url_config}
    
    # Recursion regex pattern
    recursion_url_regex = r'https:\/\/podcasts\.apple\.com\/[a-z]{2}\/podcast\/[a-zA-Z\-]+\/id\d+'

    # Call the crawl function, passing the user-defined fields and options
    crawl(
        list_of_urls=list_of_urls,
        field_configs=field_configs,
        recursion_url_regex=recursion_url_regex,
        max_recursions=3,
        max_time=30,
        site_time_delay=8,
        headless=False,
    )

if __name__ == "__main__":
    main()