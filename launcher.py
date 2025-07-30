import importlib.util
import os
import sys
import urllib.request

VAULT_URL = "https://raw.githubusercontent.com/your-username/your-repo/main/vault.py"
VAULT_SCRIPT = "vault_temp.py"

def download_and_run():
    try:
        print("[*] Downloading latest vault script...")
        urllib.request.urlretrieve(VAULT_URL, VAULT_SCRIPT)
    except Exception as e:
        print(f"[!] Failed to download {VAULT_SCRIPT}: {e}")
        sys.exit(1)

    try:
        spec = importlib.util.spec_from_file_location("vault", VAULT_SCRIPT)
        vault_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vault_module)
    except Exception as e:
        print(f"[!] Failed to run {VAULT_SCRIPT}:\n{e}")
        sys.exit(1)
    finally:
        try:
            os.remove(VAULT_SCRIPT) 
        except Exception:
            pass

if __name__ == "__main__":
    download_and_run()
