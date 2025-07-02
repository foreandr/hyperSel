# tor_manager.py
import os
import subprocess
import time
import requests
import tarfile
import socks
import socket
from bs4 import BeautifulSoup
import psutil
# We will still use stem if you plan to ever use renew_tor_circuit,
# but for a full restart, it's not strictly necessary for the core restart logic.
# However, it's good to keep if you might want to use it elsewhere.
from stem import Signal
from stem.control import Controller


# Constants
BASE_URL = "https://dist.torproject.org/torbrowser/"
TOR_EXTRACT_DIR = "resources/tor"
TOR_ZIP_PATH = "tor_expert_bundle.tar.gz" # Changed to avoid confusion with .zip
TOR_PATH = os.path.join(TOR_EXTRACT_DIR, "Tor", "tor.exe")
TOR_PID = None # Global to track Tor's PID

# Path for the Tor control port file
TOR_CONTROL_PORT_FILE = "tor_control_port"

# --- Tor Process Management ---
def _cleanup_control_port_file():
    """Removes the Tor control port file."""
    if os.path.exists(TOR_CONTROL_PORT_FILE):
        try:
            os.remove(TOR_CONTROL_PORT_FILE)
            print("Removed tor_control_port file.")
        except OSError as e:
            print(f"Error removing tor_control_port file: {e}")

def start_tor(verbose=False):
    global TOR_PID
    
    # Ensure any previous control port file is cleaned up before starting
    _cleanup_control_port_file()

    if not os.path.exists(TOR_PATH):
        if verbose:
            print("Tor executable not found. Downloading Tor...")
        download_tor()
    else:
        if verbose:
            print("Tor is already downloaded.")

    if verbose:
        print("Starting Tor...")

    try:
        tor_process = subprocess.Popen(
            [TOR_PATH, "--SOCKSPort", "9050", "--ControlPort", "9051", "--ControlPortWriteToFile", TOR_CONTROL_PORT_FILE],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.DETACHED_PROCESS # Prevent auto cleanup
        )
        TOR_PID = tor_process.pid
        if verbose:
            print(f"Tor started with PID: {TOR_PID}")

        # Wait for Tor to stabilize and control port to be accessible
        for _ in range(30): # Increased retries for stability
            if psutil.pid_exists(TOR_PID):
                if os.path.exists(TOR_CONTROL_PORT_FILE) and os.path.getsize(TOR_CONTROL_PORT_FILE) > 0:
                    with open(TOR_CONTROL_PORT_FILE, 'r') as f:
                        port_info = f.read().strip()
                    if "9051" in port_info: # Basic check for port info
                        if verbose:
                            print(f"Tor process {TOR_PID} is alive and control port is accessible.")
                        return True # Tor started successfully and control port available
                elif verbose:
                    print(f"Waiting for Tor control port file '{TOR_CONTROL_PORT_FILE}'...")
            else:
                if verbose:
                    print("Tor process not found, something went wrong during startup.")
                _cleanup_control_port_file() # Clean up if process died
                return False # Tor process died unexpectedly
            time.sleep(1)
        
        if verbose:
            print("Tor process did not stabilize or control port not accessible. Terminating...")
        terminate_tor_process(TOR_PID) # Try to terminate it if it didn't stabilize
        _cleanup_control_port_file()
        return False # Failed to start Tor and access control port
    except Exception as e:
        print(f"Error launching Tor process: {e}")
        _cleanup_control_port_file()
        return False

def terminate_tor_process(pid):
    """Terminates a specific Tor process by PID."""
    try:
        process = psutil.Process(pid)
        if process.name() == 'tor.exe': # Extra check to ensure we only kill tor.exe
            print(f"Terminating Tor process (PID {pid})...")
            process.terminate()
            process.wait(timeout=5)
            if process.is_running():
                process.kill()
                print(f"Tor process (PID {pid}) killed.")
            else:
                print(f"Tor process (PID {pid}) terminated.")
        else:
            print(f"PID {pid} is not a tor.exe process. Not terminating.")
    except psutil.NoSuchProcess:
        print(f"No Tor process with PID {pid} found.")
    except (psutil.AccessDenied, psutil.TimeoutExpired) as e:
        print(f"Could not terminate process {pid}: {e}")

def stop_tor(verbose=False):
    """Search for and terminate all running Tor processes and clean up."""
    if verbose:
        print("Looking for running Tor processes to stop...")
    found_tor_processes = False
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if proc.info['name'] == 'tor.exe':
                found_tor_processes = True
                terminate_tor_process(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass # Ignore errors for processes that might disappear
    
    if not found_tor_processes and verbose:
        print("No Tor processes found to stop.")

    _cleanup_control_port_file() # Always clean up the control file


def restart_tor(verbose=False):
    """Stops any existing Tor processes and starts a new one."""
    if verbose:
        print("\n--- RESTARTING TOR PROCESS ---")
    stop_tor(verbose=verbose)
    time.sleep(2) # Give a moment for ports to free up
    return start_tor(verbose=verbose)


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

    # Delete the temporary file after extraction
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

# --- HTTP Request Through Tor (for testing purposes) ---
def route_request_through_tor(url):
    """Route an HTTP request through Tor using SOCKS5."""
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket

    print(f"Sending request to {url} through Tor...")
    response = requests.get(url)
    return response.text

# Example of how you might test this file directly
if __name__ == "__main__":
    print("Running tor_manager.py directly for testing.")
    print("Attempting to restart Tor and check IP.")
    if restart_tor(verbose=True):
        try:
            print("Tor restarted successfully. Fetching current IP...")
            current_ip = route_request_through_tor("https://api.ipify.org").strip()
            print(f"Current IP: {current_ip}")

            print("\nRequesting new circuit (this will not restart Tor process, only renew circuit)...")
            with Controller.from_port(port=9051) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
            time.sleep(5) # Give time for new circuit
            new_circuit_ip = route_request_through_tor("https://api.ipify.org").strip()
            print(f"IP after NEWNYM: {new_circuit_ip}")

            if current_ip != new_circuit_ip:
                print("IP successfully changed via NEWNYM.")
            else:
                print("IP did not change via NEWNYM. This can happen.")


            print("\nAttempting full Tor restart...")
            if restart_tor(verbose=True):
                print("Tor fully restarted again. Fetching current IP...")
                final_ip = route_request_through_tor("https://api.ipify.org").strip()
                print(f"Final IP: {final_ip}")
            else:
                print("Failed to restart Tor second time.")

        except Exception as e:
            print(f"An error occurred during IP check: {e}")
    else:
        print("Failed to start/restart Tor initially.")
    
    print("\nStopping Tor process on exit.")
    stop_tor(verbose=True)