import json
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

CONFIG = load_config()
