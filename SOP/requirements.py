import subprocess
import sys

# List of required packages
packages = [
    "google-generativeai",
    "markdownify==0.11.6",
    "openai>=1.0.0",
    "Pillow==10.2.0",
    "pyaudio",
    "python-dotenv==1.0.0",
    "python-wordpress-xmlrpc==2.3",
    "requests==2.31.0",
    "speechrecognition",
    "streamlit==1.32.0",
    "tabulate",
    "urllib3",
    "whisper"
]

# Extra index URL for torch/whisper (for GPU support)
extra_index_url = "--extra-index-url https://download.pytorch.org/whl/cu118"

# Function to install packages
def install_packages(package_list, extra_url=None):
    for package in package_list:
        cmd = [sys.executable, "-m", "pip", "install", package]
        if extra_url and "whisper" in package:
            cmd += [extra_url]
        subprocess.check_call(cmd)

if __name__ == "__main__":
    install_packages(packages, extra_url=extra_index_url)
