import json
import os
from collections import defaultdict

FEEDBACK_FILE = "backend/feedback.json"

class FeedbackManager:
    def __init__(self):
        # Fix path to be relative to the script if needed, or assume backend is CWD
        # Using absolute path resolution for safety
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(base_dir, "feedback.json")
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_data(self):
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving feedback: {e}")

    def add_report(self, url: str):
        # In a real system, track User IDs to prevent spamming
        current = self.data.get(url, {"safe_votes": 0})
        current["safe_votes"] += 1
        self.data[url] = current
        self._save_data()
        return current["safe_votes"]

    def get_votes(self, url: str):
        return self.data.get(url, {}).get("safe_votes", 0)
