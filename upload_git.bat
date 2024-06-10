@echo off

REM Enable command echoing for debugging
setlocal EnableDelayedExpansion
echo Starting the GitHub commit and push script...

REM Add all changes to the staging area
echo Adding changes to the staging area...
git add .
if %errorlevel% neq 0 (
    echo Failed to add changes.
    exit /b %errorlevel%
)

REM Commit the changes with a message
set /p commit_message="Enter commit message: "
if not defined commit_message (
    echo Commit message is required.
    exit /b 1
)
echo Committing changes...
git commit -m "%commit_message%"
if %errorlevel% neq 0 (
    echo Failed to commit changes.
    exit /b %errorlevel%
)

REM Push the changes to the remote repository
echo Pushing changes to GitHub...
git push
if %errorlevel% neq 0 (
    echo Failed to push changes to GitHub.
    exit /b %errorlevel%
)

echo GitHub commit and push completed successfully.
endlocal
echo Script completed.
pause
