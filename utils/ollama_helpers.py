import requests
from utils.chat_helpers import log_error
from utils.constants import OLLAMA_URL, SYSTEM
import json

def check_ollama_status() -> bool:
    """Check if the Ollama server is running locally."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False

def get_bot_reply(conversation: list, model: str, temperature: float, system_prompt: str) -> str:
    """Send conversation to Ollama and return the bot's reply."""
    messages = conversation.copy()
    if not messages or messages[0]["role"] != SYSTEM:
        messages = [{"role": SYSTEM, "content": system_prompt}] + messages
    payload = {
        "model": model,
        "messages": messages,
        "options": {"temperature": temperature},
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60, stream=True)
        response.raise_for_status()
        bot_reply = ""
        for line in response.iter_lines(decode_unicode=True):
            if line.strip():
                try:
                    data = json.loads(line)
                    content = data.get("message", {}).get("content", "")
                    bot_reply += content
                except Exception as e:
                    log_error(str(e))
        return bot_reply.strip()
    except Exception as e:
        log_error(str(e))
        return "[Error: Could not get a response from the AI. Please check Ollama and try again.]"
