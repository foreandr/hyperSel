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

WEBDRIVER = None
PAGE = None

class Browser:
    def __init__(self, driver_choice, headless, use_tor):
        if use_tor:
            print("TOR INIT")
            tor_util.start_tor()

        valid_drivers = {'selenium', 'nodriver', 'playwright'}
        if driver_choice not in valid_drivers:
            raise ValueError(f"Invalid driver choice. Must be one of {valid_drivers}.")
        
        self.driver_choice = driver_choice
        self.headless = bool(headless)
        self.use_tor = bool(use_tor)
        self.init_browser()

    def init_browser(self):
        global WEBDRIVER
        if self.driver_choice == 'selenium':
            def open_site_selenium():
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
                driver = webdriver.Chrome(options=options)
                WEBDRIVER = driver

            open_site_selenium()


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

    def sniff_site(self):
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
        if self.driver_choice == 'selenium':
            pass
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
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
        if self.driver_choice == 'selenium':
            pass
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'nodriver':
            pass
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
    #browser = Browser("nodriver", False, False)
    #time.sleep(3)
    #browser.close_browser()
    #input("----DONE ONE")
    browser = Browser("selenium", False, False)
    time.sleep(3)
    browser.close_browser()