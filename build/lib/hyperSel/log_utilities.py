import os
import inspect
import datetime

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