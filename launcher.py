import urllib.request
import tempfile
import importlib.util
import os
import sys
import zipfile

VAULT_URL = "https://raw.githubusercontent.com/ChaoticCrispy/Manager/main/vault.py"
THEMES_ZIP_URL = "https://github.com/ChaoticCrispy/Manager/archive/refs/heads/main.zip"

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
        temp_dir = tempfile.gettempdir()
        vault_path = os.path.join(temp_dir, "vault_runtime.py")
        zip_path = os.path.join(temp_dir, "themes.zip")

        download_file(VAULT_URL, vault_path)
        download_file(THEMES_ZIP_URL, zip_path)
        extract_themes(zip_path, temp_dir)

        spec = importlib.util.spec_from_file_location("vault", vault_path)
        vault_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vault_module)

    except ModuleNotFoundError as e:
        print("[ERROR] Required module is missing:", e)
        print("Try running: pip install customtkinter")
        input("Press Enter to exit.")
        sys.exit(1)

    except Exception as e:
        print(f"[ERROR] Failed to load vault from GitHub:\n{e}")
        input("Press Enter to exit.")
        sys.exit(1)

if __name__ == "__main__":
    download_and_run()
