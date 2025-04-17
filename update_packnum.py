import re

def increment_version(version):
    major, minor = map(int, version.strip().split('.'))

    # Increment minor and skip x.10, x.20, x.30, etc.
    minor += 1
    if minor % 10 == 0:
        minor += 1

    return f"{major}.{minor}"

def update_version_in_setup():
    setup_file = './setup.py'

    with open(setup_file, 'r') as file:
        content = file.read()

    # 🛠 Match numeric version (unquoted like: version=6.9)
    version_pattern = r'version\s*=\s*(\d+\.\d+)'
    match = re.search(version_pattern, content)

    if match:
        current_version = match.group(1)
        new_version = increment_version(current_version)

        # ✅ Replace with raw numeric, not string
        updated_content = re.sub(
            version_pattern,
            f'version={new_version}',
            content
        )

        with open(setup_file, 'w') as file:
            file.write(updated_content)

        print(f"✅ Version updated from {current_version} to {new_version}.")
    else:
        print("❌ Version pattern not found in setup.py.")

if __name__ == "__main__":
    update_version_in_setup()
