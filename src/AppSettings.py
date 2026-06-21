import json
import os

from src.ReadFile import resource_path

SETTINGS_FILE = resource_path("settings.settings")

def load():
    try:
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)

def get(key, default = None):
    return load().get(key, default)

def set(key, value):
    data = load()
    data[key]  = value
    save(data)