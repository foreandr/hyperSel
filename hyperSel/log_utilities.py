import os
import inspect
import datetime
import json
from bs4 import BeautifulSoup

try:
    from . import colors_utilities
except:
    import colors_utilities


GLOBAL_CHECKPOINT = 0

def check_file_exists(file_path):
    return os.path.exists(file_path)

def check_and_save_dir(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        
def log_function(log_string, msg_type='test', session_user="", function_name=""):
    log_string = str(log_string)
    
    # Split the log_string by ", " and join it with newline characters
    split_log_string = '\n'.join(log_string.split(", "))
    
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.strftime('%Y-%m-%d')
    err_string = f"[{current_datetime}][{msg_type}][{function_name}][{session_user}]-{split_log_string}\n" 
    
    day = current_date.split("-")[2]
    mon = current_date.split("-")[1]
    yea = current_date.split("-")[0]
    location_logger_dateless = f"{yea}/{mon}/{day}"
    location_logger = f"{yea}/{mon}/{day}/{current_date}"
    
    if msg_type == "error":      
        colors_utilities.c_print(text=f"[{function_name}]==========LOGGING AN ERROR PLS NOTICE!========= ", color='red')
            
    try:
        file = f"./logs/"
        check_and_save_dir(f'{file}{location_logger_dateless}')
        with open(f'{file}{location_logger}.txt', 'a+', encoding='utf-8') as f:
            f.write(err_string) 
    except:
        file = f"../logs/"
        check_and_save_dir(f'{file}{location_logger_dateless}')
        with open(f'{file}{location_logger}.txt', 'a+', encoding='utf-8') as f:
            f.write(err_string)

def load_file_as_soup(file_path):
    """
    Load a text file from the given path and parse it as a BeautifulSoup object.
    
    Parameters:
        file_path (str): The path to the text file.
        
    Returns:
        BeautifulSoup: Parsed content of the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        soup = BeautifulSoup(content, 'html.parser')  # Adjust parser as needed
        return soup
    except Exception as e:
        print(f"Error loading file: {e}")
        return None


def log_data(data_object, file_name='crawl_data.json', unique_criterion=None, verbose=False):
    """
    Logs data objects to a JSON file in a 'logs' directory, avoiding duplicates based on a unique criterion.
    Updates 'recent_scrape_time' for existing entries with the same unique criterion.
    
    :param data_object: A dictionary or list of dictionaries to be logged.
    :param file_name: The name of the JSON file for logging (default: 'crawl_data.json').
    :param unique_criterion: The field used to check for duplicates (e.g., 'url').
    :param verbose: If True, prints information on logging operations.
    """
    # Define the base directory and log path
    base_dir = "./logs/"
    log_path = os.path.join(base_dir, file_name)

    # Ensure the logs directory exists
    try:
        check_and_save_dir(base_dir)
    except:
        base_dir = "../logs/"
        log_path = os.path.join(base_dir, file_name)
        check_and_save_dir(base_dir)

    # Ensure data_object is a list for consistent handling
    if isinstance(data_object, dict):
        data_object = [data_object]  # Wrap single dict in list

    # Add 'recent_scrape_time' to each data object
    recent_scrape_time = datetime.datetime.now().isoformat()
    for item in data_object:
        item["recent_scrape_time"] = recent_scrape_time

    # Load existing data from the JSON file if it exists
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []  # Start fresh if file is empty or corrupt
    else:
        existing_data = []

    # Backup existing log file
    if os.path.exists(log_path):
        backup_path = log_path + '.bak'
        with open(log_path, 'r', encoding='utf-8') as original, open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(original.read())
        if verbose:
            print(f"Backup of {file_name} created at {backup_path}")

    # Process new data with deduplication based on unique_criterion
    new_entries = []
    for item in data_object:
        is_duplicate = False

        if unique_criterion:
            # Check if item with same unique criterion value exists
            for existing_item in existing_data:
                if existing_item.get(unique_criterion) == item.get(unique_criterion):
                    # Update 'recent_scrape_time' for existing entry
                    existing_item["recent_scrape_time"] = item["recent_scrape_time"]
                    is_duplicate = True
                    break

        # Append item if it's not a duplicate
        if not is_duplicate:
            new_entries.append(item)

    # Append new entries to existing data
    updated_data = existing_data + new_entries

    # Write the updated data back to the log file
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=4)

    if verbose:
        if new_entries:
            print(f"Logged {len(new_entries)} new entries to {file_name}.")
        else:
            print("No new entries added; only updated existing entries.")


def checkpoint(pause=False, str_to_print=None):
    global GLOBAL_CHECKPOINT
    # Get the current frame and then the caller's frame
    frame = inspect.currentframe().f_back
    
    # Get the current timestamp
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get the file name of the calling function
    current_file = inspect.getfile(frame)
    
    # Get the name of the calling function
    caller_function_name = frame.f_code.co_name
    
    # Print the file, line number, function name, GLOBAL_CHECKPOINT, and current timestamp
    log_str = f"[CHECKPOINT:{GLOBAL_CHECKPOINT}][FILE:{current_file}][FUNC:{caller_function_name}][TIME:{current_time}][LINE:{frame.f_lineno}]"
    colors_utilities.c_print(text=log_str, color="cyan")

    if str_to_print != None:
        colors_utilities.c_print(text=str_to_print, color="cyan")

    if pause:
        input("STOPPING UNTIL YOU TYPE SOMETHIN")

    # Increment the global checkpoint
    GLOBAL_CHECKPOINT += 1

if __name__ == "__main__":
    checkpoint()
    pass