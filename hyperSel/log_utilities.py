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

import os
import json
import datetime

import os
import json
import datetime

import os
import json
import datetime

import os
import json
import csv
import xml.etree.ElementTree as ET
import datetime

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
        unique_key = item_copy.get(unique_criterion) if unique_criterion else frozenset(item_copy.items())
        
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

def test_locally():
    # NOT INSTALLED IN THE ACTUAL LIBRARY
    from faker import Faker

    # Initialize Faker
    fake = Faker()

    def generate_fake_data_object(n):
        data_object = [{
            'name': "Andre",
            #'age': fake.random_int(min=18, max=90),
            #'email': fake.email(),
            #'address': fake.address(),
            #'phone_number': fake.phone_number(),
            #'company': fake.company(),
            #'job_title': fake.job(),
            # 'date_of_birth': fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat()
        } for _ in range(n)]
        data_object.append({"name":"Andr"})
        return data_object
    
    
    n = 10  # Set the desired number of entries
    data_object = generate_fake_data_object(n)

    log_data(data_object,verbose=True, file_type='xml')

if __name__ == "__main__":
    test_locally()
    pass