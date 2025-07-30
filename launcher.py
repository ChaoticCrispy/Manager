import importlib.util
import os
import sys

VAULT_SCRIPT = "vault.py"

if not os.path.exists(VAULT_SCRIPT):
    print(f"Error: {VAULT_SCRIPT} not found in the current directory.")
    sys.exit(1)

spec = importlib.util.spec_from_file_location("vault", VAULT_SCRIPT)
vault_module = importlib.util.module_from_spec(spec)

try:
    spec.loader.exec_module(vault_module)
except Exception as e:
    print(f"Failed to run {VAULT_SCRIPT}:\n{e}")
    sys.exit(1)
