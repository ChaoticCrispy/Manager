import importlib.util
import os
import sys
import urllib.request

VAULT_URL = "https://raw.githubusercontent.com/your-username/your-repo/main/vault.py"
VAULT_SCRIPT = "vault.py"

try:
    print("Downloading latest vault script...")
    urllib.request.urlretrieve(VAULT_URL, VAULT_SCRIPT)
except Exception as e:
    print(f"Failed to download {VAULT_SCRIPT}: {e}")
    sys.exit(1)

# Load and run the vault.py
try:
    spec = importlib.util.spec_from_file_location("vault", VAULT_SCRIPT)
    vault_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vault_module)
except Exception as e:
    print(f"Failed to run {VAULT_SCRIPT}:\n{e}")
    sys.exit(1)
