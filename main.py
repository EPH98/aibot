

import streamlit as st
import time
import json
import requests
from utils.chat_helpers import (
    log_error,
    find_log_file_by_messages,
    save_chat_to_log,
    load_previous_chats
)
from utils.ollama_helpers import get_bot_reply, check_ollama_status
from utils.constants import OLLAMA_URL, AVAILABLE_MODELS, USER, BOT, SYSTEM, __version__

def get_bot_reply(conversation, model, temperature, system_prompt):
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
        return f"[Error: {e}]"

# === App State ===
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "usage_stats" not in st.session_state:
    st.session_state.usage_stats = {"total_chats": 0, "total_messages": 0}
if "previous_chats" not in st.session_state:
    st.session_state.previous_chats = load_previous_chats()
if "current_chat_name" not in st.session_state:
    st.session_state.current_chat_name = "New Chat"
if "ollama_status" not in st.session_state:
    st.session_state.ollama_status = None


ollama_ok = check_ollama_status()
st.session_state.ollama_status = ollama_ok

# === UI Setup ===
st.title(f"🤖 AI Chatbot (Ollama) - {st.session_state.current_chat_name}")
st.set_page_config(page_title="Ollama Chatbot", page_icon="🤖", layout="wide")
st.markdown(f"<small>Version: {__version__}</small>", unsafe_allow_html=True)

if not ollama_ok:
    st.error("⚠️ Ollama server is not running! Please start Ollama (run `ollama serve`) and ensure your models are available.")

# === Theme ===
theme = st.sidebar.radio("Theme", ["Light", "Dark", "Auto"], index=2)
if theme == "Dark":
    st.markdown("""
        <style>
        body, .stApp { background: #18191a !important; color: #f5f6fa !important; }
        .stTextInput>div>div>input, .stButton>button { background: #242526 !important; color: #f5f6fa !important; }
        </style>
    """, unsafe_allow_html=True)
elif theme == "Light":
    st.markdown("""
        <style>
        body, .stApp { background: #fff !important; color: #222 !important; }
        </style>
    """, unsafe_allow_html=True)

# === Sidebar ===
with st.sidebar:
    st.header("Settings")
    model = st.selectbox("Model", AVAILABLE_MODELS, index=0)
    temperature = st.slider("Temperature (creativity)", 0.0, 1.5, 0.7, 0.05)
    system_prompt = st.text_area("System prompt (bot personality/instructions)", "You are a helpful AI assistant.")
    st.markdown("---")


    # --- Save chat button ---
    if st.button("Save chat", type="secondary"):
        if st.session_state.conversation:
            log_data = save_chat_to_log(
                st.session_state.get("current_chat_name"),
                st.session_state.conversation
            )
            st.session_state.usage_stats["total_chats"] += 1
            st.session_state.usage_stats["total_messages"] += len(st.session_state.conversation)
            st.session_state.previous_chats.insert(0, log_data)
            st.success("Chat saved!")
        else:
            st.info("No conversation to save.")

    if st.button("Clear chat/history", type="primary"):
        if st.session_state.conversation:
            log_data = save_chat_to_log(
                st.session_state.get("current_chat_name"),
                st.session_state.conversation
            )
            st.session_state.usage_stats["total_chats"] += 1
            st.session_state.usage_stats["total_messages"] += len(st.session_state.conversation)
            st.session_state.previous_chats.insert(0, log_data)
        st.session_state.conversation = []
        st.session_state.current_chat_name = "New Chat"

    chat_text = "\n".join([
        f"You: {msg['content']}" if msg["role"] == USER else f"Bot: {msg['content']}"
        for msg in st.session_state.conversation
    ])
    if st.session_state.conversation:
        st.download_button("Download chat as .txt", chat_text, file_name="chat_history.txt")
    else:
        st.info("No chat history to download.")

    st.subheader("Stats")
    st.markdown(f"**Total chats:** {st.session_state.usage_stats['total_chats']}")
    st.markdown(f"**Total messages:** {st.session_state.usage_stats['total_messages']}")

    if st.session_state.previous_chats:
        st.markdown("---")
        st.subheader("Previous Chats")
        for idx, chat in enumerate(st.session_state.previous_chats[:5]):
            chat_name = chat.get("name", f"Chat #{idx+1}")
            with st.expander(f"{chat_name} ({len(chat['messages'])} messages)"):
                new_name = st.text_input(f"Rename chat {idx+1}", value=chat_name, key=f"rename_{idx}")
                if new_name != chat_name:
                    chat["name"] = new_name
                    path = find_log_file_by_messages(chat["messages"])
                    if path:
                        with path.open("r", encoding="utf-8") as f:
                            file_data = json.load(f)
                        file_data["name"] = new_name
                        with path.open("w", encoding="utf-8") as fw:
                            json.dump(file_data, fw, ensure_ascii=False, indent=2)
                if st.button(f"Load chat {idx+1}", key=f"load_{idx}"):
                    st.session_state.conversation = chat["messages"].copy()
                    st.session_state.current_chat_name = chat["name"]
                    st.rerun()
                if st.button(f"Delete chat {idx+1}", key=f"delete_{idx}"):
                    st.session_state.previous_chats.pop(idx)
                    path = find_log_file_by_messages(chat["messages"])
                    if path:
                        path.unlink()
                    st.rerun()

# === Main Chat Window ===
for msg in st.session_state.conversation:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your message...")
if user_input:
    st.session_state.conversation.append({"role": USER, "content": user_input})
    with st.chat_message(USER):
        st.markdown(user_input)

    with st.chat_message(BOT):
        placeholder = st.empty()
        placeholder.markdown("_Bot is typing..._")
        bot_reply = get_bot_reply(st.session_state.conversation, model, temperature, system_prompt)
        if bot_reply.startswith("[Error:"):
            placeholder.error(bot_reply)
        else:
            displayed = ""
            for char in bot_reply:
                displayed += char
                placeholder.markdown(displayed)
                time.sleep(0.005)
        st.session_state.conversation.append({"role": BOT, "content": bot_reply})
