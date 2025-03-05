import os
import time
import subprocess
import socket
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager


def kill_all_firefox():
    """Kill all running Firefox instances."""
    try:
        if os.name == "nt":  # Windows
            subprocess.run(["taskkill", "/F", "/IM", "firefox.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["taskkill", "/F", "/IM", "geckodriver.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:  # macOS/Linux
            subprocess.run(["pkill", "-f", "firefox"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-f", "geckodriver"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Killed all Firefox instances.")
    except Exception as e:
        print(f"❌ Error killing Firefox instances: {e}")
        raise


def find_firefox_path():
    """Find the Firefox executable path."""
    paths = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Mozilla Firefox\firefox.exe"),
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("❌ Firefox executable not found. Please install Firefox.")


def get_default_firefox_profile():
    """Find the default Firefox profile path."""
    profiles_path = os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles")  # Windows
    if not os.path.exists(profiles_path):
        raise FileNotFoundError("❌ No Firefox profiles found.")

    for profile in os.listdir(profiles_path):
        if profile.endswith(".default-release") or profile.endswith(".default"):
            return os.path.join(profiles_path, profile)

    raise FileNotFoundError("❌ No suitable Firefox profile found.")


def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def start_firefox_with_marionette(port):
    """Start Firefox in remote debugging mode using the default profile."""
    try:
        kill_all_firefox()  # Kill any existing instances

        firefox_path = find_firefox_path()
        profile_path = get_default_firefox_profile()

        # Check if the port is already in use
        if is_port_in_use(port):
            print(f"⚠️ Port {port} is already in use. Assuming Firefox is already running.")
            return  # Do not start a new Firefox instance

        # Command to start Firefox with Marionette enabled
        cmd = [
            firefox_path,
            "--marionette",
            "--profile", profile_path  # Use the correct profile
        ]

        print(f"🚀 Starting Firefox with Default profile: {cmd}")
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)  # Allow Firefox to start
        
    except Exception as e:
        print(f"❌ Error starting Firefox: {e}")
        raise


def connect_to_firefox():
    """Use Selenium to connect to Firefox running in Marionette mode."""
    try:
        options = Options()

        # 🔹 Force English settings
        options.set_preference("intl.accept_languages", "en-US, en")
        options.set_preference("general.useragent.locale", "en-US")
        options.set_preference("browser.search.region", "US")
        options.set_preference("intl.locale.requested", "en-US")

        # Use webdriver-manager to automatically install the correct geckodriver version
        driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

        print("✅ Connected to Firefox successfully (English forced, single instance).")
        return driver
    except Exception as e:
        print(f"❌ Error connecting to Firefox: {e}")
        raise


if __name__ == "__main__":
    PORT = 2828  # Default Marionette debugging port

    # ✅ Start Firefox with Marionette mode
    start_firefox_with_marionette(PORT)

    # ✅ Connect Selenium to the running Firefox instance
    driver = connect_to_firefox()

    # ✅ Open Zillow page
    url = "https://www.zillow.com/peterborough-on/3_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A3%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-78.66363840471068%2C%22east%22%3A-78.18882303605834%2C%22south%22%3A44.19384090860042%2C%22north%22%3A44.4093255562388%7D%7D"
    print(f"🌍 Navigating to {url}")
    driver.get(url)

    input("Press Enter to close Firefox...")
    driver.quit()
