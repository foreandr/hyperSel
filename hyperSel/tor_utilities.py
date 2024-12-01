import os
import subprocess
import time
import requests
import tarfile
import socks
import socket
from bs4 import BeautifulSoup
import psutil
import atexit

# Constants
BASE_URL = "https://dist.torproject.org/torbrowser/"
TOR_EXTRACT_DIR = "resources/tor"
TOR_ZIP_PATH = "tor.zip"
TOR_PATH = os.path.join(TOR_EXTRACT_DIR, "Tor", "tor.exe")
TOR_PID = None

# --- Tor Process Management ---
def start_tor(verbose=False):
    global TOR_PID
    if not os.path.exists(TOR_PATH):
        if verbose:
            print("Tor executable not found. Downloading Tor...")
        download_tor()
    else:
        if verbose:
            print("Tor is already downloaded.")

    if verbose:
        print("Starting Tor...")

    tor_process = subprocess.Popen(
        [TOR_PATH, "--SOCKSPort", "9050", "--ControlPort", "9051"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=subprocess.DETACHED_PROCESS  # Prevent auto cleanup
    )
    TOR_PID = tor_process.pid
    if verbose:
        print(f"Tor started with PID: {TOR_PID}")

    # Wait for Tor to stabilize
    for _ in range(10):  # Retry 10 times
        if psutil.pid_exists(TOR_PID):
            if verbose:
                print(f"Tor process {TOR_PID} is alive.")
            break
        time.sleep(1)
    else:
        if verbose:
            print("Tor process did not stabilize. Exiting...")



# --- Tor Download and Extraction ---
def get_latest_tor_url(base_url):
    """Find the latest Tor Expert Bundle folder from the base URL."""
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get the latest version folder
    version_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('/')]
    latest_version = sorted(version_links, reverse=True)[0]
    print(f"Latest version found: {latest_version}")
    return os.path.join(base_url, latest_version)


def get_tor_download_link(latest_url):
    """Find the download link for the Tor Expert Bundle."""
    response = requests.get(latest_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Match Windows Tor Expert Bundle file
    for a in soup.find_all('a', href=True):
        if "tor-expert-bundle-windows" in a['href'] and a['href'].endswith(".tar.gz"):
            return os.path.join(latest_url, a['href'])

    raise ValueError("Tor Expert Bundle for Windows not found.")


def download_and_extract_tor(download_url, tar_path, extract_dir):
    """Download and extract the Tor Expert Bundle."""
    print(f"Downloading Tor Expert Bundle from: {download_url}")
    response = requests.get(download_url, stream=True)
    with open(tar_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)

    print("Extracting Tor...")
    with tarfile.open(tar_path, 'r:gz') as tar_ref:
        tar_ref.extractall(extract_dir)

    print(f"Tor extracted to: {extract_dir}")

    # Delete the ZIP file after extraction
    if os.path.exists(tar_path):
        os.remove(tar_path)
        print(f"Deleted temporary file: {tar_path}")


def download_tor():
    """Manage the Tor download process."""
    if not os.path.exists(TOR_EXTRACT_DIR):
        os.makedirs(TOR_EXTRACT_DIR)

    latest_url = get_latest_tor_url(BASE_URL)
    download_url = get_tor_download_link(latest_url)
    download_and_extract_tor(download_url, TOR_ZIP_PATH, TOR_EXTRACT_DIR)

def terminate_existing_tor():
    """Search for and terminate all running Tor processes."""
    print("Looking for running Tor processes...")
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if proc.info['name'] == 'tor.exe':
                # print(f"Found Tor process (PID {proc.info['pid']}). Terminating...")
                proc.terminate()  # Graceful termination
                proc.wait(timeout=5)
                print(f"Tor process (PID {proc.info['pid']}) terminated.")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
            print(f"Could not terminate process {proc.info['pid']}: {e}")


# --- HTTP Request Through Tor ---
def route_request_through_tor(url):
    """Route an HTTP request through Tor using SOCKS5."""
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket

    print(f"Sending request to {url} through Tor...")
    response = requests.get(url)
    return response.text


# --- Ensure Cleanup on Script Exit ---
def cleanup():
    """Cleanup logic at script exit."""
    print("Script is exiting.")
    #if TOR_PID and psutil.pid_exists(TOR_PID):
    #    print(f"Tor process {TOR_PID} is still running.")

atexit.register(cleanup)


# --- Main Execution ---
def main():
    # Fetch a webpage through Tor
    url = "http://check.torproject.org"
    html = route_request_through_tor(url)

    # Parse and display the HTML
    soup = BeautifulSoup(html, "html.parser")
    print("LEN OF SOUP", len(str(soup)))

start_tor()

if __name__ == "__main__":
    terminate_existing_tor()
