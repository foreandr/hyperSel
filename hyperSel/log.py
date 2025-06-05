import os
import inspect
import datetime
import json
from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree as ET
import datetime
import sys
import re
import datetime
import time

GLOBAL_CHECKPOINT = 0

def print_colored(text, color="red"):
    colors = {
        "black": "\033[30m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }

    color_code = colors.get(color.lower(), colors["red"])  # Default to red if color is not found
    print(f"{color_code}{text}{colors['reset']}")


def check_file_exists(file_path):
    return os.path.exists(file_path)

def check_and_save_dir(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        
def log_function(
    log_string,
    msg_type='test',
    session_user="",
    function_name=None,
    verbose=True,
    file_name=None,
    new_line=False,
    max_retries=5,
    retry_delay=0.1
):
    

    log_string = str(log_string)
    split_log_string = '\n'.join(log_string.split(", "))
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.strftime('%Y-%m-%d')

    # Auto-detect caller if function_name not explicitly provided
    if function_name is None:
        stack = inspect.stack()
        if len(stack) > 1:
            function_name = stack[1].function
        else:
            function_name = "<unknown>"

    if verbose:
        err_string = f"[{current_datetime}][{msg_type}][{function_name}][{session_user}]-{split_log_string}\n"
        if new_line:
            err_string += "\n"
    else:
        err_string = f"{split_log_string}\n"
        if new_line:
            err_string += "\n"

    day, mon, yea = current_date.split("-")[2], current_date.split("-")[1], current_date.split("-")[0]
    location_logger_dateless = f"{yea}/{mon}/{day}"
    location_logger = f"{yea}/{mon}/{day}/{current_date}"

    if msg_type == "error":
        print(f"[{function_name}]==========LOGGING AN ERROR PLS NOTICE!=========")

    log_written = False
    paths_to_try = ['./logs/', '../logs/']

    for path_base in paths_to_try:
        try:
            check_and_save_dir(f'{path_base}{location_logger_dateless}')
            target_file = f'{path_base}{file_name}.txt' if file_name else f'{path_base}{location_logger}.txt'

            for attempt in range(max_retries):
                try:
                    with open(target_file, 'a+', encoding='utf-8') as f:
                        f.write(err_string)
                    log_written = True
                    break
                except Exception as e:
                    time.sleep(retry_delay)
            
            if log_written:
                return 1
        except Exception:
            continue  # Try next path

    # If nothing succeeded
    print(f"[{function_name}] ❌ Failed to write to log after retries.")
    return 0

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


def log_data(data_object, file_name='data', unique_criterion=None, verbose=False, max_age_days=None, file_type='json'):
    """
    Logs data objects to a specified file type in a 'logs' directory, avoiding duplicates based on a unique criterion.
    Adds 'original_scrape_time' when an entry is first added, which remains unchanged. 'recent_scrape_time' is updated each time an entry is logged.
    Optionally deletes entries older than a specified number of days.
    
    :param data_object: A dictionary or list of dictionaries to be logged.
    :param file_name: The name of the file for logging (default: 'crawl_data').
    :param unique_criterion: The field used to check for duplicates (e.g., 'url').
    :param verbose: If True, prints information on logging operations.
    :param max_age_days: If specified, deletes entries older than this number of days. None means no deletions.
    :param file_type: The type of file to save the data in ('json', 'csv', 'txt', 'xml').
    """
    # Define the base directory and file path
    base_dir = "./logs/"
    file_path = os.path.join(base_dir, f"{file_name}.{file_type.lower()}")

    # Ensure data_object is a list for consistent handling
    if isinstance(data_object, dict):
        data_object = [data_object]  # Wrap single dict in list

    # Deduplicate data_object based on unique_criterion
    unique_data = []
    seen_criteria = set()
    for item in data_object:
        # Create a copy without 'recent_scrape_time' and 'original_scrape_time' for comparison
        item_copy = {k: v for k, v in item.items() if k not in ["recent_scrape_time", "original_scrape_time"]}
        
        # Determine the unique key based on unique_criterion or entire item
        unique_key = item_copy.get(unique_criterion) if unique_criterion else json.dumps(item_copy, sort_keys=True)
        
        # Only add to unique_data if this unique_key hasn't been seen
        if unique_key not in seen_criteria:
            seen_criteria.add(unique_key)
            unique_data.append(item)

    # Update data_object with the deduplicated list
    data_object = unique_data

    # Set scrape times
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for item in data_object:
        if "original_scrape_time" not in item:
            item["original_scrape_time"] = current_time
        item["recent_scrape_time"] = current_time

    # Ensure the logs directory exists
    os.makedirs(base_dir, exist_ok=True)

    # Load existing data and remove old entries based on file type
    if file_type.lower() == 'json':
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []
    elif file_type.lower() == 'csv':
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_data = [row for row in reader]
        else:
            existing_data = []
    elif file_type.lower() == 'txt':
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = [json.loads(line) for line in f]
        else:
            existing_data = []
    elif file_type.lower() == 'xml':
        if os.path.exists(file_path):
            tree = ET.parse(file_path)
            root = tree.getroot()
            existing_data = [{child.tag: child.text for child in entry} for entry in root]
        else:
            existing_data = []

    # Remove old entries if max_age_days is set
    if max_age_days is not None:
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
        existing_data = [
            entry for entry in existing_data
            if datetime.datetime.strptime(entry.get("recent_scrape_time", ""), '%Y-%m-%d %H:%M:%S') >= cutoff_date
        ]

    # Deduplicate with existing data
    new_entries = []
    for item in data_object:
        is_duplicate = False

        for existing_item in existing_data:
            existing_copy = {k: v for k, v in existing_item.items() if k not in ["recent_scrape_time", "original_scrape_time"]}
            item_copy = {k: v for k, v in item.items() if k not in ["recent_scrape_time", "original_scrape_time"]}

            if unique_criterion:
                if existing_copy.get(unique_criterion) == item_copy.get(unique_criterion):
                    existing_item["recent_scrape_time"] = item["recent_scrape_time"]
                    is_duplicate = True
                    break
            else:
                if existing_copy == item_copy:
                    existing_item["recent_scrape_time"] = item["recent_scrape_time"]
                    is_duplicate = True
                    break

        if not is_duplicate:
            new_entries.append(item)

    # Update and save data in the specified file format
    updated_data = existing_data + new_entries
    if file_type.lower() == 'json':
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=4)
    elif file_type.lower() == 'csv':
        file_exists = os.path.exists(file_path)
        with open(file_path, 'w' if not file_exists else 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=updated_data[0].keys())
            if not file_exists:
                writer.writeheader()
            writer.writerows(new_entries)
    elif file_type.lower() == 'txt':
        with open(file_path, 'a', encoding='utf-8') as f:
            for item in new_entries:
                f.write(json.dumps(item) + '\n')
    elif file_type.lower() == 'xml':
        root = ET.Element("root")
        for entry in updated_data:
            entry_elem = ET.SubElement(root, "entry")
            for key, value in entry.items():
                child = ET.SubElement(entry_elem, key)
                child.text = str(value)
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)

    if verbose:
        print(f"Data logged to {file_name}.{file_type.lower()} as {len(new_entries)} new entries.")

def checkpoint(pause=False, str_to_print=None):
    global GLOBAL_CHECKPOINT
    frame = inspect.currentframe().f_back
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_file = inspect.getfile(frame)
    caller_function_name = frame.f_code.co_name

    log_str = (
        f"\n\033[92m[CHECKPOINT:{GLOBAL_CHECKPOINT}]"
        f"\n[TIME:{current_time}][LINE:{frame.f_lineno}]\033[0m"
        f"\n[FILE:{current_file}]"
        f"\n[FUNC:{caller_function_name}]"
        
    )
    
    print(f"{log_str}")


    if str_to_print is not None:
        print(f"\033[92m{str_to_print}\033[0m")  # Print message in green

    if pause:
        input("\033[92mSTOPPING UNTIL YOU TYPE SOMETHIN\033[0m")

    GLOBAL_CHECKPOINT += 1

def safe_print(*args, sep=" ", end="\n", flush=False, color=False, logging=True):
    """
    safe_print that never crashes and formats floats nicely.
    • Tries stdout, stderr, then file.
    • UTF-8 safe. Removes ANSI and emojis for file fallback.
    """

    def format_arg(x):
        if isinstance(x, float):
            return f"{x:.6f}"  # Decimal only
        return str(x)

    try:
        text = sep.join(map(format_arg, args)) + end
    except Exception as e:
        text = f"[safe_print format error]: {e}\n"

    try:
        if color:
            text = f"\033[92m{text}\033[0m"
        sys.stdout.write(text)
        if flush:
            sys.stdout.flush()
        return
    except Exception:
        pass

    try:
        sys.__stderr__.write(text)
        if flush:
            sys.__stderr__.flush()
        return
    except Exception:
        pass

    # Optional custom log pipeline (only if it exists)
    try:
        if logging:
            log_function(log_string=text)
    except Exception:
        pass



if __name__ == "__main__":

    pass