import subprocess
import sys
import webbrowser

# This launcher is used for PyInstaller packaging.
def main():
    # Launch Streamlit app in a subprocess
    try:
        subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "main.py", "--server.headless=true"
        ])
        # Open browser automatically
        webbrowser.open("http://localhost:8501")
    except Exception as e:
        print(f"Failed to launch app: {e}")

if __name__ == "__main__":
    main()
