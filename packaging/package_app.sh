#!/bin/bash
# Bash script to package the Streamlit app as a Mac/Linux executable using PyInstaller
# Usage: Run this script in your terminal: ./packaging/package_app.sh

# Ensure PyInstaller is installed
pip install pyinstaller

# Clean previous builds
rm -rf dist build *.spec

# Package the launcher script
pyinstaller --noconfirm --onefile --windowed packaging/desktop_launcher.py

echo "Packaging complete! Find your executable in the 'dist' folder."
