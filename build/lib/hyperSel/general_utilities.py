#AGAIN
import subprocess
import psutil
import string
import random
from screeninfo import get_monitors
import time
from difflib import SequenceMatcher

try:
    from . import colors_utilities

except:
    import colors_utilities



def get_similarity_ratio(str1, str2):
    """
    Returns the similarity ratio between two strings using difflib's SequenceMatcher.
    
    :param str1: First string to compare
    :param str2: Second string to compare
    :return: Similarity ratio as a float between 0.0 and 1.0
    """
    return SequenceMatcher(None, str1, str2).ratio()

def get_display_dimensions():
    # Get the primary monitor or the first monitor in the list
    monitor = get_monitors()[0]
    
    # Return width and height of the monitor
    return {"width": monitor.width, "height": monitor.height}

def get_all_alphabet_chars():
    alphabet = list(string.ascii_lowercase)
    return alphabet

def get_ram_percentage():
    return int(str(psutil.virtual_memory().percent).split(".")[0])

def ram_under_threshold(threshold):
    if get_ram_percentage() <= threshold:
        return True
    return False

def random_pause(n):
    # Generate a random float between 0 and n
    pause_time = random.uniform(0, n)
    
    # Pause the program for the generated random time
    time.sleep(pause_time)
    
    # Optional: Return the pause time if you want to track it
    return pause_time


def list_chrome_instances():
    chrome_processes = []
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == 'chrome.exe':
            chrome_processes.append(process.info)
    return chrome_processes

def kill_chrome_instances():
    '''NOTE: ASSUMES WINDOWS'''
    try:
        # Run the command to kill Chrome instances
        result = subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True, text=True, check=True)
        colors_utilities.c_print(text="KILLED ALL CHROME INSTANCES", color='green')

    except subprocess.CalledProcessError as e:
        colors_utilities.c_print(text=f"Command failed with return code {e.returncode}", color='red')
        colors_utilities.c_print(text=f"Error output: {e.stderr}", color='red')
    except FileNotFoundError:
        colors_utilities.c_print(text="The 'taskkill' command was not found. Is it available on your system?", color='red')
        
def kill_process_by_pid(pid):
    try:
        result = subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        colors_utilities.c_print(text=f"Command failed with return code {e.returncode}", color='red')
        colors_utilities.c_print(text=f"Error output: {e.stderr}", color='red')
    except FileNotFoundError:
         colors_utilities.c_print(text="The 'taskkill' command was not found. Is it available on your system?", color='red')
    except Exception as e:   
        colors_utilities.c_print(text=f"An error occurred while trying to kill process with PID: {pid} - {e}", color='red')
        
        
def generate_random_user_agent():
    # Define possible components for user agents
    os_list = [
        "Windows NT 10.0; Win64; x64",
        "Macintosh; Intel Mac OS X 10_15_7",
        "X11; Linux x86_64"
    ]
    
    browser_list = [
        ("Chrome/{version}", "AppleWebKit/537.36 (KHTML, like Gecko)"),
        ("Firefox/{version}", "Gecko/20100101"),
        ("Safari/{version}", "AppleWebKit/537.36 (KHTML, like Gecko) Version/{version}")
    ]
    
    # Define versions
    chrome_versions = [f"{major}.{minor}.{patch}.0" for major in range(90, 105) for minor in range(0, 100, 10) for patch in range(0, 5000, 100)]
    firefox_versions = [f"{major}.{minor}" for major in range(70, 100) for minor in range(0, 10)]
    safari_versions = [f"{major}.{minor}" for major in range(15, 18) for minor in range(0, 10)]
    
    versions = {
        'Chrome': chrome_versions,
        'Firefox': firefox_versions,
        'Safari': safari_versions
    }
    
    # Choose random components
    os = random.choice(os_list)
    browser_name, browser_template = random.choice(browser_list)
    version = random.choice(versions[browser_name.split('/')[0]])
    
    # Format the user-agent string
    user_agent = f"Mozilla/5.0 ({os}) {browser_template.format(version=version)}"
    
    return user_agent

def data_string_cleaner():
    '''THIS WILL BASICALLY GO THROUGH AND FIX SHIT THAT U WANT'''

if __name__ == '__main__':
    pass