import time
import json
from pathlib import Path

LOGS_DIR = Path("chat_logs")
LOGS_DIR.mkdir(exist_ok=True)

# Error logging
def log_error(err_msg):
    with open("error.log", "a", encoding="utf-8") as f:
        f.write(f"{time.ctime()}: {err_msg}\n")

# Find log file by messages
def find_log_file_by_messages(messages):
    for path in LOGS_DIR.glob("*.json"):
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("messages") == messages:
                    return path
        except Exception as e:
            log_error(str(e))
    return None

# Save chat to log
def save_chat_to_log(chat_name, messages):
    log_path = LOGS_DIR / f"chat_{int(time.time())}.json"
    log_data = {"name": chat_name, "messages": messages}
    try:
        with log_path.open("w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_error(str(e))
    return log_data

# Load previous chats
def load_previous_chats():
    chats = []
    for path in sorted(LOGS_DIR.glob("*.json"), reverse=True):
        try:
            with path.open("r", encoding="utf-8") as f:
                chats.append(json.load(f))
        except Exception as e:
            log_error(str(e))
    return chats
