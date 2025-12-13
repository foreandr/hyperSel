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
import undetected_chromedriver as undetected_chromedriver_

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("webdriver_manager not found. Please install it: pip install webdriver-manager")
    ChromeDriverManager = None


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
        chrome_options: Options = None,
        download_dir=None
    ):
        if use_tor:
            print("TOR INIT")
            tor_chrome_util.start_tor()

        valid_drivers = {'selenium', 'playwright', 'undetected_chromedriver'}
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
        self.chrome_options = chrome_options if chrome_options is not None else Options()
        self.chrome_process = None

        if download_dir is None:
            self.download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        else:
            self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
        print(f"Configured browser to download files to: {self.download_dir}")

        self.selenium_prefs = {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safeBrowse.enabled": True,
            "plugins.always_open_pdf_externally": True
        }
        self.selenium_args_for_downloads = ["--disable-features=DownloadBubble", "--disable-features=DownloadBubbleV2"]


    def find_chrome_path(self):
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        raise FileNotFoundError("Chrome executable not found. Please install Google Chrome or specify the path manually.")

    def is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) == 0

    def start_chrome_with_default_profile(self):
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
        try:
            options_for_connection = self.chrome_options
            options_for_connection.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.port}")
            options_for_connection.add_experimental_option("prefs", self.selenium_prefs)
            for arg in self.selenium_args_for_downloads:
                options_for_connection.add_argument(arg)

            if ChromeDriverManager is None:
                raise RuntimeError("ChromeDriverManager is not available. Please install 'webdriver-manager'.")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options_for_connection)
            return driver
        except Exception as e:
            print(f"Error connecting to Chrome on port {self.port}: {e}")
            raise

    def open_site_selenium(self):
        options = self.chrome_options

        if self.headless:
            options.add_argument("--headless=new")

        options.add_argument(f"--user-agent={util.generate_random_user_agent()}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--incognito") # Keep for standard Selenium if desired
        options.add_argument("--disable-3d-apis")
        options.add_argument("--disable-popup-blocking") # Explicitly disable pop-up blocking

        if self.use_tor:
            print("Routing requests through Tor...")
            options.add_argument("--proxy-server=socks5://127.0.0.1:9050")

        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--host-resolver-rules=MAP aa.online-metrix.net 127.0.0.1")

        options.add_experimental_option("prefs", self.selenium_prefs)
        for arg in self.selenium_args_for_downloads:
            options.add_argument(arg)

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
        if self.driver_choice == 'selenium':
            if self.default_profile:
                log.print_colored(text="STARTING WITH IN BUILT CHROME (Default Profile)", color="red")
                try:
                    self.start_chrome_with_default_profile()
                    self.WEBDRIVER = self.connect_to_chrome()
                except Exception as e:
                    log.print_colored(text=f"ERROR: Failed to use Default Profile Chrome: {e}", color="red")
                    print("Falling back to a fresh Selenium session...")
                    self.WEBDRIVER = self.open_site_selenium()
            else:
                print("Default profile disabled. Starting fresh Selenium session with provided options...")
                self.WEBDRIVER = self.open_site_selenium()
        elif self.driver_choice == 'playwright':
            pass
        elif self.driver_choice == 'undetected_chromedriver':
            print("Initializing undetected_chromedriver...")
            uc_options = Options()
            if self.headless:
                uc_options.add_argument("--headless=new")

            uc_options.add_argument(f"--user-agent={util.generate_random_user_agent()}")
            uc_options.add_argument("--disable-gpu")
            uc_options.add_argument("--no-sandbox")
            uc_options.add_argument("--disable-dev-shm-usage")
            # --- CRITICAL CHANGE: Removed --incognito for undetected_chromedriver ---
            # It's likely interfering with tab management and internal profile handling.
            # uc_options.add_argument("--incognito")
            uc_options.add_argument("--disable-3d-apis")
            uc_options.add_argument("--log-level=3")
            uc_options.add_argument(f"--force-device-scale-factor={self.zoom_level / 100.0}")
            uc_options.add_argument("--start-maximized")
            # --- CRITICAL CHANGE: Add --disable-popup-blocking for undetected_chromedriver ---
            # This directly addresses the potential "pop up block" issue.
            uc_options.add_argument("--disable-popup-blocking")


            driver = undetected_chromedriver_.Chrome(
                headless=self.headless,
                use_subprocess=False,
                version_main=137, # Ensure this matches your Chrome version
                options=uc_options
            )
            self.WEBDRIVER = driver
            print(f"undetected_chromedriver initialized. Download path may default to browser's standard location: {self.download_dir}")
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def sniff_site(self, url, timeout=5):
        def should_skip(url, skip_patterns):
            for pattern in patterns:
                if re.search(pattern, url):
                    return True
            return False

        def is_json_response(response):
            return "application/json" in response.headers.get("content-type", "")

        if self.driver_choice != 'playwright':
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for sniff_site. This method requires 'playwright'.")

        requests = []
        patterns = [r'\.png', r'\.jpg', r'\.css', r'\.webp', r'\.js', r'ads', r'google', r'jsdata']

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            page.on("response", lambda response: requests.append(response.url) if is_json_response(response) and not should_skip(response.url, patterns) else None)

            page.goto(url)
            time.sleep(timeout)
            try:
                page.wait_for_load_state('networkidle')
            except Exception:
                pass
            browser.close()

        for request_url in requests:
            print(request_url)
        return requests

    def close_browser(self):
        if self.driver_choice == 'selenium' or self.driver_choice == 'undetected_chromedriver':
            try:
                if self.chrome_process and self.chrome_process.poll() is None:
                    print(f"Terminating Chrome process PID: {self.chrome_process.pid}")
                    self.chrome_process.terminate()
                    self.chrome_process.wait(timeout=5)
                    if self.chrome_process.poll() is None:
                        self.chrome_process.kill()

                if self.WEBDRIVER:
                    print("Quitting WebDriver...")
                    self.WEBDRIVER.quit()
                self.WEBDRIVER = None
                gc.collect()
            except Exception as e:
                print(f"Error closing WebDriver or Chrome process: {e}")
        elif self.driver_choice == 'playwright':
            print("Playwright browser closed (placeholder).")
            gc.collect()
        else:
            raise ValueError("Unsupported driver. This should never happen if validation is correct.")

    def get_elements(self, by_type, value, timeout=10, multiple=False, condition="clickable"):
        if self.driver_choice not in {'selenium', 'undetected_chromedriver'}:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for get_elements.")

        by_map = {
            'xpath': By.XPATH, 'css': By.CSS_SELECTOR, 'class': By.CLASS_NAME, 'id': By.ID, 'tag': By.TAG_NAME
        }
        by = by_map.get(by_type)
        if not by:
            raise ValueError(f"Invalid by_type: {by_type}. Must be one of {list(by_map.keys())}.")

        wait = WebDriverWait(self.WEBDRIVER, timeout)
        if multiple:
            return wait.until(EC.presence_of_all_elements_located((by, value)))
        else:
            if condition == "visible":
                return wait.until(EC.visibility_of_element_located((by, value)))
            elif condition == "clickable":
                return wait.until(EC.element_to_be_clickable((by, value)))
            else:
                raise ValueError("Invalid condition. Use 'visible' or 'clickable'.")

    def go_to_site(self, site):
        if self.driver_choice not in {'selenium', 'undetected_chromedriver'}:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for go_to_site.")
        self.WEBDRIVER.get(site)
        time.sleep(3)

    def clear_and_enter_text(self, by_type, value, content_to_enter, timeout=10):
        if self.driver_choice not in {'selenium', 'undetected_chromedriver'}:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for clear_and_enter_text.")
        element = self.get_elements(by_type, value, timeout=timeout, condition="visible")
        element.clear()
        element.send_keys(content_to_enter)
        print(f"Text entered successfully into element identified by {by_type}='{value}'.")

    def clear_and_enter_text_in_chunks(self, by_type, value, content_to_enter, chunk_size=50, delay_between_chunks=0.1, timeout=10):
        if self.driver_choice not in {'selenium', 'undetected_chromedriver'}:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for clear_and_enter_text_in_chunks.")
        element = self.get_elements(by_type, value, timeout=timeout, condition="visible")
        element.clear()
        for i in range(0, len(content_to_enter), chunk_size):
            element.send_keys(content_to_enter[i:i + chunk_size])
            time.sleep(delay_between_chunks)

    def click_element(self, by_type, value, timeout=10):
        if self.driver_choice not in {'selenium', 'undetected_chromedriver'}:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for click_element.")
        element = self.get_elements(by_type, value, timeout=timeout, condition="clickable")
        element.click()

    def scroll_by_n_pixels(self, pixels_to_scroll, time_between_scrolls=0.1):
        if self.driver_choice not in {'selenium', 'undetected_chromedriver'}:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for scroll_by_n_pixels.")
        current_scroll_y = self.WEBDRIVER.execute_script("return window.pageYOffset;")
        target_scroll_y = current_scroll_y + pixels_to_scroll
        self.WEBDRIVER.execute_script(f"window.scrollTo(0, {target_scroll_y});")
        time.sleep(time_between_scrolls)

    def scroll_to_bottom(self, time_between_scrolls=0.1):
        if self.driver_choice not in {'selenium', 'undetected_chromedriver'}:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for scroll_to_bottom.") # comment
        height = self.WEBDRIVER.execute_script("return document.documentElement.scrollHeight;")
        while True:
            self.WEBDRIVER.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(time_between_scrolls)
            new_height = self.WEBDRIVER.execute_script("return document.documentElement.scrollHeight;")
            if new_height == height:
                break
            height = new_height

    def scroll_to_item_in_view(self, element):
        if self.driver_choice not in {'selenium', 'undetected_chromedriver'}:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for scroll_to_item_in_view.")
        self.WEBDRIVER.execute_script("arguments[0].scrollIntoView(true);", element)

    def scroll_n_times_or_to_bottom(self, num_scrolls, time_between_scrolls=0):
        if self.driver_choice not in {'selenium', 'undetected_chromedriver'}:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for scroll_n_times_or_to_bottom.")
        scroll_count = 0
        while scroll_count < num_scrolls:
            height = self.WEBDRIVER.execute_script("return document.body.scrollHeight")
            self.WEBDRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(time_between_scrolls)
            new_height = self.WEBDRIVER.execute_script("return document.body.scrollHeight")
            if new_height == height:
                break
            scroll_count += 1

    def return_current_soup(self):
        if self.driver_choice not in {'selenium', 'undetected_chromedriver'}:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for return_current_soup.")
        return BeautifulSoup(self.WEBDRIVER.page_source, features="lxml")

    def maximize_current_window(self):
        if self.driver_choice not in {'selenium', 'undetected_chromedriver'}:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for maximize_current_window.")
        if self.WEBDRIVER is None:
            raise RuntimeError("Webdriver is not initialized. Please ensure the browser is started.")
        self.WEBDRIVER.maximize_window()

    def minimize_current_window(self):
        if self.driver_choice not in {'selenium', 'undetected_chromedriver'}:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for minimize_current_window.")
        self.WEBDRIVER.minimize_window()

    def take_screenshot(self, path="./pics.png"):
        if self.driver_choice not in {'selenium', 'undetected_chromedriver'}:
            raise ValueError(f"Driver '{self.driver_choice}' is not supported for take_screenshot.")
        self.WEBDRIVER.save_screenshot(path)

    def reset_tor_ip(self):
        if not self.use_tor:
            print("Tor is not enabled for this browser instance. IP reset skipped.")
            return

        print("Attempting to reset Tor IP...")
        try:
            tor_chrome_util.renew_tor_circuit()
            print("Tor IP reset initiated. It may take a few moments for a new circuit to establish.")
        except Exception as e:
            print(f"Failed to reset Tor IP: {e}")
            raise

    def __repr__(self):
        return (
            f"Browser(driver_choice='{self.driver_choice}', "
            f"headless={self.headless}, use_tor={self.use_tor})"
        )

    # --- New Tab Navigation Methods ---

    def _ensure_selenium_driver(self):
        """Helper to ensure the driver is initialized and is Selenium-based."""
        if self.driver_choice not in {'selenium', 'undetected_chromedriver'}:
            raise ValueError(f"Tab navigation is not supported for driver '{self.driver_choice}'. Requires 'selenium' or 'undetected_chromedriver'.")
        if not self.WEBDRIVER:
            raise RuntimeError("WebDriver is not initialized. Cannot perform tab operations.")

    def open_new_tab(self, url: str = None) -> str:
        """
        Opens a new browser tab and optionally navigates to a URL.
        Returns the handle of the new tab.
        """
        self._ensure_selenium_driver()
        current_handles = self.WEBDRIVER.window_handles
        # print(f"Handles before open: {current_handles}") # Debugging

        # Execute script to open a new tab
        self.WEBDRIVER.execute_script("window.open('about:blank', '_blank');")

        # Wait for the number of handles to change
        # This WebDriverWait is critical.
        WebDriverWait(self.WEBDRIVER, 10).until(
            lambda driver: len(driver.window_handles) > len(current_handles)
        )

        all_handles = self.WEBDRIVER.window_handles
        # print(f"Handles after open and wait: {all_handles}") # Debugging

        # Find the newly opened tab handle
        new_tab_handle = None
        for handle in all_handles:
            if handle not in current_handles:
                new_tab_handle = handle
                break

        if new_tab_handle is None:
            # Fallback if the above logic fails for some reason
            # This is less robust but might catch an edge case where
            # the handle count increases but the new handle isn't easily identifiable
            # or if the wait times out but a new window still appears.
            if len(all_handles) > len(current_handles):
                 new_tab_handle = all_handles[-1] # Assume it's the last one if count increased

            if new_tab_handle is None:
                raise RuntimeError("Failed to open a new tab: A new window handle was not detected.")


        self.WEBDRIVER.switch_to.window(new_tab_handle)
        if url:
            self.go_to_site(url)
        # print(f"Opened new tab with handle: {new_tab_handle}")
        return new_tab_handle

    def switch_to_tab(self, tab_handle: str):
        """
        Switches the WebDriver's focus to the tab specified by its handle.
        """
        self._ensure_selenium_driver()
        if tab_handle not in self.WEBDRIVER.window_handles:
            raise ValueError(f"Tab handle '{tab_handle}' does not exist.")
        self.WEBDRIVER.switch_to.window(tab_handle)
        # print(f"Switched to tab with handle: {tab_handle}")

    def get_current_tab_handle(self) -> str:
        """
        Returns the handle of the currently active tab.
        """
        self._ensure_selenium_driver()
        return self.WEBDRIVER.current_window_handle

    def get_all_tab_handles(self) -> list[str]:
        """
        Returns a list of all open tab handles.
        """
        self._ensure_selenium_driver()
        return self.WEBDRIVER.window_handles

    def close_current_tab(self):
        """
        Closes the currently active tab. If it's the last tab, it closes the browser.
        Otherwise, it switches to the first available tab after closing.
        """
        self._ensure_selenium_driver()
        if len(self.WEBDRIVER.window_handles) == 1:
            print("Warning: Closing the last tab will close the browser entirely.")
            self.WEBDRIVER.close()
            self.WEBDRIVER = None
        else:
            current_handle = self.WEBDRIVER.current_window_handle
            self.WEBDRIVER.close()
            remaining_handles = self.WEBDRIVER.window_handles
            if remaining_handles:
                next_handle = [h for h in remaining_handles if h != current_handle]
                if next_handle:
                    self.WEBDRIVER.switch_to.window(next_handle[0])
                    print(f"Closed current tab and switched to: {self.WEBDRIVER.current_window_handle}")
                else:
                    self.WEBDRIVER.switch_to.window(remaining_handles[0])
                    print(f"Closed current tab and switched to: {self.WEBDRIVER.current_window_handle}")
            else:
                self.WEBDRIVER = None
        print("Closed current tab.")


    def close_tab_by_handle(self, tab_handle: str):
        """
        Closes a specific tab identified by its handle.
        Switches back to the original active tab after closing, if possible.
        """
        self._ensure_selenium_driver()
        if tab_handle not in self.WEBDRIVER.window_handles:
            # print(f"Warning: Tab with handle '{tab_handle}' not found or already closed.")
            return

        current_active_handle = self.WEBDRIVER.current_window_handle

        if current_active_handle == tab_handle and len(self.WEBDRIVER.window_handles) == 1:
            self.close_current_tab()
            # print(f"Closed the only remaining tab with handle: {tab_handle}")
        else:
            self.WEBDRIVER.switch_to.window(tab_handle)
            self.WEBDRIVER.close()
            # print(f"Closed tab with handle: {tab_handle}")

            if current_active_handle in self.WEBDRIVER.window_handles:
                self.WEBDRIVER.switch_to.window(current_active_handle)
                # print(f"Switched back to original tab: {current_active_handle}")
            else:
                remaining_handles = self.WEBDRIVER.window_handles
                if remaining_handles:
                    self.WEBDRIVER.switch_to.window(remaining_handles[0])
                    # print(f"Original tab closed. Switched to: {self.WEBDRIVER.current_window_handle}")
                else:
                    self.WEBDRIVER = None

    def close_all_other_tabs(self):
        """
        Closes all tabs except the currently active one.
        """
        self._ensure_selenium_driver()
        current_handle = self.WEBDRIVER.current_window_handle
        all_handles = self.WEBDRIVER.window_handles
        tabs_closed_count = 0
        for handle in all_handles:
            if handle != current_handle:
                self.WEBDRIVER.switch_to.window(handle)
                self.WEBDRIVER.close()
                tabs_closed_count += 1
        self.WEBDRIVER.switch_to.window(current_handle)
        print(f"Closed {tabs_closed_count} other tabs. Current tab is: {current_handle}")


# --- Ensure Cleanup on Script Exit ---
def cleanup():
    print("\nScript is exiting. Performing cleanup...")
    gc.collect()

atexit.register(cleanup)
