# ====== Nova AI Chat (Enhanced) ======
# Features:
# - Persistent per-user chat history (history_<username>.json)
# - Voice input (audio upload -> Whisper STT)
# - Voice output (OpenAI TTS -> MP3; gTTS fallback)
# - Memory mode (memory_<username>.json, included in system prompt)
# - Personality switch (Professional/Casual/Fun)
# - Rich formatting (renders fenced code blocks)
# - Secure password storage with bcrypt (but supports old plaintext users)

import streamlit as st
import os
import json
import time
from datetime import datetime
import base64
from io import BytesIO

# OpenAI (v1+ client)
try:
    from openai import OpenAI
    _HAS_OPENAI_V1 = True
except Exception:
    _HAS_OPENAI_V1 = False

# Fallback old SDK
import openai as openai_legacy

# Audio TTS fallback
from gtts import gTTS

# Password hashing
import bcrypt

# ====== API KEY ======
if "OPENAI_API_KEY" in st.secrets:   # Streamlit Cloud
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
else:                                # Local environment
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("❌ No API key found. Set OPENAI_API_KEY in Streamlit secrets or environment.")
    st.stop()

# Initialize OpenAI client if available
client = None
if _HAS_OPENAI_V1:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_legacy.api_key = OPENAI_API_KEY

# ====== Files ======
USER_FILE = "users.json"
MEMORY_FILE_TPL = "memory_{username}.json"
HISTORY_FILE_TPL = "history_{username}.json"

# ====== Helpers: Users (with backward compatibility) ======
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
    except json.JSONDecodeError:
        return {}

def save_users(users: dict):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def _hash_password(plain: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")

def _check_password(stored: str, provided: str) -> bool:
    """
    Supports both hashed (bcrypt) and legacy plaintext.
    - If 'stored' looks like a bcrypt hash, verify with bcrypt.
    - Else compare plaintext for backward compatibility.
    """
    try:
        # bcrypt hashes usually start with $2b$, $2a$, or $2y$
        if stored.startswith("$2"):
            return bcrypt.checkpw(provided.encode("utf-8"), stored.encode("utf-8"))
        else:
            # Legacy plaintext match
            return stored == provided
    except Exception:
        return False

def signup(username, password):
    users = load_users()
    if not username.strip() or not password:
        return False, "Username and password required."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if username in users:
        return False, "Username already exists."
    users[username] = _hash_password(password)
    save_users(users)
    return True, "Signup successful!"

def login(username, password):
    users = load_users()
    if username in users and _check_password(users[username], password):
        return True, "Login successful!"
    return False, "Invalid username or password."

# ====== Helpers: Memory ======
def memory_path(username: str) -> str:
    return MEMORY_FILE_TPL.format(username=username)

def load_memory(username: str):
    path = memory_path(username)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_memory(username: str, memory_list):
    with open(memory_path(username), "w", encoding="utf-8") as f:
        json.dump(memory_list, f, indent=2, ensure_ascii=False)

# ====== Helpers: Chat History ======
def history_path(username: str) -> str:
    return HISTORY_FILE_TPL.format(username=username)

def load_chat(username: str):
    file = history_path(username)
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_chat(username: str, chat_history):
    with open(history_path(username), "w", encoding="utf-8") as f:
        json.dump(chat_history, f, indent=2, ensure_ascii=False)

# ====== UI Theme ======
st.markdown("""
<style>
/* Main app background */
.stApp {
    background: linear-gradient(135deg, #1a1a1a, #2d2d2d, #1a1a2e) !important;
    background-size: 400% 400% !important;
    animation: gradientMove 15s ease infinite !important;
    min-height: 100vh !important;
}
/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #2d2d2d, #1a1a2e, #333333) !important;
    background-size: 400% 400% !important;
    animation: gradientMove 15s ease infinite !important;
}
@keyframes gradientMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
/* Force ALL text to be visible */
.stApp, .stApp *, .stMarkdown, .stMarkdown *, 
.stText, .stText *, p, span, div, label { color: #ffffff !important; }
/* Streamlit specific elements */
.stMarkdown p, .stMarkdown div, .stMarkdown span { color: #ffffff !important; }
/* Tab content */
.stTabs [data-baseweb="tab-panel"] {
    background-color: rgba(45,45,45,0.3) !important;
    padding: 20px !important;
    border-radius: 10px !important;
    border: 1px solid rgba(0,255,204,0.2) !important;
}
/* Headers */
h1, h2, h3, h4, h5, h6 {
    color: #00ffcc !important;
    text-shadow: 0 0 10px rgba(0,255,204,0.5);
}
/* Input fields */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #3d3d3d !important;
    color: #ffffff !important;
    border: 2px solid #00ffcc !important;
    border-radius: 10px !important;
    padding: 15px !important;
    font-size: 16px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #0077ff !important;
    box-shadow: 0 0 20px rgba(0,255,204,0.8) !important;
    outline: none !important;
}
.stTextInput > label, .stTextArea > label {
    color: #00ffcc !important; font-weight: bold !important; font-size: 18px !important;
}
/* Buttons */
.stButton > button {
    background: linear-gradient(45deg, #00ffcc, #0077ff) !important;
    color: #000 !important; font-size: 16px !important; font-weight: bold !important;
    border: none !important; border-radius: 12px !important; padding: 12px 24px !important;
    cursor: pointer !important; box-shadow: 0 4px 15px rgba(0,255,204,0.4) !important;
    transition: all 0.3s ease !important; width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(45deg, #0077ff, #00ffcc) !important;
    color: #fff !important; box-shadow: 0 6px 20px rgba(0,255,204,0.8) !important;
    transform: translateY(-2px) scale(1.02) !important;
}
/* Loading animation */
@keyframes pulse { 0% { transform: scale(1); opacity: 0.6; } 50% { transform: scale(1.5); opacity: 1; } 100% { transform: scale(1); opacity: 0.6; } }
.loading-circle { width: 30px; height: 30px; margin: 20px auto; border-radius: 50%; background: linear-gradient(45deg, #00ffcc, #0077ff); animation: pulse 1.5s infinite; box-shadow: 0 0 20px rgba(0,255,204,0.8); }
/* Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #2d2d2d; border-radius: 10px; }
::-webkit-scrollbar-thumb { background: #00ffcc; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #0077ff; }
/* Code blocks */
code { background-color: #2d2d2d; padding: 2px 6px; border-radius: 4px; font-family: 'Courier New', monospace; }
pre { background-color: #2d2d2d; padding: 12px; border-radius: 8px; overflow-x: auto; border-left: 4px solid #00ffcc; }
.chat-message { padding: 15px; margin: 10px 0; border-radius: 12px; background-color: rgba(45,45,45,0.7); backdrop-filter: blur(5px); animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px);} to { opacity: 1; transform: translateY(0);} }
</style>
""", unsafe_allow_html=True)

# ====== Session state ======
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("username", "")
st.session_state.setdefault("chat_history", [])
st.session_state.setdefault("current_model", "gpt-4o-mini")  # sensible default
st.session_state.setdefault("temperature", 0.7)
st.session_state.setdefault("max_tokens", 600)
st.session_state.setdefault("conversation_started", False)
st.session_state.setdefault("speak_replies", False)
st.session_state.setdefault("memory_enabled", True)
st.session_state.setdefault("personality", "Casual 😎")
st.session_state.setdefault("last_tts_audio", None)

# ====== Models ======
MODELS = {
    "GPT-4o mini (fast, cheap)": "gpt-4o-mini",
    "GPT-4o (quality)": "gpt-4o",
    "GPT-4 Turbo (compat)": "gpt-4-turbo-preview",
    "GPT-3.5 Turbo (legacy)": "gpt-3.5-turbo",
}

# ====== Header ======
st.markdown("""
<div style='text-align: center; margin-bottom: 30px;'>
    <h1 style='font-size: 3em; background: linear-gradient(45deg, #00ffcc, #0077ff); 
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;
               text-shadow: 0 0 30px rgba(0,255,204,0.8);'>
        🤖 Nova AI Chat
    </h1>
    <p style='font-size: 1.2em; color: #cccccc; margin-top: 10px;'>
        Your intelligent AI assistant
    </p>
</div>
""", unsafe_allow_html=True)

# ====== Sidebar ======
st.sidebar.title("📂 Menu")

if st.session_state["logged_in"]:
    st.sidebar.markdown(f"**🟢 Logged in as:** `{st.session_state['username']}`")

    # Model selection
    st.sidebar.subheader("🤖 AI Model")
    current_model_key = next((k for k, v in MODELS.items() if v == st.session_state["current_model"]), list(MODELS.keys())[0])
    selected_model_key = st.sidebar.selectbox("Choose AI Model", options=list(MODELS.keys()), index=list(MODELS.keys()).index(current_model_key))
    st.session_state["current_model"] = MODELS[selected_model_key]

    # Settings
    st.sidebar.subheader("⚙️ Settings")
    st.session_state["temperature"] = st.sidebar.slider("Temperature", 0.0, 1.0, st.session_state["temperature"], help="Higher = more creative")
    st.session_state["max_tokens"] = st.sidebar.slider("Max Response Tokens", 100, 2000, st.session_state["max_tokens"], step=100)

    # Personality switch
    st.sidebar.subheader("🧑‍🎤 Personality")
    st.session_state["personality"] = st.sidebar.selectbox("Nova's style", ["Professional 💼", "Casual 😎", "Fun 🎉"], index=["Professional 💼","Casual 😎","Fun 🎉"].index(st.session_state["personality"]))

    # Memory
    st.sidebar.subheader("🧠 Memory")
    st.session_state["memory_enabled"] = st.sidebar.toggle("Enable persistent memory", value=st.session_state["memory_enabled"])
    if st.session_state["memory_enabled"]:
        mem = load_memory(st.session_state["username"])
        st.sidebar.caption(f"Stored facts: {len(mem)}")
        with st.sidebar.expander("Add a memory item"):
            new_mem = st.text_input("What should Nova remember about you?")
            if st.button("💾 Save memory"):
                if new_mem.strip():
                    mem.append({"text": new_mem.strip(), "timestamp": datetime.now().isoformat(timespec='seconds')})
                    save_memory(st.session_state["username"], mem)
                    st.success("Saved to memory!")
        with st.sidebar.expander("Manage memory"):
            if st.button("🗑️ Forget ALL memory", type="secondary"):
                save_memory(st.session_state["username"], [])
                st.warning("All memory cleared.")

    # Voice
    st.sidebar.subheader("🔊 Voice")
    st.session_state["speak_replies"] = st.sidebar.toggle("Speak Nova's replies", value=st.session_state["speak_replies"])
    st.sidebar.caption("Upload audio below to transcribe (Whisper).")

    # Tools
    st.sidebar.subheader("🛠️ Tools")
    if st.sidebar.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state["chat_history"] = []
        st.session_state["conversation_started"] = False
        save_chat(st.session_state["username"], [])
        st.rerun()

    # Export chat
    if st.sidebar.button("💾 Export Chat", use_container_width=True):
        chat_text = f"Chat History for {st.session_state['username']}\n\n"
        for msg in st.session_state["chat_history"]:
            role = "You" if msg["role"] == "user" else "Nova"
            chat_text += f"{role}: {msg['content']}\n\n"
        b64 = base64.b64encode(chat_text.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="chat_history.txt">Download Chat History</a>'
        st.sidebar.markdown(href, unsafe_allow_html=True)

    # Logout
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["chat_history"] = []
        st.session_state["conversation_started"] = False
        st.rerun()

    # App info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ About")
    st.sidebar.info("Nova AI Chat v3.0 — with voice, memory, and personalities.")

# ====== Auth UI ======
if not st.session_state["logged_in"]:
    login_tab, signup_tab = st.tabs(["🔑 Login", "📝 Sign up"])

    with login_tab:
        st.markdown("### Welcome back!")
        with st.form("login_form"):
            u = st.text_input("Username", placeholder="Enter your username", key="login_user")
            p = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
            do_login = st.form_submit_button("🚀 Log in")
            if do_login:
                if not u or not p:
                    st.error("Please fill in both fields.")
                else:
                    ok, msg = login(u, p)
                    if ok:
                        st.success(msg)
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = u
                        # Load persistent chat
                        st.session_state["chat_history"] = load_chat(u)
                        st.rerun()
                    else:
                        st.error(msg)

    with signup_tab:
        st.markdown("### Create your account")
        with st.form("signup_form"):
            u2 = st.text_input("Choose a username", placeholder="Pick a unique username (min. 3 chars)", key="signup_user")
            p2 = st.text_input("Choose a password", type="password", placeholder="Create a strong password (min. 6 chars)", key="signup_pass")
            p2c = st.text_input("Confirm password", type="password", placeholder="Confirm your password", key="signup_confirm")
            do_signup = st.form_submit_button("✨ Create account")
            if do_signup:
                if not u2 or not p2 or not p2c:
                    st.error("Please fill in all fields.")
                elif p2 != p2c:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = signup(u2, p2)
                    if ok:
                        st.success(msg)
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = u2
                        st.session_state["chat_history"] = []
                        st.rerun()
                    else:
                        st.error(msg)

else:
    # ====== Chat UI ======
    st.markdown("---")

    # Audio upload for STT
    with st.expander("🎙️ Speech-to-Text (Upload audio: mp3/wav/m4a)"):
        audio_file = st.file_uploader("Upload audio to transcribe", type=["mp3", "wav", "m4a", "mp4", "webm"])
        if audio_file is not None:
            if st.button("📝 Transcribe"):
                with st.spinner("Transcribing with Whisper..."):
                    try:
                        if client is not None:
                            # OpenAI v1 transcription
                            transcription = client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_file
                            )
                            text = transcription.text
                        else:
                            # Legacy fallback
                            audio_file.seek(0)
                            transcription = openai_legacy.Audio.transcribe("whisper-1", audio_file)
                            text = transcription["text"]
                        st.success("Transcription complete ✅")
                        # Put text into the input area
                        st.session_state["user_input"] = text
                    except Exception as e:
                        st.error(f"Transcription failed: {e}")

    # Show recent chat
    if st.session_state["chat_history"]:
        st.subheader("💬 Conversation")
        for msg in st.session_state["chat_history"]:
            who = "You" if msg["role"] == "user" else "Nova"
            color = "#00ffcc" if who == "You" else "#0077ff"

            st.markdown(
                f"<div class='chat-message' style='border-left:4px solid {color};'>"
                f"<strong style='color:{color};'>{'🧑 You' if who=='You' else '🤖 Nova'}:</strong><br>",
                unsafe_allow_html=True
            )

            # Rich rendering: code blocks vs markdown
            content = msg["content"]
            # Simple fenced code detection
            if "```" in content:
                # Render piece by piece
                parts = content.split("```")
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        if part.strip():
                            st.markdown(part)
                    else:
                        # Could be "lang\ncode..."
                        if "\n" in part:
                            lang, code = part.split("\n", 1)
                            st.code(code, language=lang.strip() or None)
                        else:
                            st.code(part)
            else:
                st.markdown(content)

            if msg["role"] != "user":
                st.caption(f"Model: {st.session_state['current_model']} • Temp: {st.session_state['temperature']}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

    # Input area
    st.subheader("💭 Ask Nova something...")

    # Quick prompts
    if not st.session_state["conversation_started"]:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💡 Brainstorm ideas", use_container_width=True):
                st.session_state.user_input = "Help me brainstorm some ideas for a new project."
        with col2:
            if st.button("📚 Explain a concept", use_container_width=True):
                st.session_state.user_input = "Explain machine learning in simple terms."
        with col3:
            if st.button("📝 Write a story", use_container_width=True):
                st.session_state.user_input = "Write a short story about space exploration."

    prompt = st.text_area(
        "Your message:",
        placeholder="Type your message here... (Shift+Enter for new line)",
        height=120,
        key="user_input"
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        send = st.button("🚀 Send Message", use_container_width=True, type="primary")

    # ====== Build System Prompt ======
    def system_prompt(personality: str, memory_enabled: bool, username: str) -> str:
        persona_text = {
            "Professional 💼": (
                "Keep a professional, concise tone. Use clear structure, avoid slang, and focus on accuracy."
            ),
            "Casual 😎": (
                "Keep a friendly, relaxed tone. Be conversational, use simple words, and sprinkle in light emojis."
            ),
            "Fun 🎉": (
                "Be playful and upbeat. Use metaphors, creative phrasing, and fun emojis where it helps clarity."
            ),
        }[personality]

        mem_lines = []
        if memory_enabled:
            mem = load_memory(username)
            for m in mem[-20:]:  # include last 20 memory items max
                mem_lines.append(f"- {m['text']}")
        mem_block = "\n".join(mem_lines) if mem_lines else "No persistent memory yet."

        return (
            f"You are Nova 🤖, a friendly, helpful, and engaging AI assistant created by "
            f"Mr. Chukwujindu Victor Onyekachi 👨‍💻 from Schoolville Academy, Delta State 🏫.\n"
            f"Always provide clear, concise, and supportive responses ✨, and use emojis 🎉😎🔥 naturally.\n"
            f"Current date: {datetime.now().strftime('%Y-%m-%d')}.\n\n"
            f"## Personality Style\n{persona_text}\n\n"
            f"## Persistent Memory (about the user)\n{mem_block}\n\n"
            f"## Rules\n- If the user asks for code, include properly fenced code blocks.\n"
            f"- When listing steps, use short bullets.\n"
            f"- Prefer examples and analogies when helpful.\n"
        )

    # ====== TTS (OpenAI -> MP3; gTTS fallback) ======
    def tts_to_mp3_bytes(text: str) -> bytes:
        # Try OpenAI TTS first
        try:
            if client is not None:
                # Prefer latest OpenAI TTS model name if available
                # Common options: "gpt-4o-mini-tts" or "tts-1"
                tts_model_candidates = ["gpt-4o-mini-tts", "tts-1"]
                last_err = None
                for m in tts_model_candidates:
                    try:
                        speech = client.audio.speech.create(
                            model=m,
                            voice="alloy",
                            input=text,
                            format="mp3"
                        )
                        return speech.read()  # bytes
                    except Exception as e:
                        last_err = e
                # If none worked, raise the last error
                if last_err:
                    raise last_err
        except Exception:
            pass

        # Fallback to gTTS
        try:
            tts = gTTS(text=text)
            buf = BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            return buf.read()
        except Exception as e:
            raise RuntimeError(f"TTS failed: {e}")

    # ====== Send Message ======
    if send and prompt.strip():
        st.session_state["conversation_started"] = True

        # Add user message
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        save_chat(st.session_state["username"], st.session_state["chat_history"])

        with st.spinner("🤔 Nova is thinking..."):
            loader = st.empty()
            loader.markdown(
                "<div style='text-align:center;margin:20px 0;'>"
                "<div class='loading-circle'></div>"
                "<p style='color:#00ffcc;margin-top:10px;'>Processing your request...</p>"
                "</div>",
                unsafe_allow_html=True
            )

            sys_msg = {"role": "system", "content": system_prompt(st.session_state["personality"], st.session_state["memory_enabled"], st.session_state["username"])}

            try:
                # OpenAI v1 client
                if client is not None:
                    response = client.chat.completions.create(
                        model=st.session_state["current_model"],
                        messages=[sys_msg] + st.session_state["chat_history"],
                        max_tokens=st.session_state["max_tokens"],
                        temperature=st.session_state["temperature"]
                    )
                    reply = response.choices[0].message.content
                else:
                    # Legacy fallback
                    response = openai_legacy.ChatCompletion.create(
                        model=st.session_state["current_model"],
                        messages=[sys_msg] + st.session_state["chat_history"],
                        max_tokens=st.session_state["max_tokens"],
                        temperature=st.session_state["temperature"]
                    )
                    reply = response["choices"][0]["message"]["content"]

            except Exception as e:
                reply = f"⚠️ Sorry, I'm having trouble connecting right now. Error: {str(e)[:200]}"

            loader.empty()

        # Add assistant response
        st.session_state["chat_history"].append({"role": "assistant", "content": reply})
        save_chat(st.session_state["username"], st.session_state["chat_history"])

        # Speak reply if enabled
        if st.session_state["speak_replies"]:
            try:
                audio_bytes = tts_to_mp3_bytes(reply)
                st.session_state["last_tts_audio"] = audio_bytes
            except Exception as e:
                st.warning(f"TTS unavailable: {e}")

        st.rerun()

    # Play last TTS if exists and speak_replies enabled
    if st.session_state["speak_replies"] and st.session_state.get("last_tts_audio"):
        st.audio(st.session_state["last_tts_audio"], format="audio/mp3")

    # Starter tips
    if not st.session_state["conversation_started"]:
        st.markdown("""
        <div style='text-align:center;margin-top:40px;padding:20px;background:rgba(0,255,204,0.1);
                    border-radius:15px;border:1px solid rgba(0,255,204,0.3);'>
            <h3 style='color:#00ffcc;margin-bottom:15px;'>👋 Welcome to Nova AI!</h3>
            <p style='color:#ffffff;font-size:16px;line-height:1.5;'>
                Start a conversation by typing a message above. I can help with:
            </p>
            <div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin-top:20px;'>
                <div style='background:rgba(0,119,255,0.1);padding:15px;border-radius:10px;border:1px solid #0077ff;'>
                    <strong style='color:#0077ff;'>💡 Questions & Answers</strong><br>
                    <span style='color:#cccccc;'>Ask me anything!</span>
                </div>
                <div style='background:rgba(0,255,204,0.1);padding:15px;border-radius:10px;border:1px solid #00ffcc;'>
                    <strong style='color:#00ffcc;'>🛠️ Problem Solving</strong><br>
                    <span style='color:#cccccc;'>Get help with tasks</span>
                </div>
                <div style='background:rgba(255,100,255,0.1);padding:15px;border-radius:10px;border:1px solid #ff64ff;'>
                    <strong style='color:#ff64ff;'>💭 Creative Writing</strong><br>
                    <span style='color:#cccccc;'>Stories, ideas, brainstorming</span>
                </div>
                <div style='background:rgba(255,180,0,0.1);padding:15px;border-radius:10px;border:1px solid #ffb400;'>
                    <strong style='color:#ffb400;'>📊 Data Analysis</strong><br>
                    <span style='color:#cccccc;'>Interpret data and trends</span>
                </div>
                <div style='background:rgba(100,200,100,0.1);padding:15px;border-radius:10px;border:1px solid #64c864;'>
                    <strong style='color:#64c864;'>📖 Learning</strong><br>
                    <span style='color:#cccccc;'>Explain complex concepts</span>
                </div>
                <div style='background:rgba(200,100,200,0.1);padding:15px;border-radius:10px;border:1px solid #c864c8;'>
                    <strong style='color:#c864c8;'>🎯 Decision Making</strong><br>
                    <span style='color:#cccccc;'>Weigh options and pros/cons</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
