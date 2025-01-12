import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv
import paramiko
import os
import json
from pydantic_settings import BaseSettings
from pathlib import Path

load_dotenv()


class RemarkableSettings(BaseSettings):
    remarkable_ip: str
    remarkable_wifi_ip: str
    remarkable_password: str
    remarkable_user: str
    local_script_dir: Path
    remote_base_dir: Path

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> any:
            if field_name in ["local_script_dir", "remote_base_dir"]:
                return Path(os.path.expanduser(raw_val))
            return raw_val


class RemarkableInstaller:
    def __init__(self):
        # Load settings
        self.settings = RemarkableSettings()

        # Local paths
        self.config_file = os.path.join(
            self.settings.local_script_dir, "remarkable_scripts_config.json"
        )

        # Laad de script configuratie
        self.load_config()

        self.setup_gui()

    def load_config(self):
        """Laad de script configuratie uit het JSON bestand."""
        try:
            expanded_config_file = os.path.expanduser(self.config_file)
            with open(expanded_config_file, "r") as f:
                self.scripts_config = json.load(f)
        except FileNotFoundError:
            messagebox.showerror(
                "Configuratie Fout",
                f"Configuratie bestand niet gevonden: {expanded_config_file}",
            )
            self.scripts_config = {}
        except json.JSONDecodeError as e:
            messagebox.showerror(
                "Configuratie Fout", f"Fout in JSON configuratie: {str(e)}"
            )
            self.scripts_config = {}

    def save_config(self):
        """Sla de huidige configuratie op in het JSON bestand."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.scripts_config, f, indent=4)
        except Exception as e:
            messagebox.showerror(
                "Opslaan Fout", f"Kon configuratie niet opslaan: {str(e)}"
            )

    def connect_to_remarkable(self):
        """Maak SSH verbinding met de reMarkable."""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Probeer eerst USB verbinding
            try:
                ssh.connect(
                    self.settings.remarkable_wifi_ip,
                    username=self.settings.remarkable_user,
                    password=self.settings.remarkable_password,
                )
            except Exception:
                # Als USB niet werkt, probeer WiFi
                ssh.connect(
                    self.settings.remarkable_ip,
                    username=self.settings.remarkable_user,
                    password=self.settings.remarkable_password,
                )

            return ssh
        except Exception as e:
            messagebox.showerror(
                "Verbinding Fout", f"Kon geen verbinding maken met reMarkable: {str(e)}"
            )
            return None

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("reMarkable Script Installer")
        self.root.geometry("500x600")

        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Status label
        self.status_var = tk.StringVar(value="Gereed voor installatie")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, columnspan=2, pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=300, mode="determinate")
        self.progress.grid(row=1, column=0, columnspan=2, pady=5)

        # Install button
        install_btn = ttk.Button(
            main_frame, text="Installeer Scripts", command=self.start_installation
        )
        install_btn.grid(row=2, column=0, pady=5)

        # Reload config button
        reload_btn = ttk.Button(
            main_frame, text="Herlaad Configuratie", command=self.reload_config
        )
        reload_btn.grid(row=2, column=1, pady=5)

        # Script list
        self.create_script_list(main_frame)

    def reload_config(self):
        """Herlaad de configuratie en update de GUI."""
        self.load_config()
        self.update_script_list()
        self.update_status("Configuratie herladen")

    def create_script_list(self, parent):
        # Create a frame for the script list
        self.list_frame = ttk.LabelFrame(
            parent, text="Te installeren scripts", padding="5"
        )
        self.list_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        self.update_script_list()

    def update_script_list(self):
        # Clear existing items
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        # Add headers
        ttk.Label(self.list_frame, text="Volgorde", width=8).grid(row=0, column=0)
        ttk.Label(self.list_frame, text="Script", width=20).grid(row=0, column=1)
        ttk.Label(self.list_frame, text="Beschrijving", width=40).grid(row=0, column=2)

        # Add scripts
        for i, (script_name, config) in enumerate(
            sorted(self.scripts_config.items(), key=lambda x: x[1]["order"])
        ):
            ttk.Label(self.list_frame, text=str(config["order"])).grid(
                row=i + 1, column=0
            )
            ttk.Label(self.list_frame, text=script_name).grid(row=i + 1, column=1)
            ttk.Label(self.list_frame, text=config.get("description", "")).grid(
                row=i + 1, column=2
            )

    def update_status(self, message: str):
        self.status_var.set(message)
        self.root.update()

    def connect_ssh(self) -> paramiko.SSHClient:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.remarkable_ip,
                username=self.remarkable_user,
                password=self.remarkable_password,
            )
            return ssh
        except Exception as e:
            messagebox.showerror(
                "Verbindingsfout", f"Kan niet verbinden met reMarkable: {str(e)}"
            )
            raise

    def transfer_file(self, sftp, local_path: str, remote_path: str):
        try:
            self.update_status(f"Bestand overzetten: {os.path.basename(local_path)}")
            sftp.put(os.path.join(self.local_script_dir, local_path), remote_path)
        except Exception as e:
            messagebox.showerror(
                "Overzetfout", f"Fout bij overzetten {local_path}: {str(e)}"
            )
            raise

    def execute_remote_script(self, ssh: paramiko.SSHClient, remote_path: str):
        try:
            self.update_status(f"Script uitvoeren: {os.path.basename(remote_path)}")
            stdin, stdout, stderr = ssh.exec_command(f"python3 {remote_path}")
            exit_status = stdout.channel.recv_exit_status()

            if exit_status != 0:
                error_message = stderr.read().decode()
                raise Exception(
                    f"Script fout (exit code {exit_status}): {error_message}"
                )

        except Exception as e:
            messagebox.showerror(
                "Uitvoeringsfout", f"Fout bij uitvoeren {remote_path}: {str(e)}"
            )
            raise

    def start_installation(self):
        try:
            self.progress["value"] = 0
            step = 100.0 / (len(self.scripts_config) * 2)  # Transfer + Execute

            ssh = self.connect_ssh()
            sftp = ssh.open_sftp()

            # Ensure base directory exists
            ssh.exec_command(f"mkdir -p {self.remote_base_dir}")

            # Transfer and execute scripts in order
            for script_name, config in sorted(
                self.scripts_config.items(), key=lambda x: x[1]["order"]
            ):
                # Transfer
                self.transfer_file(sftp, config["local_path"], config["remote_path"])
                self.progress["value"] += step

                # Execute if needed
                if config["execute"]:
                    self.execute_remote_script(ssh, config["remote_path"])
                self.progress["value"] += step

            sftp.close()
            ssh.close()

            self.update_status("Installatie succesvol afgerond!")
            self.progress["value"] = 100
            messagebox.showinfo("Succes", "Alle scripts zijn geïnstalleerd!")

        except Exception as e:
            self.update_status("Installatie mislukt!")
            messagebox.showerror("Fout", f"Installatie mislukt: {str(e)}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    installer = RemarkableInstaller()
    installer.run()
