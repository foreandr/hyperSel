import time
import os
import random
import csv
from datetime import datetime

try:
    from . import log as log
    from . import parser as parser
    from . import instance as instance
except:

    import log as log
    import parser as parser
    import instance as instance


# 📁 Create a directory for storing screenshots
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)  # Ensure directory exists

def write_to_csv_with_timestamp(data, filename):
    """
    Appends a 2D list (list of lists) to a CSV file, adding a timestamp as the last column.
    Strips whitespace, replaces newlines with spaces, and ensures consistent formatting.
    """
    with open(filename, mode="a", newline="", encoding="utf-8") as file:  # Use 'a' to append instead of 'w'
        writer = csv.writer(file)
        
        for row in data:
            cleaned_row = []
            for item in row:
                if isinstance(item, str):
                    cleaned_item = item.strip().replace("\n", " ").replace("\r", " ")
                else:
                    cleaned_item = item
                cleaned_row.append(cleaned_item)
            
            # Append timestamp as the last column
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cleaned_row.append(timestamp)
            
            writer.writerow(cleaned_row)
    
    print(f"Data appended to {filename}")


if __name__ == "__main__":
    

    '''
    FOR THE DEFAULT PROFILE GOTTA SPEND SOME TIME FIGURING OUT
    HOW TO GET THAT CHROME CONTENT INTO FIREFOX,
     THEN I CAN SAY IF CHROME RUNNING TO FIREFOX AND VICE VERSA
    
    '''
    time_windows = [
        "120_160",
    ]
    iterations = 0
    cities = ["toronto-on", "peterborough-on", "london-on", "kingston-on"]
    browser = instance.Browser(
                    driver_choice="selenium", 
                    headless=True,
                    use_tor=False,
                    default_profile=False,
                    zoom_level=20
                    )

    for city in cities:
        for time_tuple in time_windows:
            path_tuple_pairs = time_tuple.split("_")
            min_sleep = int(path_tuple_pairs[0])
            max_sleep = int(path_tuple_pairs[1])
            sleep_time = random.uniform(min_sleep, max_sleep)

            local_iteration = 0
            while local_iteration <= 25:
                os.makedirs(os.path.join(SCREENSHOT_DIR, str(time_tuple), str(iterations)), exist_ok=True)
                screenshot_path = os.path.join(os.path.join(SCREENSHOT_DIR, str(time_tuple), str(iterations)), f"screenshot_{local_iteration}.png")

                browser.init_browser()
                url = f"https://www.zillow.com/{city}/{local_iteration}_p/"
                browser.go_to_site(url)
                time.sleep(2)
                
                soup = browser.return_current_soup()

                if len(str(soup)) < 20000:
                    time.sleep(sleep_time)
                    browser.close_browser()
                    continue

                data = parser.main(soup)
                write_to_csv_with_timestamp(data, filename="./TEST_DATA1")
                
                browser.take_screenshot(screenshot_path)
                browser.close_browser()

                time.sleep(sleep_time)
                local_iteration +=1

        iterations+=1
