# PowerShell script to package the Streamlit app as a Windows executable using PyInstaller
# Usage: Run this script in PowerShell: ./packaging/package_app.ps1

# Ensure PyInstaller is installed
pip install pyinstaller

# Clean previous builds
Remove-Item -Recurse -Force dist, build, *.spec -ErrorAction SilentlyContinue

# Package the launcher script
pyinstaller --noconfirm --onefile --windowed packaging/desktop_launcher.py

Write-Host "Packaging complete! Find your executable in the 'dist' folder."
