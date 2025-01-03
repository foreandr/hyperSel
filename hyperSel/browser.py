import tor_util
import util
import asyncio
import nodriver as nd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from playwright.async_api import async_playwright
import gc
import time
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import os
import socket
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from subprocess import Popen
import util
import tor_util

WEBDRIVER = None
PAGE = None

class Browser:
    def __init__(self, driver_choice, headless, use_tor, default_profile=True):
        if use_tor:
            print("TOR INIT")
            tor_util.start_tor()

        valid_drivers = {'selenium', 'nodriver', 'playwright'}
        if driver_choice not in valid_drivers:
            raise ValueError(f"Invalid driver choice. Must be one of {valid_drivers}.")
        
        self.driver_choice = driver_choice
        self.headless = bool(headless)
        self.use_tor = bool(use_tor)
        self.default_profile = default_profile
        self.init_browser()

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

    def start_chrome_with_default_profile(self, port):
        """Start Chrome with the Default profile and remote debugging port."""
        try:
            # Ensure Chrome executable is found
            chrome_path = self.find_chrome_path()
            profile_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")  # Parent directory of profiles

            # Check if the port is already in use
            if self.is_port_in_use(port):
                print(f"Port {port} is already in use. Assuming Chrome is already running.")
                return  # Do not start a new Chrome instance

            # Command to start Chrome
            cmd = [
                chrome_path,
                f"--remote-debugging-port={port}",
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

    def connect_to_chrome(self, port):
        """Use Selenium to connect to Chrome running on the specified port."""
        try:
            options = Options()
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            driver = webdriver.Chrome(service=Service(), options=options)
            return driver
        except Exception as e:
            print(f"Error connecting to Chrome: {e}")
            raise

    def open_site_selenium(self):
        """Open a Selenium driver without using a profile."""
        global WEBDRIVER
        options = Options()
        if self.headless:
            options.add_argument("--headless")  # Run in headless mode

        # Add user-agent
        options.add_argument(f"--user-agent={util.generate_random_user_agent()}")

        # Use Tor if specified
        if self.use_tor:
            print("Routing requests through Tor...")
            options.add_argument("--proxy-server=socks5://127.0.0.1:9050")

        options.add_argument("--disable-features=NetworkService")
        options.add_argument("--log-level=3")  # Suppress unnecessary logs
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--host-resolver-rules=MAP aa.online-metrix.net 127.0.0.1")

        # Initialize the driver
        WEBDRIVER = webdriver.Chrome(options=options)

    def init_browser(self):
        global WEBDRIVER
        if self.driver_choice == 'selenium':
            if self.default_profile:
                port = 9222  # Default debugging port
                try:
                    # Attempt to start Chrome with the Default profile
                    self.start_chrome_with_default_profile(port)
                    WEBDRIVER = self.connect_to_chrome(port)
                except Exception as e:
                    print(f"Failed to connect to local Chrome instance: {e}")
                    print("Falling back to a fresh Selenium session...")
                    self.open_site_selenium()
            else:
                print("Default profile disabled. Starting fresh Selenium session...")
                self.open_site_selenium()

        elif self.driver_choice == 'nodriver':
            async def open_nodriver(headless=False, tor=False):
                browser_args = ["--start-maximized"]
                browser_args.append(f"--user-agent={util.generate_random_user_agent()}")

                if tor:
                    browser_args.append("--proxy-server=socks5://127.0.0.1:9050")

                browser = await nd.start(
                    headless=headless,
                    browser_args=browser_args,
                    lang="en-US",
                )
                return browser
            
            async def asyc_open_browser(headless, tor):
                browser = await open_nodriver(headless, tor)
                return browser

            def open_browser(headless=False, tor=False):
                return asyncio.run(asyc_open_browser(headless, tor))

            browser = open_browser(headless=self.headless, tor=self.use_tor)
            WEBDRIVER = browser 

        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def sniff_site(self, url):
        '''CHECKS FOR OPEN JSONS AND APIS'''
        if self.driver_choice == 'selenium':
            pass
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def close_browser(self):
        global WEBDRIVER
        if self.driver_choice == 'selenium':
            try:
                WEBDRIVER.quit()
                WEBDRIVER = None
                gc.collect()
            except Exception as e:
                print(f"Error closing Selenium browser: {e}")

        elif self.driver_choice == 'playwright':
            print("GETTING HERE?")
            gc.collect()

        elif self.driver_choice == 'nodriver':
            async def custom_kill_browser(browser):
                util.kill_process_by_pid(browser._process_pid)

            def kill_browser(browser):
                asyncio.run(custom_kill_browser(browser))

            kill_browser(WEBDRIVER)
            WEBDRIVER = None

        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    
    def get_element(self):
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
        global WEBDRIVER
        global PAGE
        sleep_time = 2
        
        if self.driver_choice == 'selenium':
            WEBDRIVER.get(site)
            time.sleep(sleep_time)
        elif self.driver_choice == 'nodriver':
            async def async_go_to_site(browser, url):
                page = await browser.get(url=url)
                return page
            
            def go_to_site(browser, url):
                return asyncio.run(async_go_to_site(browser, url))

            page = go_to_site(WEBDRIVER, site)    
            PAGE = page
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def clear_input_field_by_xpath(self):
        if self.driver_choice == 'selenium':
            pass
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def enter_text_into_input_field(self):
        if self.driver_choice == 'selenium':
            pass
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def click_button(self):
        if self.driver_choice == 'selenium':
            pass
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")
    
    def scroll_to_bottom(self):
        if self.driver_choice == 'selenium':
            pass
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")
    
    def scroll_to_item_in_view(self):
        if self.driver_choice == 'selenium':
            pass
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def scroll_n_times_or_to_bottom(self):
        if self.driver_choice == 'selenium':
            pass
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
        global WEBDRIVER
        global PAGE
        if self.driver_choice == 'selenium':
            html = WEBDRIVER.page_source
            soup = BeautifulSoup(html, features="lxml")
            return soup
        elif self.driver_choice == 'nodriver':

            async def async_get_site_soup():
                page = PAGE
                content = await page.get_content()
                soup = BeautifulSoup(content, 'html.parser')
                return soup
            
            def get_site_soup():
                return asyncio.run(async_get_site_soup())
            
            return get_site_soup()
        
        
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def maximize_current_window(self):
        if self.driver_choice == 'selenium':
            pass
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def minimize_current_window(self):
        if self.driver_choice == 'selenium':
            pass
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def take_screenshot(self):
        if self.driver_choice == 'selenium':
            pass
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

if __name__ == "__main__":
    # Instantiate browser objects for each driver type
    # drivers = ["selenium", "playwright", "nodriver"]

    browser = Browser(driver_choice='selenium', headless=False, use_tor=False, default_profile=False)
    browser.go_to_site("http://check.torproject.org")
    soup = browser.return_current_soup()
    print(len(str(soup)))
    time.sleep(3)
    browser.close_browser()

    exit()
    browser = Browser("nodriver", False, False)
    browser.go_to_site("http://check.torproject.org")
    soup = browser.return_current_soup()
    print(len(str(soup)))
    time.sleep(3)
    browser.close_browser()

    '''
    SCROLLS AND CLICKS, FIND by xpath, css selector, class, get current url
    sending keys, scroll into vieew
    
    '''
