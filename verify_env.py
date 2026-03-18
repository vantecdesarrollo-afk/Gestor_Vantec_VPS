import os
from dotenv import load_dotenv
import json

load_dotenv()

zones_str = os.getenv("WATCHER_ZONES")
print(f"WATCHER_ZONES Raw: {zones_str}")

try:
    zones = json.loads(zones_str)
    print(f"WATCHER_ZONES Loaded: {zones}")
except Exception as e:
    print(f"Error parsing JSON: {e}")
