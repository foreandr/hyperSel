import subprocess
import datetime
import os
import sys


def modify_file_for_trial(file_name, free_trial, trial_duration_minutes=10000, email="foreandr@gmail.com"):
    """
    Modifies the given Python file to include free trial logic if free_trial is True.
    """
    if free_trial:
        compile_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Inject trial code at the top of the file
        trial_code = f"""
# Free Trial Logic
import datetime
import customtkinter as ctk
import sys

compile_time_str = "{compile_time}"
compile_time = datetime.datetime.strptime(compile_time_str, "%Y-%m-%d %H:%M:%S")
trial_duration = {trial_duration_minutes}
trial_end_time = compile_time + datetime.timedelta(minutes=trial_duration)
current_time = datetime.datetime.now()
elapsed_time = (current_time - compile_time).total_seconds()
elapsed_minutes = elapsed_time / 60

if current_time > trial_end_time:
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

        label = ctk.CTkLabel(root, text=details, font=("Arial", 12), wraplength=450, justify="left")
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
        print("Trial logic added successfully:")
        print(f"- Compilation Time: {compile_time}")
        print(f"- Trial Duration: {trial_duration_minutes} minutes")
        print(f"- Contact Email: {email}")
        return original_code
    else:
        print("Free trial logic not added since free_trial is False.")
        return None


def restore_original_file(file_name, original_code):
    """
    Restores the original file content after compilation.
    """
    if original_code:
        print("Restoring the original file content...")
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(original_code)
        print("File restored successfully.")


def run_pyinstaller(file_name="./foo.py", is_gui=False, free_trial=True, include_folders=None, build_folder="WebWeb"):
    """
    Compiles a Python script into a standalone executable using PyInstaller.
    All output files will be placed inside the folder specified by `build_folder`.
    
    :param file_name: Path to the .py file to compile.
    :param is_gui: If True, suppresses the console window (--noconsole).
    :param free_trial: If True, injects trial logic into the script.
    :param include_folders: List of folders to bundle with the executable.
    :param build_folder: The folder where all build outputs will go (default: "WebWeb").
    """
    if not file_name.endswith(".py"):
        print("❌ Error: File must be a Python script with a '.py' extension.")
        return

    # Add trial logic if enabled
    original_code = modify_file_for_trial(file_name, free_trial)

    # Output name based on base filename
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    output_name = f"{base_name}_trial" if free_trial else base_name

    # Create output folder if it doesn't exist
    os.makedirs(build_folder, exist_ok=True)

    print(f"\n🔧 Building: {file_name}")
    print(f"🛠️  Output Name: {output_name}")
    print(f"🖼️  GUI Mode: {is_gui}")
    print(f"🔓 Free Trial: {free_trial}")
    print(f"📁 Including Folders: {include_folders or []}")
    print(f"📂 Output Directory: {build_folder}")

    # Base pyinstaller command
    command = [
        "pyinstaller",
        "--onefile",
        "--distpath", build_folder,
        "--workpath", os.path.join(build_folder, "build"),
        "--specpath", build_folder,
        "--name", output_name,
        file_name
    ]

    if is_gui:
        command.append("--noconsole")

    # Add folders with --add-data
    if include_folders:
        sep = ";" if os.name == "nt" else ":"
        for folder in include_folders:
            if os.path.isdir(folder):
                command.extend(["--add-data", f"{folder}{sep}{os.path.basename(folder)}"])
            else:
                print(f"⚠️  Skipping non-existent folder: {folder}")

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        print("\n📦 PyInstaller Output:")
        print(stdout)
        if stderr:
            print("\n❗ PyInstaller Errors:")
            print(stderr)

        print(f"\n✅ Compilation complete! Output is in: {build_folder}/")

    except FileNotFoundError:
        print("❌ PyInstaller not found. Install it with 'pip install pyinstaller'")
    except Exception as e:
        print(f"❌ Unexpected error during build: {e}")
    finally:
        restore_original_file(file_name, original_code)


# Example usage
if __name__ == "__main__":
    run_pyinstaller(
        file_name="./crawlRealEstate.py",
        is_gui=False,
        free_trial=False,
        include_folders=["data"],         # Folders you want to bundle
        build_folder="WebWeb"             # Folder where .exe and files will go
    )
