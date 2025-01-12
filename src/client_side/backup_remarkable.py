#!/usr/bin/env python3
import paramiko
import os
from datetime import datetime
from pathlib import Path
import sys
from settings import RemarkableSettings

# Add parent directory to Python path so we can import settings
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(PARENT_DIR)


def create_backup():
    # Load settings
    settings = RemarkableSettings(_env_file=os.path.join(PARENT_DIR, ".env"))
    # Backup settings
    REMARKABLE_DOCUMENTS_PATH = "/home/root/.local/share/remarkable/xochitl/"
    backup_dir = os.path.expanduser(settings.remarkable_backups)
    current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"remarkable_backup_{current_date}")

    # Ensure backup directory exists
    os.makedirs(backup_path, exist_ok=True)

    # Connect to reMarkable
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Try WiFi connection first
        try:
            print("Attempting WiFi connection...")
            ssh.connect(
                settings.remarkable_wifi_ip,
                username=settings.remarkable_user,
                password=settings.remarkable_password,
                timeout=5,
            )
        except Exception as e:
            print("WiFi connection failed, trying USB connection...")
            ssh.connect(
                settings.remarkable_ip,
                username=settings.remarkable_user,
                password=settings.remarkable_password,
            )

        print("Connected to reMarkable")
        sftp = ssh.open_sftp()

        # Get list of files and directories to backup
        stdin, stdout, stderr = ssh.exec_command(
            f"find {REMARKABLE_DOCUMENTS_PATH} -type f"
        )
        files = stdout.read().decode().splitlines()

        total_files = len(files)
        print(f"Found {total_files} files to backup")

        # Create backup
        for i, file in enumerate(files, 1):
            try:
                # Create local directory structure
                local_path = os.path.join(
                    backup_path, os.path.relpath(file, REMARKABLE_DOCUMENTS_PATH)
                )
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                # Copy file
                print(f"Copying file {i}/{total_files}: {os.path.basename(file)}")
                sftp.get(file, local_path)

            except Exception as e:
                print(f"Error copying {file}: {str(e)}")

        print(f"\nBackup completed successfully!")
        print(f"Backup location: {backup_path}")

    except Exception as e:
        print(f"Error during backup: {str(e)}")

    finally:
        ssh.close()


if __name__ == "__main__":
    create_backup()
