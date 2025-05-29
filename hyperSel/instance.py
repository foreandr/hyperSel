import os
import re
import gc
import time
import socket
import asyncio
from subprocess import Popen
import atexit
import nodriver as nd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# print("🧠 ChromeDriver path:", ChromeDriverManager().install())
from selenium.webdriver.chrome.options import Options

try:
    from . import tor_chrome_util as tor_chrome_util
    from . import util as util
    from . import log as log
except:
    import tor_chrome_util as tor_chrome_util
    import util as util
    import log as log

'''TODO
ALL THESE VARS SHOUDL BE LISTS, AND WE WILL ASSIGN AN INDEX TO EACH browser
CUZ I MAY WANT 5 OF THESE OPEN

I NEED GETTERS AND SETTERS FOR THE PARAMS
'''

class Browser:
    def __init__(
            self, 
            driver_choice="selenium", 
            headless=False, use_tor=False, 
            default_profile=False, 
            zoom_level=20, 
            port=9222
        ):
        if use_tor:
            print("TOR INIT")
            tor_chrome_util.start_tor()

        valid_drivers = {'selenium', 'nodriver', 'playwright'}
        if driver_choice not in valid_drivers:
            raise ValueError(f"Invalid driver choice. Must be one of {valid_drivers}.")
        
        self.driver_choice = driver_choice
        self.headless = bool(headless)
        self.use_tor = bool(use_tor)
        self.default_profile = default_profile
        self.zoom_level = zoom_level
        self.port = port
        self.WEBDRIVER = None
        self.PID = None

    def find_chrome_path(self):
        """Find the Chrome executable path."""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        raise FileNotFoundError("Chrome executable not found. Please install Google Chrome or specify the path manually.")

    def is_port_in_use(self):
        """Check if a port is already in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", self.port)) == 0

    def start_chrome_with_default_profile(self):
        """Start Chrome with the Default profile and remote debugging port."""
        try:
            # Ensure Chrome executable is found
            chrome_path = self.find_chrome_path()
            profile_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")  # Parent directory of profiles

            # Check if the port is already in use
            if self.is_port_in_use(self.port):
                print(f"Port {self.port} is already in use. Assuming Chrome is already running.")
                return  # Do not start a new Chrome instance

            # Command to start Chrome
            cmd = [
                chrome_path,
                f"--remote-debugging-port={self.port}",
                f"--user-data-dir={profile_path}",
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
            ]

            # Add Tor proxy logic if enabled
            if self.use_tor:
                print("Routing Chrome through Tor...")
                cmd.append("--proxy-server=socks5://127.0.0.1:9050")

            print(f"Starting Chrome with Default profile: {cmd}")
            Popen(cmd)
            time.sleep(5)  # Allow Chrome to start
            
        except Exception as e:
            print(f"Error starting Chrome: {e}")
            raise

    def connect_to_chrome(self):
        """Use Selenium to connect to Chrome running on the specified port."""
        try:
            options = Options()
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.port}")
            driver = webdriver.Chrome(service=Service(), options=options)
            return driver
        except Exception as e:
            print(f"Error connecting to Chrome: {e}")
            input("------------")
            raise

    def open_site_selenium(self):
        """Open a Selenium driver with anti-detection measures."""
        options = Options()

        if self.headless:
            options.add_argument("--headless")

        # User-agent spoofing
        options.add_argument(f"--user-agent={util.generate_random_user_agent()}")

    # Anti-bot and stealth
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--incognito")
        options.add_argument("--disable-3d-apis")

        # Use Tor if needed
        if self.use_tor:
            print("Routing requests through Tor...")
            options.add_argument("--proxy-server=socks5://127.0.0.1:9050")

        # Suppress logs
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        # Spoof DNS if needed
        options.add_argument("--host-resolver-rules=MAP aa.online-metrix.net 127.0.0.1")

        # Scale for screen emulation
        scale_factor = self.zoom_level / 100.0
        options.add_argument(f"--force-device-scale-factor={scale_factor}")

        # Maximize to seem human
        options.add_argument("--start-maximized")

        # ✅ SAFELY locate the correct chromedriver.exe
        raw_path = ChromeDriverManager().install()
        driver_folder = os.path.dirname(raw_path)
        driver_path = os.path.join(driver_folder, "chromedriver.exe")
        print(f"👉 Using ChromeDriver at: {driver_path}")

        service = Service(executable_path=driver_path)

        driver = webdriver.Chrome(service=service, options=options)
        self.PID = service.process.pid if service.process else None
        return driver


    def init_browser(self):
        if self.driver_choice == 'selenium':
            if self.default_profile:
                log.print_colored(text="STARTING WITH IN BUILT CHROME", color="red")
                try:
                    log.checkpoint()
                    # Attempt to start Chrome with the Default profile
                    self.start_chrome_with_default_profile()
                    log.checkpoint()
                    self.WEBDRIVER = self.connect_to_chrome()
                    log.checkpoint()
                    input("stop here and check")
                except Exception as e:
                    log.print_colored(text="ERROR FAILURE", color="red")
                    log.checkpoint(pause=True)

                    print(f"Failed to connect to local Chrome instance: {e}")
                    print("Falling back to a fresh Selenium session...")
                    self.WEBDRIVER = self.open_site_selenium()
            else:
                print("Default profile disabled. Starting fresh Selenium session...")
                self.WEBDRIVER = self.open_site_selenium()

            self.WEBDRIVER.maximize_window()

        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")
    
    def sniff_site(self, url):
        # Function to check if the URL matches any of the skip patterns
        def should_skip(url, skip_patterns):
            for pattern in skip_patterns:
                if re.search(pattern, url):
                    return True
            return False

        # Function to check if the response is JSON
        def is_json(response):
            content_type = response.headers.get("content-type", "")
            return "application/json" in content_type

        def playwright_network_capture(url, wait_time):
            requests = []
            # Add patterns to skip (regex-friendly)
            skip_patterns = [
                r'\.png', r'\.jpg', r'\.css', r'\.webp', r'\.js', r'ads', r'google', r'jsdata'
            ]
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()

                # Intercept network requests and responses
                page.on("response", lambda response: requests.append(response.url) 
                        if is_json(response) and not should_skip(response.url, skip_patterns) else None)

                page.goto(url)
                time.sleep(wait_time)
                try:
                    page.wait_for_load_state('networkidle')  # Ensures all network requests finish
                except Exception as e:
                    pass
                browser.close()

            return requests  # Return the list of URLs instead of logging

            
        def main(url, wait_time=5):
            captured_urls = playwright_network_capture(url, wait_time)
            
            # Print each URL one by one
            for request_url in captured_urls:
                print(request_url)

            return captured_urls

        return main(url)
    
    def close_browser(self):
        if self.driver_choice == 'selenium':
            try:
                self.WEBDRIVER.quit()
                self.WEBDRIVER = None
                gc.collect()
            except Exception as e:
                print(f"Error closing Selenium browser: {e}")

        elif self.driver_choice == 'playwright':
            print("GETTING HERE?")
            gc.collect()

        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")
        
    def get_many_elements_by_xpath(self, xpath,time=10):
        if self.driver_choice == 'selenium':
            try:
                # Wait for the elements to be present and visible
                elements = WebDriverWait(self.WEBDRIVER, time).until(
                    EC.presence_of_all_elements_located((By.XPATH, xpath))
                )
                return elements
            except Exception as e:
                print(f"Elements not found or couldn't be interacted with: {e}")
                return []
            
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")
        
    def get_many_elements_by_css_selector(self, css_selector,time=10):
        if self.driver_choice == 'selenium':
            try:
                # Wait for the elements to be present and visible
                elements = WebDriverWait(self.WEBDRIVER, time).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
                )
                return elements
            except Exception as e:
                print(f"Elements not found or couldn't be interacted with: {e}")
                return []
            
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")
    
    def get_many_elements_by_class(self, class_name,time=10):
        if self.driver_choice == 'selenium':
            try:
                # Wait for the elements to be present and visible
                elements = WebDriverWait(self.WEBDRIVER, time).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, class_name))
                )
                return elements
            except Exception as e:
                print(f"Elements not found or couldn't be interacted with: {e}")
                return []
            
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def get_element_by_xpath(self, xpath, time=10):
        if self.driver_choice == 'selenium':
            element = WebDriverWait(self.WEBDRIVER, time).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            return element
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def get_element_by_class(self, class_name, time=10):
        if self.driver_choice == 'selenium':
            element = WebDriverWait(self.WEBDRIVER, time).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
            return element
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def get_element_by_id(self, element_id, time=10):
        if self.driver_choice == 'selenium':
            select_element = WebDriverWait(self.WEBDRIVER, time).until(EC.element_to_be_clickable((By.ID, element_id)))
            return select_element
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def get_element_by_css_selector(self, css_selector, condition="visible", time=10):
        if self.driver_choice == 'selenium':
            if condition == "visible":
                element = WebDriverWait(self.WEBDRIVER, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
            elif condition == "clickable":
                element = WebDriverWait(self.WEBDRIVER, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
            else:
                raise ValueError("Invalid condition. Use 'visible' or 'clickable'.")
            
            return element
        
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def get_element_by_css_class(self):
        if self.driver_choice == 'selenium':
            pass
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def get_multiple_elements(self):
        if self.driver_choice == 'selenium':
            pass
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def go_to_site(self, site):
        sleep_time = 2
        
        if self.driver_choice == 'selenium':
            self.WEBDRIVER.get(site)
            time.sleep(sleep_time)
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def clear_input_field_by_xpath(self, xpath, timeout=10):
        if self.driver_choice == 'selenium':
            try:
                # Wait for the input field to be present and visible
                input_field = WebDriverWait(self.WEBDRIVER, timeout).until(
                    EC.visibility_of_element_located((By.XPATH, xpath))
                )
                # Clear the input field
                input_field.clear()
                print(f"Input field cleared successfully at XPath: {xpath}")
            except Exception as e:
                print(f"Failed to clear the input field at XPath: {xpath}, Error: {e}")

        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def enter_text_into_input_field_by_xpath(self, xpath, content_to_enter, time=10):
        if self.driver_choice == 'selenium':
            input_field =  WebDriverWait(self.WEBDRIVER, time).until(EC.presence_of_element_located((By.XPATH, xpath)))
            input_field.clear()
            input_field.send_keys(content_to_enter)
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def enter_text_into_input_field_by_class(self, element_class, content_to_enter, time=10):
        if self.driver_choice == 'selenium':
            element = WebDriverWait(self.WEBDRIVER, time).until(EC.visibility_of_element_located((By.CLASS_NAME, element_class)))
            element.clear()  # Optional: Clear any existing content in the input field
            element.send_keys(content_to_enter)
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def click_button_by_xpath(self, xpath, time=10):
        if self.driver_choice == 'selenium':
            element = WebDriverWait(self.WEBDRIVER, time).until(EC.presence_of_element_located((By.XPATH, xpath)))
            element.click()
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")
    

    def click_button_by_tag(self, tag_name, time=10):
        if self.driver_choice == 'selenium':
            button = WebDriverWait(self.WEBDRIVER, time).until(EC.element_to_be_clickable((By.TAG_NAME, tag_name)))
            button.click()
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def click_button_by_class(self, class_name, time=10):
        if self.driver_choice == 'selenium':
            button = WebDriverWait(self.WEBDRIVER, time).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
            button.click()
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def click_button_by_id(self, button_id, time=10):
        if self.driver_choice == 'selenium':
            button = WebDriverWait(self.WEBDRIVER, time).until(EC.element_to_be_clickable((By.ID, button_id)))
            button.click()
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def scroll_to_bottom(self, time_between_scrolls=0.1):
        if self.driver_choice == 'selenium':
            height = self.WEBDRIVER.execute_script("return document.body.scrollHeight")
            while True:
                time.sleep(time_between_scrolls)  # Add a 1-second delay
                self.WEBDRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                new_height = self.WEBDRIVER.execute_script("return document.body.scrollHeight")
                if new_height == height:
                    break
                height = new_height

        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")
    
    def scroll_to_item_in_view(self, element):
        if self.driver_choice == 'selenium':
            self.WEBDRIVER.execute_script("arguments[0].scrollIntoView(true);", element)
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def scroll_n_times_or_to_bottom(self, num_scrolls, time_between_scrolls=0):
        if self.driver_choice == 'selenium':
            scroll_count = 0

            while scroll_count < num_scrolls:
                height = self.WEBDRIVER.execute_script("return document.body.scrollHeight")
                self.WEBDRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(time_between_scrolls)

                new_height = self.WEBDRIVER.execute_script("return document.body.scrollHeight")
                if new_height == height:
                    break

                scroll_count += 1
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def scroll_up_or_down_n_pixels(self):
        if self.driver_choice == 'selenium':
            pass
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def return_current_soup(self):
        if self.driver_choice == 'selenium':
            html = self.WEBDRIVER.page_source
            soup = BeautifulSoup(html, features="lxml")
            return soup
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def maximize_current_window(self):
        if self.driver_choice == 'selenium':
            if self.WEBDRIVER is None:
                raise RuntimeError("Webdriver is not initialized. Please ensure the browser is started.")
            try:
                self.WEBDRIVER.maximize_window()
            except Exception as e:
                print(f"Error maximizing the window: {e}", "red")
        elif self.driver_choice == 'playwright':
            # Placeholder for Playwright logic
            pass
        elif self.driver_choice == 'nodriver':
            # Placeholder for Nodriver logic
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def minimize_current_window(self):
        if self.driver_choice == 'selenium':
            try:
                self.WEBDRIVER.minimize_window()
            except Exception as e:
                print(e)

        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def take_screenshot(self, path="./pics.png"):
        if self.driver_choice == 'selenium':
            self.WEBDRIVER.save_screenshot(path)
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def __repr__(self):
        return (
            f"Browser(driver_choice='{self.driver_choice}', "
            f"headless={self.headless}, use_tor={self.use_tor})"
        )
    
# --- Ensure Cleanup on Script Exit ---
def cleanup():

    """Cleanup logic at script exit."""
    print("Script is exiting.")
    # util.close_process_by_pid(PID)

    #try:
    #    WEBDRIVER.quit() # DIDINT INIT THE CHROMEDRIVER
    #except:
    #    pass

    gc.collect()

atexit.register(cleanup)

if __name__ == "__main__":
    
    pass