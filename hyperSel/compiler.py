print("COMPILER MODULE LOADED")

import os
import shutil
import subprocess

def run_pyinstaller(file_name, is_gui=False, free_trial=False, include_folders=None, build_folder=None, icon_path=None, extra_data_files=None, use_onedir=False):
    if not file_name.endswith(".py"):
        print("❌ Error: File must be a Python script with a '.py' extension.")
        return

    base_name = os.path.splitext(os.path.basename(file_name))[0]
    output_name = f"{base_name}_trial" if free_trial else base_name

    output_dir = os.path.abspath(build_folder) if build_folder else os.getcwd()
    dist_dir = output_dir

    print(f"\n🔧 Building: {file_name}")
    print(f"🛠️  Output Name: {output_name}")
    print(f"📁 Folders to Copy After: {include_folders}")
    print(f"📂 Output Directory: {dist_dir}")
    print(f"📦 Mode: {'--onedir' if use_onedir else '--onefile'}")

    command = [
        "pyinstaller",
        "--onedir" if use_onedir else "--onefile",
        "--distpath", dist_dir,
        "--workpath", os.path.join(dist_dir, "build"),
        "--specpath", dist_dir,
        "--name", output_name,
    ]

    if icon_path:
        abs_icon_path = os.path.abspath(icon_path)
        if os.path.isfile(abs_icon_path):
            command.extend(["--icon", abs_icon_path])
        else:
            print(f"⚠️ Icon file not found: {abs_icon_path}")

    if is_gui:
        command.append("--noconsole")

    # ✅ Include extra files
    if extra_data_files:
        for data_file in extra_data_files:
            abs_path = os.path.abspath(data_file)
            if os.path.isfile(abs_path):
                sep = ";" if os.name == "nt" else ":"
                command.extend(["--add-data", f"{abs_path}{sep}."])
            else:
                print(f"⚠️ File not found: {abs_path}")

    command.append(os.path.abspath(file_name))

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        print("\n📦 PyInstaller Output:\n", result.stdout)
        if result.returncode != 0:
            print('================================================')
            print("\n❗ PyInstaller Errors:\n", result.stderr)
            print("=============================================\n")
        else:
            pass
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    if include_folders:
        for folder in include_folders:
            abs_source = os.path.abspath(folder)
            if os.path.isdir(abs_source):
                dest_folder = os.path.join(dist_dir, os.path.basename(abs_source))
                try:
                    if os.path.exists(dest_folder):
                        shutil.rmtree(dest_folder)
                    shutil.copytree(abs_source, dest_folder)
                    print(f"📁 Folder copied: {abs_source} -> {dest_folder}")
                except Exception as e:
                    print(f"❌ Failed to copy folder '{folder}': {e}")
            else:
                print(f"⚠️ Skipping non-existent folder: {abs_source}")

    print(f"\n✅ Compilation complete! Output is in: {dist_dir}")
