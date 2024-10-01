import json
import os
from typing import Any


def load_json(file_path: str) -> Any:
    full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), file_path)
    # print("Loading...", full_path)
    with open(full_path, 'r') as f:
        return json.load(f)
