from pydantic_settings import BaseSettings
from pathlib import Path
import os


class RemarkableSettings(BaseSettings):
    remarkable_ip: str
    remarkable_wifi_ip: str
    remarkable_password: str
    remarkable_user: str
    local_script_dir: Path
    remote_base_dir: Path
    remarkable_script_config_json: str
    window_width: int = 800
    window_height: int = 800
    remarkable_backups: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> any:
            if field_name in ["local_script_dir", "remote_base_dir"]:
                return Path(os.path.expanduser(raw_val))
            if field_name in ["window_width", "window_height"]:
                return int(raw_val)
            return raw_val
