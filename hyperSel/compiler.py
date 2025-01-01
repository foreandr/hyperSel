import subprocess
import datetime
import os

def modify_file_for_trial(file_name, free_trial, trial_duration_minutes=10000, email="foreandr@gmail.com"):
    """
    Modifies the given Python file to include free trial logic if free_trial is True.

    :param file_name: The Python file to modify.
    :param free_trial: Boolean to decide whether to add free trial code.
    :param trial_duration_minutes: Trial duration in minutes.
    :param email: Contact email to display when the trial ends.
    """
    if free_trial:
        # Record the compilation time
        compile_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        trial_code = f"""
# Free Trial Logic
import datetime
import customtkinter as ctk
import sys

# Compilation time
compile_time_str = "{compile_time}"  # Compilation time recorded at compile time
compile_time = datetime.datetime.strptime(compile_time_str, "%Y-%m-%d %H:%M:%S")

# Trial duration in minutes
trial_duration = {trial_duration_minutes}  # Configurable trial duration
trial_end_time = compile_time + datetime.timedelta(minutes=trial_duration)

# Check trial status
current_time = datetime.datetime.now()
elapsed_time = (current_time - compile_time).total_seconds()
elapsed_minutes = elapsed_time / 60

if current_time > trial_end_time:
    # Create a customtkinter GUI to inform the user
    def trial_expired_popup():
        root = ctk.CTk()
        root.title("Trial Expired")
        root.geometry("500x300")
        
        # Details of the trial expiration
        details = (
            "Your free trial has ended.\\n\\n"
            f"Compilation Time: {{compile_time_str}}\\n"
            f"Current Time: {{current_time.strftime('%Y-%m-%d %H:%M:%S')}}\\n"
            f"Elapsed Time: {{elapsed_minutes:.2f}} minutes\\n"
            f"Trial Duration: {{trial_duration}} minutes\\n\\n"
            f"Contact {email} for the full version."
        )
        
        label = ctk.CTkLabel(
            root,
            text=details,
            font=("Arial", 12),
            wraplength=450,
            justify="left"
        )
        label.pack(pady=20)
        
        button = ctk.CTkButton(root, text="Close", command=root.destroy)
        button.pack(pady=20)
        
        root.mainloop()
    
    trial_expired_popup()
    sys.exit()
"""
        print("BEGIN: Adding free trial logic to the file.")
        with open(file_name, "r+") as f:
            original_code = f.read()
            f.seek(0, 0)
            f.write(trial_code + "\n" + original_code)
        print(f"Trial logic added successfully with the following details:")
        print(f"- Compilation Time: {compile_time}")
        print(f"- Trial Duration: {trial_duration_minutes} minutes")
        print(f"- Contact Email: {email}")
        return original_code  # Return the original content for restoration later
    else:
        print("Free trial logic not added since free_trial is False.")
        return None


def restore_original_file(file_name, original_code):
    """
    Restores the original file content after compilation.

    :param file_name: The file to restore.
    :param original_code: The original content of the file.
    """
    if original_code:
        print("Restoring the original file content...")
        with open(file_name, "w") as f:
            f.write(original_code)
        print("File restored successfully.")


def run_pyinstaller(file_name="./foo.py", is_gui=False, free_trial=True):
    """
    Runs the PyInstaller command based on the provided file name, GUI option, and free trial.

    :param file_name: The name of the Python file to compile (default: './foo.py').
    :param is_gui: Boolean indicating if the GUI flag (--noconsole) should be used (default: False).
    :param free_trial: Boolean indicating free trial status (default: True).
    """
    if not file_name.endswith(".py"):
        print("Error: File must be a Python script with a '.py' extension.")
        return

    # Add free trial logic to the file if necessary
    original_code = modify_file_for_trial(file_name, free_trial)

    # Determine output file name
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    if free_trial:
        output_name = f"{base_name}_trial"
    else:
        output_name = base_name

    # Print debug information
    print(f"File Name: {file_name}")
    print(f"Output Name: {output_name}")
    print(f"Is GUI: {is_gui}")
    print(f"Free Trial: {free_trial}")

    # Build the PyInstaller command
    command = [
        "pyinstaller",
        "--onefile",
        file_name,
        "--name",
        output_name
    ]
    if is_gui:
        command.append("--noconsole")

    try:
        # Run the command and capture output
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        # Print output and errors
        print("PyInstaller Output:")
        print(stdout)
        if stderr:
            print("PyInstaller Errors:", stderr)
    except FileNotFoundError:
        print("Error: PyInstaller not found. Ensure it is installed in your environment.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Restore the original file content
        restore_original_file(file_name, original_code)


if __name__ == "__main__":
    run_pyinstaller(file_name="./foo.py", is_gui=False, free_trial=False)
