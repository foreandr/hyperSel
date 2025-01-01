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
        self.driver = self.init_browser()

    def init_browser(self):
        if self.driver_choice == 'selenium':
            def open_site_selenium():
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
                return driver
            
            return open_site_selenium()
            
        elif self.driver_choice == 'playwright':
            playwright, browser = open_playwright_browser(headless=False, tor=True)
            print("playwright:", playwright)
            print("browser   :", browser)
            return browser

        elif self.driver_choice == 'nodriver':
            playwright, browser = open_playwright_browser(headless=False, tor=True)
            print("playwright:", playwright)
            print("browser   :", browser)

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
        if self.driver_choice == 'selenium':
            try:
                self.driver.quit()
                self.driver = None
                gc.collect()
            except Exception as e:
                print(f"Error closing Selenium browser: {e}")


        elif self.driver_choice == 'nodriver':
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(self.driver.stop())
                else:
                    loop.run_until_complete(self.driver.stop())
                self.driver = None
                gc.collect()
            except Exception as e:
                print(f"Error closing Nodriver browser: {e}")
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

def create_playwright():
    async def create_playwright():
        try:
            # Start Playwright session
            playwright = await async_playwright().start()
            return playwright
        except Exception as e:
            print(f"Error creating Playwright instance: {e}")
            return None
    # Run the asynchronous function synchronously
    return asyncio.run(create_playwright())

def open_playwright_browser(headless=True, tor=False):
    async def open_browser():
        try:
            # Start Playwright session
            playwright = await async_playwright().start()

            # Get screen dimensions (modify if necessary)
            # width, height = util.get_display_dimensions()['width'], util.get_display_dimensions()['height']

            # Launch Chromium browser with Tor support if enabled
            launch_options = {
                "headless": headless,
                "proxy": {"server": "socks5://127.0.0.1:9050"} if tor else None,
                # "args": [f"--window-size={width},{height}"],  # Set the window size
            }
            if tor:
                print("Routing requests through Tor...")

            browser = await playwright.chromium.launch(**launch_options)

            # Create a new browser context with viewport size matching screen dimensions
            context = await browser.new_context(
                # viewport={"width": 1920, "height": 1080},
                user_agent=util.generate_random_user_agent()
            )

            page = await context.new_page()
            return playwright, browser
        except Exception as e:
            print(f"Error opening Playwright browser: {e}")
            return None, None

    # Run the asynchronous function synchronously
    return asyncio.run(open_browser())

def close_playwright_browser(playwright, browser):
    async def close_browser():
        try:
            # Close the browser
            if browser:
                print("Closing browser...")
                await browser.close()
                print("Browser closed.")
            
            # Stop the Playwright session
            if playwright:
                print("Stopping Playwright...")
                await playwright.stop()
                print("Playwright stopped.")
        except Exception as e:
            print(f"Error closing Playwright browser: {e}")

    # Run the asynchronous function synchronously
    asyncio.run(close_browser())

if __name__ == "__main__":
    # Instantiate browser objects for each driver type
    drivers = ["selenium", "playwright", "nodriver"]
    browser = Browser("nodriver", False, False)
    input("-")
    time.sleep(5)
    browser.close_browser()
    input("--")
