import requests
import streamlit as st
import os
import json
import time


OLLAMA_URL = "http://localhost:11434/api/chat"
AVAILABLE_MODELS = ["llama3", "llama2", "mistral", "phi"]
LOGS_DIR = "chat_logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Initialize session state variables before any UI
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "usage_stats" not in st.session_state:
    st.session_state.usage_stats = {"total_chats": 0, "total_messages": 0}
if "previous_chats" not in st.session_state:
    st.session_state.previous_chats = []
    for fname in sorted(os.listdir(LOGS_DIR), reverse=True):
        if fname.endswith(".json"):
            try:
                with open(os.path.join(LOGS_DIR, fname), "r", encoding="utf-8") as f:
                    st.session_state.previous_chats.append(json.load(f))
            except Exception:
                continue
if "current_chat_name" not in st.session_state:
    st.session_state.current_chat_name = "New Chat"

# Theme toggle
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



# Sidebar controls
with st.sidebar:
    st.header("Settings")
    model = st.selectbox("Model", AVAILABLE_MODELS, index=0)
    temperature = st.slider("Temperature (creativity)", 0.0, 1.5, 0.7, 0.05)
    system_prompt = st.text_area("System prompt (bot personality/instructions)", "You are a helpful AI assistant.")
    st.markdown("---")
    if st.button("Clear chat/history", type="primary"):
        if st.session_state.conversation:
            log_path = os.path.join(LOGS_DIR, f"chat_{int(time.time())}.json")
            chat_name = st.session_state.get("current_chat_name", f"Chat {time.strftime('%Y-%m-%d %H:%M:%S')}")
            log_data = {"name": chat_name, "messages": st.session_state.conversation}
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            st.session_state.usage_stats["total_chats"] += 1
            st.session_state.usage_stats["total_messages"] += len(st.session_state.conversation)
            st.session_state.previous_chats.insert(0, log_data)
        st.session_state.conversation = []
        st.session_state.current_chat_name = "New Chat"
    chat_text = "\n".join([
        f"You: {msg['content']}" if msg["role"] == "user" else f"Bot: {msg['content']}" for msg in st.session_state.get("conversation", [])
    ])
    if st.session_state.conversation:
        st.download_button("Download chat as .txt", chat_text, file_name="chat_history.txt")
    else:
        st.info("No chat history to download.")
    st.markdown(f"**Total chats:** {st.session_state.usage_stats['total_chats']}  ")
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
                    # Also update the file if it exists
                    for fname in os.listdir(LOGS_DIR):
                        if fname.endswith(".json"):
                            with open(os.path.join(LOGS_DIR, fname), "r", encoding="utf-8") as f:
                                try:
                                    file_data = json.load(f)
                                    if file_data.get("messages") == chat["messages"]:
                                        file_data["name"] = new_name
                                        with open(os.path.join(LOGS_DIR, fname), "w", encoding="utf-8") as fw:
                                            json.dump(file_data, fw, ensure_ascii=False, indent=2)
                                except Exception:
                                    continue
                if st.button(f"Load chat {idx+1}"):
                    st.session_state.conversation = chat["messages"].copy()
                    st.session_state.current_chat_name = chat["name"]
                    st.rerun()
                if st.button(f"Delete chat {idx+1}"):
                    # Remove from previous_chats and delete file
                    st.session_state.previous_chats.pop(idx)
                    for fname in os.listdir(LOGS_DIR):
                        if fname.endswith(".json"):
                            with open(os.path.join(LOGS_DIR, fname), "r", encoding="utf-8") as f:
                                try:
                                    file_data = json.load(f)
                                    if file_data.get("messages") == chat["messages"]:
                                        os.remove(os.path.join(LOGS_DIR, fname))
                                        break
                                except Exception:
                                    continue
                    st.rerun()

# Define get_bot_reply before any UI or chat logic

def get_bot_reply(conversation, model, temperature, system_prompt):
    # Insert system prompt as the first message if not already present
    messages = conversation.copy()
    if not messages or messages[0]["role"] != "system":
        messages = [{"role": "system", "content": system_prompt}] + messages
    payload = {
        "model": model,
        "messages": messages,
        "options": {"temperature": temperature}
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60, stream=True)
        response.raise_for_status()
        bot_reply = ""
        for line in response.iter_lines(decode_unicode=True):
            if not line.strip():
                continue
            data = None
            try:
                data = __import__('json').loads(line)
            except Exception:
                continue
            content = data.get("message", {}).get("content", "")
            if content:
                bot_reply += content
        return bot_reply.strip()
    except Exception as e:
        return f"[Error: {e}]"

st.set_page_config(page_title="Ollama Chatbot", page_icon="🤖", layout="wide")

st.title(f"🤖 AI Chatbot (Ollama) - {st.session_state.current_chat_name}")

# Display chat using Streamlit's built-in chat components
for msg in st.session_state.conversation:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

user_input = st.chat_input("Type your message...")
if user_input:
    st.session_state.conversation.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    # Typing indicator and smooth reveal
    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown("_Bot is typing..._", unsafe_allow_html=True)
        bot_reply = get_bot_reply(st.session_state.conversation, model, temperature, system_prompt)
        # Typing animation: reveal one character at a time
        displayed = ""
        for char in bot_reply:
            displayed += char
            typing_placeholder.markdown(displayed, unsafe_allow_html=True)
            time.sleep(0.005)  # Adjust speed as desired
    st.session_state.conversation.append({"role": "assistant", "content": bot_reply})
