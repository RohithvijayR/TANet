import csv
import os
import datetime

class TrafficLogger:
    def __init__(self, filename="captured_data.csv"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filepath = os.path.join(base_dir, filename)
        self._ensure_header()

    def _ensure_header(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Schema: Timestamp, URL, PredictionScore, IsPhishing, Features...
                writer.writerow(["timestamp", "url", "score", "is_phishing", "features"])

    def log(self, url, score, is_phishing, features):
        try:
            with open(self.filepath, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Flatten features dict to string for simple storage, or expand if retraining script expects it.
                # For simplicity in this prototype, storing features as a string representation.
                writer.writerow([
                    datetime.datetime.now().isoformat(),
                    url,
                    f"{score:.4f}",
                    "1" if is_phishing else "0",
                    str(features)
                ])
        except Exception as e:
            print(f"Logging failed: {e}")

    def log_user_report(self, url, label, features):
        """
        Log user feedback (Active Learning).
        label: 0 for Safe, 1 for Phishing
        """
        filepath = self.filepath.replace("captured_data.csv", "user_reports.csv")
        
        # Ensure header
        if not os.path.exists(filepath):
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["timestamp", "url", "user_label", "features"])
        
        try:
            with open(filepath, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([
                    datetime.datetime.now().isoformat(),
                    url,
                    label,
                    str(features)
                ])
        except Exception as e:
            print(f"User Report logging failed: {e}")
