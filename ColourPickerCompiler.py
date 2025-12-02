# Script to build ColourPicker.py into an .exe using PyInstaller

import os
import subprocess
import sys
import shutil

def build_exe():
    script = "ColourPicker.py"
    exe_name = "ColourPicker.exe"
    script_path = os.path.join(os.path.dirname(__file__), script)
    dist_path = os.path.join(os.path.dirname(__file__), "dist", exe_name)
    target_path = os.path.join(os.path.dirname(__file__), exe_name)

    # Remove previous build/dist if they exist
    for folder in ["build", "dist"]:
        folder_path = os.path.join(os.path.dirname(__file__), folder)
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
            except Exception:
                pass
    # Remove old exe if exists
    if os.path.exists(target_path):
        os.remove(target_path)
    # Build with PyInstaller (must be installed and on PATH)
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "ColourPicker",
        script_path
    ]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("PyInstaller is not installed or not found. Install it with 'pip install pyinstaller'.")
        return
    except subprocess.CalledProcessError:
        print("PyInstaller build failed.")
        return

    # Move the exe to the script directory
    if os.path.exists(dist_path):
        shutil.move(dist_path, target_path)
        print(f"Build complete. EXE is at: {target_path}")
    else:
        print("Build failed: EXE not found in dist folder.")

if __name__ == "__main__":
    build_exe()
