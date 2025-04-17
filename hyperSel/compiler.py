import subprocess
import datetime
import os
import sys


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

        # Inject trial logic that checks if the app has expired based on compile time
        trial_code = f"""
# Free Trial Logic
import datetime
import customtkinter as ctk
import sys

# Compilation time
compile_time_str = "{compile_time}"
compile_time = datetime.datetime.strptime(compile_time_str, "%Y-%m-%d %H:%M:%S")

# Trial duration in minutes
trial_duration = {trial_duration_minutes}
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

        details = (
            "Your free trial has ended.\\n\\n"
            f"Compilation Time: {{compile_time_str}}\\n"
            f"Current Time: {{current_time.strftime('%Y-%m-%d %H:%M:%S')}}\\n"
            f"Elapsed Time: {{elapsed_minutes:.2f}} minutes\\n"
            f"Trial Duration: {{trial_duration}} minutes\\n\\n"
            f"Contact {email} for the full version."
        )

        label = ctk.CTkLabel(
            root, text=details, font=("Arial", 12),
            wraplength=450, justify="left"
        )
        label.pack(pady=20)

        button = ctk.CTkButton(root, text="Close", command=root.destroy)
        button.pack(pady=20)

        root.mainloop()

    trial_expired_popup()
    sys.exit()
"""
        print("BEGIN: Adding free trial logic to the file.")
        with open(file_name, "r+", encoding="utf-8") as f:
            original_code = f.read()
            f.seek(0, 0)
            f.write(trial_code + "\n" + original_code)
        print("Trial logic added successfully with the following details:")
        print(f"- Compilation Time: {compile_time}")
        print(f"- Trial Duration: {trial_duration_minutes} minutes")
        print(f"- Contact Email: {email}")
        return original_code  # For restoring later
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
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(original_code)
        print("File restored successfully.")


def run_pyinstaller(file_name="./foo.py", is_gui=False, free_trial=True, include_folders=None):
    """
    Compiles a Python script into a standalone executable using PyInstaller.
    
    :param file_name: Path to the .py file to compile.
    :param is_gui: If True, suppresses the console window (--noconsole).
    :param free_trial: If True, injects trial logic into the script.
    :param include_folders: List of folder names to include as --add-data.
    """
    if not file_name.endswith(".py"):
        print("❌ Error: File must be a Python script with a '.py' extension.")
        return

    # Inject trial logic if enabled
    original_code = modify_file_for_trial(file_name, free_trial)

    # Generate output name
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    output_name = f"{base_name}_trial" if free_trial else base_name

    # Log basic info
    print(f"\n🔧 Building: {file_name}")
    print(f"🛠️  Output Name: {output_name}")
    print(f"🖼️  GUI Mode: {is_gui}")
    print(f"🔓 Free Trial: {free_trial}")
    print(f"📁 Including Folders: {include_folders or []}")

    # Construct base PyInstaller command
    command = [
        "pyinstaller",
        "--onefile",
        file_name,
        "--name",
        output_name
    ]

    if is_gui:
        command.append("--noconsole")

    # Include additional folders (like data/)
    if include_folders:
        sep = ";" if os.name == "nt" else ":"
        for folder in include_folders:
            if os.path.isdir(folder):
                command.extend(["--add-data", f"{folder}{sep}{os.path.basename(folder)}"])
            else:
                print(f"⚠️  Skipping non-existent folder: {folder}")

    try:
        # Run PyInstaller command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        print("\n📦 PyInstaller Output:")
        print(stdout)
        if stderr:
            print("\n❗ PyInstaller Errors:")
            print(stderr)

    except FileNotFoundError:
        print("❌ PyInstaller not found. Make sure it is installed.")
    except Exception as e:
        print(f"❌ Unexpected error during compilation: {e}")
    finally:
        restore_original_file(file_name, original_code)


# Example usage
if __name__ == "__main__":
    run_pyinstaller(
        file_name="./crawlRealEstate.py",
        is_gui=False,
        free_trial=False,
        include_folders=["data"]  # <-- Add any folders your app depends on
    )
