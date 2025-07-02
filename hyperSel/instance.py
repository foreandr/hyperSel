import os
import re
import gc
import time
import socket
from subprocess import Popen, PIPE
import atexit
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from playwright.sync_api import sync_playwright

# Using webdriver_manager for ChromeDriverManager to handle driver installation
try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("webdriver_manager not found. Please install it: pip install webdriver-manager")
    ChromeDriverManager = None # Set to None if import fails, indicating it's unavailable


# Assuming these are local imports from your project structure
try:
    from . import tor_chrome_util as tor_chrome_util
    from . import util as util
    from . import log as log
except ImportError:
    import tor_chrome_util as tor_chrome_util
    import util as util
    import log as log

class Browser:
    def __init__(
        self,
        driver_choice="selenium",
        headless=False,
        use_tor=False,
        default_profile=False,
        zoom_level=20,
        port=9222,
        chrome_options: Options = None
    ):
        if use_tor:
            print("TOR INIT")
            tor_chrome_util.start_tor()

        valid_drivers = {'selenium', 'playwright'} 
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
        self.chrome_options = chrome_options
        self.chrome_process = None

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

    def is_port_in_use(self, port):
        """Check if a port is already in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) == 0

    def start_chrome_with_default_profile(self):
        """Start Chrome with the Default profile and remote debugging port."""
        # Note: This method retains its try-except because its an internal setup function
        # that might fail due to external system factors (port in use, chrome not found).
        # It's not a "scroller, clicker, getter" that should pass errors up.
        try:
            chrome_path = self.find_chrome_path()
            profile_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")

            if self.is_port_in_use(self.port):
                print(f"Port {self.port} is already in use. Assuming Chrome is already running.")
                return

            cmd = [
                chrome_path,
                f"--remote-debugging-port={self.port}",
                f"--user-data-dir={profile_path}",
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
            ]

            if self.use_tor:
                print("Routing Chrome through Tor...")
                cmd.append("--proxy-server=socks5://127.0.0.1:9050")

            print(f"Starting Chrome with Default profile via Popen: {cmd}")
            self.chrome_process = Popen(cmd, stdout=PIPE, stderr=PIPE)
            time.sleep(5)
            
        except Exception as e:
            print(f"Error starting Chrome with default profile: {e}")
            raise

    def connect_to_chrome(self):
        """Use Selenium to connect to Chrome running on the specified port."""
        # Note: This method retains its try-except as it's an internal connection helper.
        try:
            options_for_connection = Options()
            options_for_connection.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.port}")
            
            if ChromeDriverManager is None:
                raise RuntimeError("ChromeDriverManager is not available. Please install 'webdriver-manager'.")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options_for_connection)
            return driver
        except Exception as e:
            print(f"Error connecting to Chrome on port {self.port}: {e}")
            input("------------ (Error connecting to Chrome) ------------")
            raise

    def open_site_selenium(self):
        """
        Open a Selenium driver with anti-detection measures.
        Custom ChromeOptions passed to Browser.__init__ will be applied here.
        """
        options = self.chrome_options if self.chrome_options is not None else Options()

        if self.headless:
            options.add_argument("--headless=new")

        options.add_argument(f"--user-agent={util.generate_random_user_agent()}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--incognito")
        options.add_argument("--disable-3d-apis")

        if self.use_tor:
            print("Routing requests through Tor...")
            options.add_argument("--proxy-server=socks5://127.0.0.1:9050")

        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--host-resolver-rules=MAP aa.online-metrix.net 127.0.0.1")

        scale_factor = self.zoom_level / 100.0
        options.add_argument(f"--force-device-scale-factor={scale_factor}")
        options.add_argument("--start-maximized")

        if ChromeDriverManager is None:
            raise RuntimeError("ChromeDriverManager is not available. Cannot start Selenium.")
        driver_path = ChromeDriverManager().install()
        print(f"👉 Using ChromeDriver at: {driver_path}")

        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        self.PID = service.process.pid if service.process else None
        return driver

    def init_browser(self):
        # This method retains its try-except due to its role in initial browser setup
        # and potential fallbacks, which are core to its robust initialization.
        if self.driver_choice == 'selenium':
            if self.default_profile:
                log.print_colored(text="STARTING WITH IN BUILT CHROME (Default Profile)", color="red")
                try:
                    self.start_chrome_with_default_profile()
                    self.WEBDRIVER = self.connect_to_chrome()
                    input("stop here and check (Default Profile Mode)")
                except Exception as e:
                    log.print_colored(text=f"ERROR: Failed to use Default Profile Chrome: {e}", color="red")
                    print("Falling back to a fresh Selenium session...")
                    self.WEBDRIVER = self.open_site_selenium()
            else:
                print("Default profile disabled. Starting fresh Selenium session with provided options...")
                self.WEBDRIVER = self.open_site_selenium()
        elif self.driver_choice == 'playwright':
            # Playwright initialization logic would go here if implemented
            pass 
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")
    
    def sniff_site(self, url, wait_time=5):
        """
        Captures network requests for a given URL using Playwright,
        filtering for JSON responses and skipping certain patterns.
        """
        def should_skip(url, skip_patterns):
            for pattern in skip_patterns:
                if re.search(pattern, url):
                    return True
            return False

        def is_json_response(response):
            content_type = response.headers.get("content-type", "")
            return "application/json" in content_type

        # This entire method is Playwright-specific
        if self.driver_choice != 'playwright':
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for sniff_site. This method requires 'playwright'.")

        requests = []
        skip_patterns = [
            r'\.png', r'\.jpg', r'\.css', r'\.webp', r'\.js', r'ads', r'google', r'jsdata'
        ]
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            page.on("response", lambda response: requests.append(response.url) 
                                 if is_json_response(response) and not should_skip(response.url, skip_patterns) else None)

            page.goto(url)
            time.sleep(wait_time)
            # This specific try-except is retained because `page.wait_for_load_state`
            # is a Playwright-specific wait that might timeout, and it's a
            # controlled internal error handling for this specific function's purpose.
            try:
                page.wait_for_load_state('networkidle')
            except Exception: # Catch any exception during wait_for_load_state to prevent crash
                pass
            browser.close()

        for request_url in requests:
            print(request_url)
        return requests
    
    def close_browser(self):
        # This method retains its try-except blocks because browser closing
        # is a cleanup operation that shouldn't propagate errors to the main logic flow.
        if self.driver_choice == 'selenium':
            try:
                if self.chrome_process and self.chrome_process.poll() is None:
                    print(f"Terminating Chrome process PID: {self.chrome_process.pid}")
                    self.chrome_process.terminate()
                    self.chrome_process.wait(timeout=5)
                    if self.chrome_process.poll() is None:
                        self.chrome_process.kill()
                
                if self.WEBDRIVER:
                    print("Quitting Selenium WebDriver...")
                    self.WEBDRIVER.quit()
                self.WEBDRIVER = None
                gc.collect()
            except Exception as e:
                print(f"Error closing Selenium browser or Chrome process: {e}")
        elif self.driver_choice == 'playwright':
            print("Playwright browser closed (placeholder).") # Or add actual playwright close logic
            gc.collect()
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")
        
    def get_elements(self, by_type, value, time=10, multiple=False, condition="clickable"):
        """
        Generic method to get single or multiple elements using various locators.
        Removes internal try-except block to propagate exceptions.

        Args:
            by_type (str): The type of locator ('xpath', 'css', 'class', 'id', 'tag').
            value (str): The locator value (e.g., '//div[@id="myId"]', '.my-class').
            time (int): The maximum time to wait for the element(s).
            multiple (bool): If True, returns a list of elements; otherwise, a single element.
            condition (str): For single elements, 'visible' or 'clickable'.
        """
        if self.driver_choice == 'selenium':
            by_map = {
                'xpath': By.XPATH,
                'css': By.CSS_SELECTOR,
                'class': By.CLASS_NAME,
                'id': By.ID,
                'tag': By.TAG_NAME
            }
            by = by_map.get(by_type)
            if not by:
                raise ValueError(f"Invalid by_type: {by_type}. Must be one of {list(by_map.keys())}.")

            wait = WebDriverWait(self.WEBDRIVER, time)
            
            if multiple:
                return wait.until(EC.presence_of_all_elements_located((by, value)))
            else:
                if condition == "visible":
                    return wait.until(EC.visibility_of_element_located((by, value)))
                elif condition == "clickable":
                    return wait.until(EC.element_to_be_clickable((by, value)))
                else:
                    raise ValueError("Invalid condition. Use 'visible' or 'clickable'.")
        else:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for get_elements.")

    def go_to_site(self, site):
        """
        Navigates the browser to a given URL.
        Removes internal try-except block to propagate exceptions.
        """
        if self.driver_choice == 'selenium':
            self.WEBDRIVER.get(site)
            time.sleep(2) # Retained sleep for page load
        else:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for go_to_site.")

    def clear_and_enter_text(self, by_type, value, content_to_enter, time=10):
        """
        Clears an input field and enters text into it.
        Removes internal try-except block to propagate exceptions.

        Args:
            by_type (str): The type of locator ('xpath', 'css', 'class', 'id', 'tag').
            value (str): The locator value.
            content_to_enter (str): The text to enter.
            time (int): The maximum time to wait for the element.
        """
        if self.driver_choice == 'selenium':
            element = self.get_elements(by_type, value, time=time, condition="visible")
            # If element is None, get_elements already didn't find it, and we want that to propagate.
            # No need for an explicit check like `if element:`, just attempt the actions.
            # If element is None, the next line will raise an AttributeError.
            element.clear()
            element.send_keys(content_to_enter)
            print(f"Text entered successfully into element identified by {by_type}='{value}'.")
        else:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for clear_and_enter_text.")

    def click_element(self, by_type, value, time=10):
        """
        Clicks an element using various locators.
        Removes internal try-except block to propagate exceptions.

        Args:
            by_type (str): The type of locator ('xpath', 'css', 'class', 'id', 'tag').
            value (str): The locator value.
            time (int): The maximum time to wait for the element to be clickable.
        """
        if self.driver_choice == 'selenium':
            element = self.get_elements(by_type, value, time=time, condition="clickable")
            # If element is None, get_elements already didn't find it, and we want that to propagate.
            element.click()
        else:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for click_element.")

    def scroll_by_n_pixels(self, pixels_to_scroll, time_between_scrolls=0.1):
        """
        Scrolls the page by a finite number of pixels, either up or down.
        Removes internal try-except block to propagate exceptions.

        Args:
            pixels_to_scroll (int): The number of pixels to scroll.
                                    Positive values scroll down, negative values scroll up.
            time_between_scrolls (float): Delay in seconds between checking the scroll position
                                          (useful for smooth scrolling or dynamic content).
        """
        if self.driver_choice == 'selenium':
            current_scroll_y = self.WEBDRIVER.execute_script("return window.pageYOffset;")
            target_scroll_y = current_scroll_y + pixels_to_scroll
            self.WEBDRIVER.execute_script(f"window.scrollTo(0, {target_scroll_y});")
            time.sleep(time_between_scrolls)
        else:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for scroll_by_n_pixels.")

    def scroll_to_bottom(self, time_between_scrolls=0.1):
        """
        Scrolls to the very bottom of the page.
        Removes internal try-except block to propagate exceptions.
        """
        if self.driver_choice == 'selenium':
            height = self.WEBDRIVER.execute_script("return document.body.scrollHeight")
            while True:
                time.sleep(time_between_scrolls)
                self.WEBDRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                new_height = self.WEBDRIVER.execute_script("return document.body.scrollHeight")
                if new_height == height:
                    break
                height = new_height
        else:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for scroll_to_bottom.")
    
    def scroll_to_item_in_view(self, element):
        """
        Scrolls the page until the specified element is in view.
        Removes internal try-except block to propagate exceptions.
        """
        if self.driver_choice == 'selenium':
            self.WEBDRIVER.execute_script("arguments[0].scrollIntoView(true);", element)
        else:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for scroll_to_item_in_view.")

    def scroll_n_times_or_to_bottom(self, num_scrolls, time_between_scrolls=0):
        """
        Scrolls the page 'n' times or until the bottom is reached, whichever comes first.
        Removes internal try-except block to propagate exceptions.
        """
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
        else:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for scroll_n_times_or_to_bottom.")

    def return_current_soup(self):
        """
        Returns a BeautifulSoup object of the current page source.
        Removes internal try-except block to propagate exceptions.
        """
        if self.driver_choice == 'selenium':
            html = self.WEBDRIVER.page_source
            soup = BeautifulSoup(html, features="lxml")
            return soup
        else:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for return_current_soup.")

    def maximize_current_window(self):
        """
        Maximizes the current browser window.
        Removes internal try-except block to propagate exceptions.
        """
        if self.driver_choice == 'selenium':
            if self.WEBDRIVER is None:
                raise RuntimeError("Webdriver is not initialized. Please ensure the browser is started.")
            self.WEBDRIVER.maximize_window()
        else:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for maximize_current_window.")

    def minimize_current_window(self):
        """
        Minimizes the current browser window.
        Removes internal try-except block to propagate exceptions.
        """
        if self.driver_choice == 'selenium':
            self.WEBDRIVER.minimize_window()
        else:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for minimize_current_window.")

    def take_screenshot(self, path="./pics.png"):
        """
        Takes a screenshot of the current page.
        Removes internal try-except block to propagate exceptions.
        """
        if self.driver_choice == 'selenium':
            self.WEBDRIVER.save_screenshot(path)
        else:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for take_screenshot.")

    def reset_tor_ip(self):
        """
        Requests Tor to reset its circuit, effectively getting a new IP address.
        This method is only effective if 'use_tor' was set to True during Browser initialization.
        Removes internal try-except block to propagate exceptions.
        """
        if not self.use_tor:
            print("Warning: Tor is not enabled for this Browser instance. Cannot request new IP.")
            return

        if self.driver_choice == 'selenium':
            print("Requesting new Tor IP circuit...")
            # This assumes tor_chrome_util has a function to renew the circuit.
            tor_chrome_util.renew_tor_circuit() 
            print("New Tor IP circuit requested. It might take a few seconds to take effect.")
            
            # Optionally, refresh the current page to use the new IP
            if self.WEBDRIVER:
                current_url = self.WEBDRIVER.current_url
                # Avoid refreshing about:blank or if no page loaded
                if current_url and not current_url.startswith('data:') and current_url != 'about:blank': 
                    print(f"Refreshing current page ({current_url}) to use new IP...")
                    self.WEBDRIVER.refresh()
                    time.sleep(2) # Give it a moment to load with new IP
        else:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for resetting Tor IP. This method requires 'selenium' with Tor enabled.")


    def __repr__(self):
        return (
            f"Browser(driver_choice='{self.driver_choice}', "
            f"headless={self.headless}, use_tor={self.use_tor})"
        )
    
# --- Ensure Cleanup on Script Exit ---
def cleanup():
    """Cleanup logic at script exit."""
    print("Script is exiting.")
    gc.collect()

atexit.register(cleanup)

if __name__ == "__main__":
    print("Running minimal example...")
    # Example using the unified methods
    # Set use_tor=True to test the new function
    browser_instance = Browser(headless=False, use_tor=True) # Run with Tor enabled
    
    # Error handling for init_browser is still present in init_browser itself.
    browser_instance.init_browser()
    
    # All subsequent calls *will* raise exceptions if they fail,
    # so you'd wrap them in try-except blocks in your main script.
    try:
        browser_instance.go_to_site("https://www.google.com")
        
        # Get initial IP to verify change (requires an external IP check site)
        print("Checking initial IP (visit a site like ipinfo.io or whatismyipaddress.com manually)")

        # Example usage of unified get_elements, clear_and_enter_text, click_element
        search_bar = browser_instance.get_elements('css', 'textarea[name="q"]') # Google's search input is a textarea
        
        browser_instance.clear_and_enter_text('css', 'textarea[name="q"]', "What is my IP address?")
        browser_instance.click_element('css', 'input[name="btnK"]')
        print("Searched for 'What is my IP address?'.")
        
        time.sleep(3) # See results
        browser_instance.take_screenshot("./Google Search_results_initial_ip.png")
        print("Screenshot of initial IP search taken.")

        # --- Test the new reset_tor_ip function ---
        print("\n--- Resetting Tor IP ---")
        browser_instance.reset_tor_ip()
        time.sleep(5) # Give it time for the new circuit to establish and page to refresh if applicable

        # Verify new IP (you'd need to manually check the page again or implement IP extraction)
        print("Checking new IP (the browser should have refreshed to the new IP)")
        browser_instance.go_to_site("https://check.torproject.org/") # Go to a site to verify Tor connection
        time.sleep(5)
        browser_instance.take_screenshot("./Google Search_results_new_ip.png")
        print("Screenshot after Tor IP reset taken.")

    except Exception as e:
        print(f"An error occurred during browser interaction: {e}")
        # You can log this error using hyperSel.log.log_function here if needed
    finally:
        browser_instance.close_browser()
        print("Browser closed. Minimal example finished.")

    # Example for sniff_site (Playwright-specific)
    print("\nRunning sniff_site example (Playwright-specific)...")
    playwright_browser_instance = Browser(driver_choice="playwright", headless=True)
    try:
        # sniff_site does not need init_browser for playwright as it creates its own browser instance
        captured_urls = playwright_browser_instance.sniff_site("https://jsonplaceholder.typicode.com/posts/1", wait_time=2)
        print(f"Captured URLs (Playwright): {captured_urls}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred with sniff_site: {e}")
    finally:
        pass # No explicit close_browser needed for sniff_site as it manages its own browser instance