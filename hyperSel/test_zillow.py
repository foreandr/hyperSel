import time
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import parser
from bs4 import BeautifulSoup

try:

    from . import log as log
except:

    import log as log


# 📁 Create a directory for storing screenshots
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)  # Ensure directory exists

# 🔄 List of User-Agents for Rotation (Spoof Identity)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/537.36",
    "Mozilla/5.0 (Android 11; Mobile; rv:94.0) Gecko/94.0 Firefox/94.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36"
]

# 🚀 Function to Start and Return a New WebDriver Instance
def start_selenium(headless=True, zoom_level=100):
    """Launch a new Selenium WebDriver instance with a spoofed User-Agent and custom zoom level."""
    options = Options()

    # 🏳️ Headless Mode (default: True)
    if headless:
        options.add_argument("--headless")
        print("🎭 Running in headless mode (no UI).")

    # 🔄 Rotate and Spoof User-Agent
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"user-agent={user_agent}")

    # 🛑 Anti-Bot Detection Measures
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--incognito")  # Open in Incognito Mode

    # 🖥️ Start in Full-Screen Mode
    options.add_argument("--start-maximized")

    # 🧑‍💻 Adjust Zoom Level
    scale_factor = zoom_level / 100.0  # Convert percentage to scale factor
    options.add_argument(f"--force-device-scale-factor={scale_factor}")

    # ✅ Start a Fresh WebDriver Instance
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    print(f"🚀 New Selenium WebDriver started with User-Agent: {user_agent} and {zoom_level}% zoom")
    return driver


if __name__ == "__main__":
    time_windows = [
        "100_120",
    ]
    iterations = 0
    while True:
        for time_tuple in time_windows:
            path_tuple_pairs = time_tuple.split("_")

            # Convert string values to integers
            min_sleep = int(path_tuple_pairs[0])
            max_sleep = int(path_tuple_pairs[1])

            # Generate a random sleep time between min_sleep and max_sleep
            sleep_time = random.uniform(min_sleep, max_sleep)

            print("\npath_tuple_pairs:", path_tuple_pairs)

            for i in range(1, 25):  # Iterates Zillow pages
                os.makedirs(os.path.join(SCREENSHOT_DIR, str(time_tuple), str(iterations)), exist_ok=True)
                screenshot_path = os.path.join(os.path.join(SCREENSHOT_DIR, str(time_tuple), str(iterations)), f"screenshot_{i}.png")

                driver = start_selenium(headless=False, zoom_level=20)  # ✅ Start new WebDriver each loop
                url = f"https://www.zillow.com/toronto-on/{i}_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A{i}%7D%2C%22isMapVisible%22%3Atrue%7D"
                driver.get(url)
                time.sleep(2)
                
                soup = BeautifulSoup(driver.page_source, "html.parser")
                print("LEN SOUP:", len(str(soup)))
                # log.log_function(soup)

                if len(str(soup)) < 20000:
                    print("HIT A SKIPPER, GOING NEXT")
                    print("SLEEPING FIRST THO")
                    time.sleep(sleep_time)
                    driver.quit()  # 🚪 Fully close WebDriver before next loop
                    continue

                print("HIT A NROAML, CHEKCING PAGE")
                parser.main(soup, i=random.randint(20, 2000))
                input("---")

                
                
                driver.save_screenshot(screenshot_path)
                driver.quit()  # 🚪 Fully close WebDriver before next loop

                print("\nscreenshot_path:", screenshot_path)
                print("\nurl:", url)
                

                print("\n\nSLEEPING FOR:", sleep_time)
                time.sleep(sleep_time)
                input("--- STOP HERE")
            time.sleep(120)

        iterations+=1
'''
THIS WORKS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

CLOSE BROWSER EVERY TIME, SPOOF USER USER_AGENTS
TRRY WITH SWITCHING LOCATIONS,
GOTTA GET THE P2P WORKING
AND THEN WE CAN JUST SELL THE ZILLOW FOR NOW'
'''