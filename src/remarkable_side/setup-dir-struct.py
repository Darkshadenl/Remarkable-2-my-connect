#!/usr/bin/env python3


import os
from pathlib import Path
from pydantic_settings import BaseSettings

def setup_directory_structure():
    base_dir = "/home/root/remarkable_scripts"
    directories = [
        "webserver",
        "utils",
        "logs"
    ]
    
    # Maak hoofdmap
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Maak submappen
    for dir_name in directories:
        dir_path = os.path.join(base_dir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            # Maak __init__.py voor Python packages
            if dir_name in ['webserver', 'utils']:
                open(os.path.join(dir_path, '__init__.py'), 'a').close()

    # Maak requirements.txt
    requirements = [
        'fastapi',
        'uvicorn',
        'requests',
        'paramiko'
    ]
    
    with open(os.path.join(base_dir, 'requirements.txt'), 'w') as f:
        f.write('\n'.join(requirements))

if __name__ == "__main__":
    setup_directory_structure()
    print("Directory structuur succesvol opgezet!")
