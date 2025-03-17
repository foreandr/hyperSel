import os
import requests
import subprocess
from bs4 import BeautifulSoup

# Get absolute path of the script directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Constants
TOR_BASE_URL = "https://dist.torproject.org/torbrowser/"
TOR_DOWNLOAD_DIR = os.path.join(BASE_DIR, "resources", "tor_browser")
TOR_INSTALLER_PATH = os.path.join(TOR_DOWNLOAD_DIR, "torbrowser-install.exe")

def get_latest_tor_browser_url():
    """Fetch the latest stable Tor Browser version dynamically."""
    response = requests.get(TOR_BASE_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract all version links, remove empty values
    version_links = [a['href'].strip('/') for a in soup.find_all('a', href=True) if a['href'].endswith('/')]
    version_links = [v for v in version_links if v]  # Remove empty strings

    print("\n🔍 Found version links:", version_links)

    # Filter out alpha, rc, and nightly builds
    stable_versions = [v for v in version_links if "alpha" not in v and "rc" not in v and "nightly" not in v]

    print("✅ Filtered stable versions:", stable_versions)

    if not stable_versions:
        raise ValueError("❌ No stable Tor Browser versions found.")

    # Sort versions properly, ignoring non-numeric parts
    def version_key(v):
        return list(map(int, v.split('.'))) if all(x.isdigit() for x in v.split('.')) else [0]

    latest_version = sorted(stable_versions, key=version_key, reverse=True)[0]
    print("📢 Latest stable Tor Browser version found:", latest_version)

    return os.path.join(TOR_BASE_URL, latest_version + "/")


def get_tor_browser_download_link(latest_url):
    """Find the correct Windows Tor Browser installer (.exe)."""
    print("\n🌍 Fetching version directory:", latest_url)
    
    response = requests.get(latest_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Debugging: Print all .exe links in this version directory
    exe_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.exe')]
    print("📝 Found .exe files:", exe_links)

    # Find the correct Windows installer
    for a in exe_links:
        if "tor-browser-windows" in a:
            download_url = os.path.join(latest_url, a)
            print("✅ Found correct installer:", download_url)
            return download_url
    
    raise ValueError("❌ Tor Browser installer for Windows not found.")


def download_tor_browser():
    """Download the full Tor Browser installer and save it."""
    if not os.path.exists(TOR_DOWNLOAD_DIR):
        os.makedirs(TOR_DOWNLOAD_DIR)

    try:
        latest_url = get_latest_tor_browser_url()
        download_url = get_tor_browser_download_link(latest_url)
    except ValueError as e:
        print(f"⚠️ {e}")
        print("🔄 Falling back to stable version (14.0.7)...")
        download_url = "https://dist.torproject.org/torbrowser/14.0.7/torbrowser-install-win64-14.0.7_en-US.exe"

    print(f"📥 Downloading Tor Browser from: {download_url}")

    response = requests.get(download_url, stream=True)
    with open(TOR_INSTALLER_PATH, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)

    print("✅ Tor Browser download complete!")
    print(f"🟢 Tor Browser installer saved to: {TOR_INSTALLER_PATH}")
    
    # Run the installer automatically
    install_tor_browser()


def install_tor_browser():
    """Run the Tor Browser installer silently."""
    installer_path = os.path.normpath(TOR_INSTALLER_PATH)  # Ensure correct path format
    print(f"🚀 Running installer: {installer_path}")

    if os.path.exists(installer_path):
        subprocess.run([f'"{installer_path}"', "/S"], shell=True)
        print("✅ Tor Browser installation complete!")
    else:
        print("❌ Installer file not found!")


if __name__ == "__main__":
    download_tor_browser()


import tor_d
import subprocess
import os


# tor_d.download_tor_browser()  # Uncomment if needed

# Get the absolute path and normalize it for Windows compatibility
exe_path = os.path.normpath(os.path.abspath(tor_d.TOR_INSTALLER_PATH))
print(f"Installer Path: {exe_path}")


def install_from_path(installer_exe_path, tor_browser_path=os.getcwd()):
    # Ensure the installer exists before running
    if os.path.exists(installer_exe_path):
        print(f"✅ Tor Browser installer found: {installer_exe_path}")
        
        # Run installer silently with the current directory as the installation location
        subprocess.run([installer_exe_path, "/S", f"/D={tor_browser_path}"], shell=True)
        
        print(f"✅ Tor Browser installed successfully in: {tor_browser_path}")
    else:
        print("❌ Installer file not found!")
    

import os
import time
import signal
import psutil
import stem.process
import requests
from stem.control import Controller
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By

# Paths
BASE_DIR = os.path.abspath("./Browser")
TOR_BROWSER_EXE = os.path.join(BASE_DIR, "firefox.exe")  # Tor Browser path
TOR_CONTROL_PORT = 9151  # Control Port for issuing NEWNYM commands
TOR_SOCKS_PORT = 9150  # Default SOCKS5 port

def close_existing_tor():
    """Terminate any running instances of Tor Browser."""
    tor_processes = []
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if "firefox" in proc.info['name'].lower():  # Adjust this if needed
                tor_processes.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if tor_processes:
        print(f"❌ Closing {len(tor_processes)} running Tor instances...")
        for pid in tor_processes:
            try:
                os.kill(pid, signal.SIGTERM)  # Graceful termination
            except PermissionError:
                print(f"⚠️ Could not terminate process {pid}. Try running with admin privileges.")
        time.sleep(3)  # Allow time for processes to close
        print("✅ All existing Tor instances closed.")
    else:
        print("✅ No existing Tor instances found.")

def start_tor_with_selenium():
    """Launch Tor Browser directly using Selenium in fullscreen mode."""
    if not os.path.exists(TOR_BROWSER_EXE):
        print("❌ Tor Browser executable not found! Check the installation path.")
        exit(1)

    close_existing_tor()  # 🔥 Ensure all existing Tor instances are closed before launching

    print("🚀 Launching Tor Browser with Selenium...")

    options = Options()
    options.binary_location = TOR_BROWSER_EXE  # Use Tor Browser as the Firefox binary
    options.set_preference("network.proxy.type", 1)
    options.set_preference("network.proxy.socks", "127.0.0.1")
    options.set_preference("network.proxy.socks_port", TOR_SOCKS_PORT)  # Tor's SOCKS5 proxy
    options.set_preference("network.proxy.socks_remote_dns", True)
    options.add_argument("--start-fullscreen")  # ✅ Open in fullscreen mode

    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    driver.maximize_window()  # ✅ Ensure fullscreen even if the argument is ignored

    try:
        connect_button = driver.find_element(By.ID, "connectButton")  # ✅ Using ID for faster lookup
        connect_button.click()
        print("✅ Clicked 'Connect' button to start Tor.")
    except Exception as e:
        print(f"⚠️ Unable to find or click the connect button: {e}")

    time.sleep(30)  # ✅ Wait for Tor to establish a connection

    print("✅ Selenium launched Tor Browser successfully in fullscreen.")
    return driver

def change_tor_ip():
    """Change Tor's IP by issuing a NEWNYM command to the control port."""
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
            controller.authenticate()  # Requires proper Tor setup
            controller.signal(stem.Signal.NEWNYM)
            print("🔄 Requested new Tor identity (IP address).")
    except Exception as e:
        print(f"❌ Failed to request new Tor identity: {e}")

def get_current_ip():
    """Check the current IP address through Tor."""
    try:
        session = requests.session()
        session.proxies = {'http': f'socks5h://127.0.0.1:{TOR_SOCKS_PORT}', 'https': f'socks5h://127.0.0.1:{TOR_SOCKS_PORT}'}
        ip = session.get("http://check.torproject.org/api/ip").text.strip()
        return ip
    except Exception as e:
        print(f"⚠️ Failed to retrieve current IP: {e}")
        return None

if __name__ == "__main__":
    driver = start_tor_with_selenium()  # ✅ Launch Tor with Selenium (ONE instance)

    print(f"🌍 Current Tor IP: {get_current_ip()}")  # Print initial IP

    for i in range(3):  # Change IP 3 times
        change_tor_ip()
        time.sleep(10)  # Wait for the new identity to take effect
        print(f"🔄 New Tor IP: {get_current_ip()}")
