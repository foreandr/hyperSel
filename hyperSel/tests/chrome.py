import os
import time
import subprocess
import socket
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def kill_all_chrome():
    """Kill all running Chrome instances."""
    try:
        if os.name == "nt":  # Windows
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["taskkill", "/F", "/IM", "chromedriver.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:  # macOS/Linux
            subprocess.run(["pkill", "-f", "chrome"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-f", "chromedriver"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Killed all Chrome instances.")
    except Exception as e:
        print(f"❌ Error killing Chrome instances: {e}")
        raise


def find_chrome_path():
    """Find Chrome executable path."""
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("❌ Chrome executable not found. Please install Chrome or specify the correct path.")


def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def start_chrome_with_default_profile(port, use_tor=False):
    """Kill all Chrome instances and start Chrome with the Default profile and remote debugging port."""
    try:
        kill_all_chrome()  # Kill all running Chrome instances before starting a new one

        chrome_path = find_chrome_path()
        profile_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")  # Parent directory of profiles

        # Check if the port is already in use
        if is_port_in_use(port):
            print(f"⚠️ Port {port} is already in use. Assuming Chrome is already running.")
            return  # Do not start a new Chrome instance

        # Command to start Chrome
        cmd = [
            chrome_path,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={profile_path}",
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-dev-shm-usage",
        ]

        # Add Tor proxy logic if enabled
        if use_tor:
            print("🌍 Routing Chrome through Tor...")
            cmd.append("--proxy-server=socks5://127.0.0.1:9050")

        print(f"🚀 Starting Chrome with Default profile: {cmd}")
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)  # Allow Chrome to start
        
    except Exception as e:
        print(f"❌ Error starting Chrome: {e}")
        raise


def connect_to_chrome(port):
    """Use Selenium to connect to Chrome running on the specified port."""
    try:
        options = Options()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")

        # Use webdriver-manager to automatically install the correct chromedriver version
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        print("✅ Connected to Chrome successfully.")
        return driver
    except Exception as e:
        print(f"❌ Error connecting to Chrome: {e}")

        # Debugging step: check if Chrome is running on the remote debugging port
        print("\n🔍 Checking if Chrome is running in debug mode...")
        try:
            import requests
            response = requests.get(f"http://127.0.0.1:{port}/json/version")
            if response.status_code == 200:
                print(f"✅ Chrome is running on port {port}: {response.json()}")
            else:
                print(f"⚠️ Chrome is running but returned an unexpected response: {response.status_code}")
        except Exception:
            print("❌ Could not reach Chrome debugging endpoint. Ensure Chrome started with the correct port.")

        input("Press Enter to continue debugging...")
        raise


if __name__ == "__main__":
    PORT = 9222  # Change this if needed
    USE_TOR = False  # Set to True if using Tor

    # ✅ Start Chrome with the default profile
    start_chrome_with_default_profile(PORT, USE_TOR)

    # ✅ Connect Selenium to the Chrome instance
    driver = connect_to_chrome(PORT)

    # ✅ Open Zillow page
    url = "https://www.zillow.com/peterborough-on/3_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A3%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-78.66363840471068%2C%22east%22%3A-78.18882303605834%2C%22south%22%3A44.19384090860042%2C%22north%22%3A44.4093255562388%7D%7D"
    print(f"🌍 Navigating to {url}")
    driver.get(url)

    input("Press Enter to close Chrome...")
    driver.quit()
