import os
import sys
import shutil
import subprocess
import venv
import platform

# Paths
venv_dir = ".venv"

# Step 0: Recreate the venv if it exists
if os.path.exists(venv_dir):
    print(f"Removing existing virtual environment at {venv_dir}...")
    shutil.rmtree(venv_dir)

# Step 1: Create new venv
print(f"Creating virtual environment in {venv_dir}...")
venv.create(venv_dir, with_pip=True)

# Step 2: Determine venv python executable
system = platform.system()
if system == "Windows":
    venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
else:
    venv_python = os.path.join(venv_dir, "bin", "python")

# Step 3: Upgrade pip
print("Upgrading pip...")
subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pip"])

# Step 4: Install current package and dependencies
print("Installing the package (editable mode) and dependencies...")
subprocess.check_call([venv_python, "-m", "pip", "install", "-e", "."])

# Step 5: Print activation instructions
print("\nSetup complete!")

# Auto-detect likely shell for activation instructions
shell = os.environ.get("SHELL", "").lower()
powershell = "powershell" in os.environ.get("PSModulePath", "").lower()

if system == "Windows":
    if powershell:
        print(f"Activate with PowerShell: {venv_dir}\\Scripts\\Activate.ps1")
    else:
        print(f"Activate with cmd: {venv_dir}\\Scripts\\activate.bat")
else:
    print(f"Activate with: source {venv_dir}/bin/activate")
