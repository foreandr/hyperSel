import subprocess
import psutil
def get_ram_percentage():
    return int(str(psutil.virtual_memory().percent).split(".")[0])

def ram_under_threshold(threshold):
    if get_ram_percentage() <= threshold:
        return True
    return False

def list_chrome_instances():
    chrome_processes = []
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == 'chrome.exe':
            chrome_processes.append(process.info)
    return chrome_processes

def kill_chrome_instances():
    try:
        # Run the command to kill Chrome instances
        result = subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True, text=True, check=True)
        # print("Command output:", result.stdout)
        # print("Command error (if any):", result.stderr)
        print("KILLED ALL CHROME INSTANCES")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
        print("Error output:", e.stderr)
    except FileNotFoundError:
        print("The 'taskkill' command was not found. Is it available on your system?")
        
def kill_process_by_pid(pid):
    try:
        # Run the command to kill the process with the given PID
        result = subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True, text=True, check=True)
        # Print the command output and error (if any)
        print("Command output:", result.stdout)
        print("Command error (if any):", result.stderr)
        print(f"Killed process with PID: {pid}")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
        print("Error output:", e.stderr)
    except FileNotFoundError:
        print("The 'taskkill' command was not found. Is it available on your system?")
    except Exception as e:
        print(f"An error occurred while trying to kill process with PID: {pid} - {e}")    