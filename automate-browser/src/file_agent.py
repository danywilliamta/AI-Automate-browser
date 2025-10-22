import os
import json

class FileAgent:
    def __init__(self, filename ="test_report.json"):
        self.filename = filename
        self.filepath = os.path.join(os.getcwd(), self.filename)


    def save_content(self, content: json):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=4)
            print(f"Content saved to {self.filepath}")
        except Exception as e:
            print(f"Error saving content to {self.filepath}: {e}")
