import json
from pathlib import Path

MEMORY_FILE = Path("user_memory.json")

def load_memory():
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())
    return {}

def save_memory(memory):
    MEMORY_FILE.write_text(json.dumps(memory, indent=2))

def get_user_context(user_id):
    memory = load_memory()
    entries = memory.get(user_id, [])
    return "\n".join(entries[-5:])

def set_user_profile(user_id, profile):
    memory = load_memory()
    memory[user_id] = profile
    save_memory(memory)

def get_user_profile(user_id):
    memory = load_memory()
    return memory.get(user_id, {})