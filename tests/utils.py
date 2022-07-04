import json
import os

BASE_DIR = os.path.dirname(__file__)


def open_file(file_path: str):
    path = os.path.join(BASE_DIR, file_path)
    with open(path) as f:
        return json.load(f)
