
# Ollama Local AI Chatbot

A privacy-first, local AI chatbot app powered by [Ollama](https://ollama.com/) and Streamlit. No cloud, no data leaks—your conversations stay on your machine.

---

## Features
- **100% Local, Privacy-First**: All chat data and AI inference run on your computer.
- **Multi-Model Support**: Switch between Llama 3, Llama 2, Mistral, Phi, and more.
- **Persistent Chat History**: Save, load, rename, and delete previous chats.
- **Customizable**: System prompt, model, and creativity (temperature) controls.
- **Modern UI**: Responsive, themeable (light/dark/auto), markdown rendering, and smooth bot typing animation.
- **Download/Export**: Download chat history as .txt.
- **Ollama Status Check**: Warns if Ollama is not running.

---

## Quickstart

### 1. Prerequisites
- **Python 3.9+**
- **[Ollama](https://ollama.com/download)** (install and run locally)
- (Optional) [Streamlit Desktop](https://github.com/streamlit/streamlit-desktop) or PyInstaller for desktop packaging

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Start Ollama
```powershell
ollama serve
```

### 4. Run the App
```powershell
streamlit run main.py
```

The app will open in your browser at http://localhost:8501

---

## Usage
- **Chat**: Type messages, get instant AI responses.
- **Sidebar**: Change model, temperature, system prompt, theme, and manage chat history.
- **Save/Load**: Save chats for later, load or delete previous conversations.
- **Download**: Export chat as .txt.

---

## Packaging as Desktop App

### Option 1: Streamlit Desktop (Recommended)
- Use [Streamlit Desktop](https://github.com/streamlit/streamlit-desktop) for a native app feel. Follow their instructions to wrap this app.

### Option 2: PyInstaller (Windows, Mac, Linux)

#### Windows (PowerShell)
1. Run:
   ```powershell
   ./package_app.ps1
   ```
2. Find your `.exe` in the `dist` folder and double-click to launch.

#### Mac/Linux (Bash)
1. Make the script executable:
   ```bash
   chmod +x package_app.sh
   ./package_app.sh
   ```
2. Find your executable in the `dist` folder and run it:
   ```bash
   ./dist/desktop_launcher
   ```

**Note:**
- The app uses `desktop_launcher.py` as the entry point for packaging.
- For best results on Mac/Linux, run from a terminal. Use Streamlit Desktop for a more native feel if desired.

---

## Troubleshooting
- **Ollama not running?** Start it with `ollama serve`.
- **Model not found?** Pull a model with `ollama pull llama3` (or your preferred model).
- **Port in use?** Change the Streamlit port with `streamlit run main.py --server.port 8502`.

---

## Unique Selling Points (USPs)
- 100% local, privacy-first AI chat
- Multi-model, multi-persona
- Persistent, manageable chat history
- Modern, themeable UI
- No cloud, no subscriptions, no tracking

---

## License
MIT License

---

## Credits
- [Ollama](https://ollama.com/)
- [Streamlit](https://streamlit.io/)
