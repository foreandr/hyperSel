from datetime import datetime
import os
from . import colors_utilities


def check_file_exists(file_path):
    return os.path.exists(file_path)

def check_and_save_dir(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        
def log_function(log_string, msg_type='test', session_user="", function_name=""):
    log_string = str(log_string)
    current_datetime = datetime.now()
    current_date = current_datetime.strftime('%Y-%m-%d')
    err_string = f"[{current_datetime}][{msg_type}][{function_name}][{session_user}]-{log_string}\n" 
    
    day = current_date.split("-")[2]
    mon = current_date.split("-")[1]
    yea = current_date.split("-")[0]
    location_logger_dateless = f"{yea}/{mon}/{day}"
    location_logger = f"{yea}/{mon}/{day}/{current_date}"
    
    if msg_type == "error":
        if "CREATE_TABLE" not in err_string or "relation" not in err_string:        
            colors_utilities.c_print(text=f"[{function_name}]==========LOGGING AN ERROR PLS NOTICE!========= ", color='red')
            
    try:
        file = f"./logs/"
        check_and_save_dir(f'{file}{location_logger_dateless}')
        with open(f'{file}{location_logger}.txt', 'a+',encoding='utf-8') as f:
            f.write(err_string) 
    except:
        file = f"../logs/"
        check_and_save_dir(f'{file}{location_logger_dateless}')
        with open(f'{file}{location_logger}.txt', 'a+',encoding='utf-8') as f:
            f.write(err_string)