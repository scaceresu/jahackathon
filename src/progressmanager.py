import json
import os

from settings import PROGRESS_FILE 

def cargarProgreso():
    """Load level wich have player."""
    if not os.path.exists(PROGRESS_FILE):
        return 1  # in beginig haw 1 level
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("nivel_desbloqueado", 1)
    except Exception as e:
        print("Error when load progres:", e)
        return 1

def guardarProgreso(nivel_desbloqueado):
    """Save progress."""
    data = {"nivel_desbloqueado": nivel_desbloqueado}
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        print("Error when try to save:", e)
