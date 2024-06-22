@echo off
echo Running update_package_num.bat...
call ./update_package_num.bat
if %errorlevel% neq 0 (
    echo Failed to run update_package_num.bat.
    exit /b 1
)

echo Running upload_github.bat...
call ./upload_github.bat
if %errorlevel% neq 0 (
    echo Failed to run upload_github.bat.
    exit /b 1
)

echo Running upload_pypi.bat...
call ./upload_pypi.bat
if %errorlevel% neq 0 (
    echo Failed to run upload_pypi.bat.
    exit /b 1
)

echo All scripts completed successfully.
