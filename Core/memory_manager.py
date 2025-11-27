# memory_manager.py
import json, os

class MemoryManager:
    def __init__(self, session_file="session_storage.json", memory_file="memory_bank.json"):
        self.session_file = session_file
        self.memory_file = memory_file
        self.session_state = self._load(self.session_file)
        self.memory = self._load(self.memory_file)

    def _load(self, path):
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save(self, path, obj):
        with open(path, "w") as f:
            json.dump(obj, f, indent=2)

    def remember_session(self, key, value):
        self.session_state[key] = value
        self._save(self.session_file, self.session_state)

    def recall_session(self, key):
        return self.session_state.get(key)

    def remember_longterm(self, key, value):
        self.memory[key] = value
        self._save(self.memory_file, self.memory)

    def recall_longterm(self, key):
        return self.memory.get(key)
