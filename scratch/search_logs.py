import json
import sys

# Reconfigure stdout to use UTF-8
sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\eniai\.gemini\antigravity-cli\brain\34cb03a2-2194-4c54-8dca-2c07a78f70e0\.system_generated\logs\transcript.jsonl"

with open(log_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "diner_south_112" in line:
            obj = json.loads(line)
            if obj.get("type") == "SYSTEM_MESSAGE":
                print(f"=====================================")
                print(f"Step {i}: SYSTEM_MESSAGE content")
                print(f"=====================================")
                print(obj.get("content"))
                print("\n" + "="*50 + "\n")
