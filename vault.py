import customtkinter as ctk
from tkinter import messagebox
import os, json, base64, webbrowser
from datetime import datetime
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
import urllib.request
import os, sys

VAULT_FILE = "vault.crispy"
HEADER = b"CRISPY1"


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def ensure_theme():
    local_theme_path = resource_path("customtkinter/assets/themes/blue.json")
    os.makedirs(os.path.dirname(local_theme_path), exist_ok=True)
    if not os.path.exists(local_theme_path):
        try:
            print("Downloading missing theme...")
            urllib.request.urlretrieve(
                "https://raw.githubusercontent.com/ChaoticCrispy/Manager/main/themes/blue.json",
                local_theme_path
            )
        except Exception as e:
            print("Failed to download theme:", e)
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

ensure_theme()
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme(resource_path("customtkinter/assets/themes/blue.json"))

def load_vault(password: str):
    if not os.path.exists(VAULT_FILE):
        return [], os.urandom(16)

    with open(VAULT_FILE, "rb") as f:
        if f.read(7) != HEADER:
            raise ValueError("Invalid vault format.")
        salt = f.read(16)
        data = f.read()

    key = derive_key(password, salt)
    fernet = Fernet(key)
    try:
        decrypted = fernet.decrypt(data)
        return json.loads(decrypted.decode()), salt
    except:
        raise ValueError("Wrong password or corrupt vault.")

def save_vault(data: list, password: str, salt: bytes):
    key = derive_key(password, salt)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(json.dumps(data).encode())

    with open(VAULT_FILE, "wb") as f:
        f.write(HEADER)
        f.write(salt)
        f.write(encrypted)

class VaultLoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_unlock):
        super().__init__(master)
        self.on_unlock = on_unlock

        ctk.CTkLabel(self, text="Enter your encryption key", font=ctk.CTkFont(size=18)).pack(pady=(60, 10))
        self.entry = ctk.CTkEntry(self, show="*", width=280, placeholder_text="Master Key")
        self.entry.pack(pady=10)
        self.entry.focus()

        ctk.CTkButton(self, text="Unlock Vault", command=self.submit).pack(pady=20)
        self.entry.bind("<Return>", lambda e: self.submit())

    def submit(self):
        password = self.entry.get().strip()
        if not password:
            messagebox.showerror("Error", "Encryption key is required.")
            return
        try:
            vault, salt = load_vault(password)
            self.on_unlock(password, vault, salt)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Vault Error", str(e))

class PasswordManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Crispy Vault")
        self.geometry("420x500")
        self.login_screen = VaultLoginScreen(self, self.unlock)
        self.login_screen.pack(fill="both", expand=True)

    def unlock(self, password, vault, salt):
        self.password = password
        self.vault = vault
        self.salt = salt
        self.init_ui()

    def init_ui(self):
        self.inputs_frame = ctk.CTkFrame(self)
        self.inputs_frame.pack(pady=20, padx=20, fill="x")

        self.user_entry = ctk.CTkEntry(self.inputs_frame, placeholder_text="Username")
        self.pass_entry = ctk.CTkEntry(self.inputs_frame, placeholder_text="Password")
        self.note_entry = ctk.CTkEntry(self.inputs_frame, placeholder_text="Note (optional)")

        self.user_entry.pack(pady=5, fill="x")
        self.pass_entry.pack(pady=5, fill="x")
        self.note_entry.pack(pady=5, fill="x")

        ctk.CTkButton(self, text="Add Entry", command=self.add_entry).pack(pady=8)
        ctk.CTkButton(self, text="View Vault", command=self.view_vault).pack(pady=4)
        ctk.CTkButton(self, text="Export Backup", command=self.export_backup).pack(pady=8)

        self.output = ctk.CTkTextbox(self, height=200)
        self.output.pack(padx=10, pady=10, fill="both", expand=True)

    def add_entry(self):
        user = self.user_entry.get().strip()
        pwd = self.pass_entry.get().strip()
        note = self.note_entry.get().strip()

        if not user or not pwd:
            messagebox.showerror("Error", "Username and password are required.")
            return

        self.vault.append({
            "username": user,
            "password": pwd,
            "note": note
        })

        save_vault(self.vault, self.password, self.salt)
        messagebox.showinfo("Saved", "Entry added.")
        self.user_entry.delete(0, "end")
        self.pass_entry.delete(0, "end")
        self.note_entry.delete(0, "end")

    def view_vault(self):
        self.output.delete("0.0", "end")
        for i, entry in enumerate(self.vault, start=1):
            self.output.insert("end", f"[{i}]\n")
            self.output.insert("end", f"  Username: {entry['username']}\n")
            self.output.insert("end", f"  Password: {entry['password']}\n")
            if entry.get("note"):
                self.output.insert("end", f"  Note: {entry['note']}\n")
            self.output.insert("end", "-"*40 + "\n")

    def export_backup(self):
        if not hasattr(self, "vault") or not self.password or not self.salt:
            messagebox.showerror("Error", "Vault not loaded.")
            return

        # Save latest vault first
        save_vault(self.vault, self.password, self.salt)

        os.makedirs("backup", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        backup_path = f"backup/backup_{timestamp}.crispy"

        try:
            with open(VAULT_FILE, "rb") as f:
                data = f.read()
            with open(backup_path, "wb") as out:
                out.write(data)
            webbrowser.open("https://www.dropbox.com/home")
            messagebox.showinfo("Backup Exported", f"Saved to:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export backup:\n{e}")
import os, sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)





    app = PasswordManager()
    app.mainloop()
