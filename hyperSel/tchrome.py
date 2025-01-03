import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from subprocess import Popen

def list_all_chrome_profiles():
    """List all Chrome profiles and their corresponding file paths."""
    base_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    profiles = []

    if os.path.exists(base_path):
        for folder in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder)
            if os.path.isdir(folder_path):
                preferences_path = os.path.join(folder_path, "Preferences")
                if os.path.exists(preferences_path):
                    try:
                        with open(preferences_path, "r", encoding="utf-8") as f:
                            preferences = json.load(f)
                            profile_name = preferences.get("profile", {}).get("name", "Unknown")
                            profiles.append((profile_name, folder_path))
                    except json.JSONDecodeError:
                        pass

    return profiles

def start_chrome_with_default_profile(port):
    """Start Chrome with the Default profile and remote debugging port."""
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # Path to Chrome executable
    profile_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")  # Parent directory of profiles

    cmd = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_path}",
        "--disable-blink-features=AutomationControlled",
        "--start-maximized",
    ]
    print(f"Starting Chrome with Default profile: {cmd}")
    Popen(cmd)
    time.sleep(5)  # Allow Chrome to start



def use_chrome_profile(port):
    """Use Selenium to connect to Chrome running on the specified port."""
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")

    driver = webdriver.Chrome(service=Service(), options=options)
    return driver


def rotate_through_profiles():
    """Rotate through Chrome profiles and perform actions."""
    profiles = list_all_chrome_profiles()
    if not profiles:
        print("No profiles found.")
        return

    base_port = 9222
    for i, (profile_name, profile_path) in enumerate(profiles):
        port = base_port + i
        print(f"Using profile: {profile_name}, Path: {profile_path}")

        # Start Chrome with the current profile
        start_chrome_with_default_profile(port)

        # Connect to Chrome using Selenium
        try:
            driver = use_chrome_profile(port)
            driver.get("https://www.youtube.com")
            print(f"Page title for profile {profile_name}: {driver.title}")  # Should reflect logged-in user
            driver.quit()
        except Exception as e:
            print(f"Failed to connect to Chrome with profile {profile_name}: {e}")


if __name__ == "__main__":
    rotate_through_profiles()
