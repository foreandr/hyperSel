import os
import requests
from bs4 import BeautifulSoup
from zipfile import ZipFile

BASE_URL = "https://dist.torproject.org/torbrowser/"
TOR_EXTRACT_DIR = "resources/tor"
TOR_ZIP_PATH = "tor.zip"

def get_latest_tor_url(base_url):
    """Scrape the index page to find the latest Tor Expert Bundle."""
    response = requests.get(base_url)
    response.raise_for_status()  # Ensure the request was successful
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the latest version folder
    version_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('/')]
    latest_version = sorted(version_links, reverse=True)[0]  # Get the latest folder
    print(f"Latest version found: {latest_version}")

    # Build URL to the latest version folder
    latest_url = os.path.join(base_url, latest_version)
    return latest_url

def get_tor_download_link(latest_url):
    """Find the download link for the Tor Expert Bundle within the latest version folder."""
    response = requests.get(latest_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the Windows Tor Expert Bundle file
    for a in soup.find_all('a', href=True):
        # Match filenames for the Windows Tor Expert Bundle
        if "tor-expert-bundle-windows" in a['href'] and a['href'].endswith(".tar.gz"):
            return os.path.join(latest_url, a['href'])

    # If no matching file is found
    raise ValueError("Tor Expert Bundle for Windows not found.")


import tarfile

def download_and_extract_tor(download_url, tar_path, extract_dir):
    """Download and extract the Tor Expert Bundle."""
    print(f"Downloading Tor Expert Bundle from: {download_url}")
    response = requests.get(download_url, stream=True)
    with open(tar_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)

    print("Extracting Tor...")
    # Extract the tar.gz file
    with tarfile.open(tar_path, 'r:gz') as tar_ref:
        tar_ref.extractall(extract_dir)

    print(f"Tor extracted to: {extract_dir}")

def download_tor():
    if not os.path.exists(TOR_EXTRACT_DIR):
        os.makedirs(TOR_EXTRACT_DIR)

    latest_url = get_latest_tor_url(BASE_URL)
    download_url = get_tor_download_link(latest_url)
    download_and_extract_tor(download_url, TOR_ZIP_PATH, TOR_EXTRACT_DIR)


import os
import subprocess
import time
import requests
import socks
import socket
from bs4 import BeautifulSoup

# Path to the extracted Tor executable
TOR_PATH = os.path.join("resources", "tor", "Tor", "tor.exe")

def start_tor():
    """Start the Tor process."""
    if not os.path.exists(TOR_PATH):
        raise FileNotFoundError(f"Tor executable not found at {TOR_PATH}")

    print("Starting Tor...")
    tor_process = subprocess.Popen(
        [TOR_PATH, "--SOCKSPort", "9050", "--ControlPort", "9051"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(5)  # Wait for Tor to initialize
    return tor_process

def stop_tor(tor_process):
    """Terminate the Tor process."""
    tor_process.terminate()
    tor_process.wait()
    print("Tor process terminated.")

def route_request_through_tor(url):
    """Route an HTTP request through Tor using SOCKS5."""
    # Set up the SOCKS5 proxy
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket

    # Send the HTTP request
    print(f"Sending request to {url} through Tor...")
    response = requests.get(url)
    return response.text

def main():
    tor_process = None
    try:
        # Start the Tor process
        tor_process = start_tor()

        # Example: Fetch a webpage through Tor
        url = "http://check.torproject.org"  # Tor check URL
        html = route_request_through_tor(url)

        # Parse and display the HTML
        soup = BeautifulSoup(html, "html.parser")
        print(soup.prettify())

    finally:
        if tor_process:
            stop_tor(tor_process)

if __name__ == "__main__":
    main()
