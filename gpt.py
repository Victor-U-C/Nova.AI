# ====== IMPORTS ======
import streamlit as st
import os
import json
import hashlib
import base64
from typing import Tuple
import openai
import plotly.graph_objects as go
import tempfile

# ====== API KEY HANDLING ======
if "OPENAI_API_KEY" in st.secrets:   # Streamlit Cloud
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:                                # Local environment
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ====== FILES ======
USER_DATA_FILE = "users.json"
STATS_FILE = "stats.json"

# ====== HELPERS ======
def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
    import hashlib, os, base64
    if salt is None:
        salt = hashlib.sha256(os.urandom(60)).hexdigest()  # always string
    
    pwdhash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    )
    pwdhash = base64.b64encode(pwdhash).decode("ascii")
    return pwdhash, salt

def verify_password(stored_password: str, provided_password: str, salt: str) -> bool:
    pwdhash, _ = hash_password(provided_password, salt)
    return pwdhash == stored_password

def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    return {
        "daily_usage": {},
        "model_usage": {},
        "monthly_usage": {}
    }

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

# ====== OPENAI CALL ======
def call_openai_api(model, messages, max_tokens, temperature, user):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            user=user
        )
        content = response.choices[0].message["content"]
        tokens_used = response.usage.total_tokens
        return content, tokens_used
    except Exception as e:
        st.error(f"❌ OpenAI API Error: {e}")
        return None

# ====== TEXT TO SPEECH ======
def tts_speak(text, voice):
    try:
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text[:4096]
        ) as response:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
                response.stream_to_file(tmpfile.name)
                st.audio(tmpfile.name, format="audio/mp3")
    except Exception as e:
        st.error(f"❌ TTS Error: {e}")

# ====== BACKGROUND ======
def set_bg(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .stChatMessage, .stMarkdown {{
            background-color: rgba(255, 255, 255, 0.8);
            padding: 10px;
            border-radius: 12px;
            margin-bottom: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Ocean background 🌊
set_bg("https://images.unsplash.com/photo-1507525428034-b723cf961d3e")

# ====== STREAMLIT APP ======
st.set_page_config(page_title="Nova AI Chat", page_icon="🤖", layout="wide")

# --- Initialize Session State ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "username" not in st.session_state:
    st.session_state["username"] = None
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ====== LOGIN & SIGNUP ======
users = load_users()

def signup(username, password):
    if username in users:
        return False, "❌ Username already exists."
    hashed_pwd, salt = hash_password(password)
    users[username] = {"password": hashed_pwd, "salt": salt}
    save_users(users)
    return True, "✅ Signup successful!"

def login(username, password):
    if username not in users:
        return False, "❌ Username does not exist."
    stored_pwd = users[username]["password"]
    salt = users[username]["salt"]
    if verify_password(stored_pwd, password, salt):
        return True, "✅ Login successful!"
    else:
        return False, "❌ Incorrect password."

# ====== SIDEBAR ======
with st.sidebar:
    st.header("🔐 User Login")
    if not st.session_state["logged_in"]:
        tab1, tab2 = st.tabs(["Login", "Signup"])
        with tab1:
            uname = st.text_input("Username", key="login_user")
            pwd = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                success, msg = login(uname, pwd)
                st.info(msg)
                if success:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = uname
        with tab2:
            uname_new = st.text_input("New Username", key="signup_user")
            pwd_new = st.text_input("New Password", type="password", key="signup_pass")
            if st.button("Signup"):
                success, msg = signup(uname_new, pwd_new)
                st.info(msg)
    else:
        st.success(f"🟢 Logged in as: {st.session_state['username']}")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None

    # --- Model Settings ---
    st.header("⚙️ Settings")
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-3.5-turbo"])
    max_tokens = st.slider("Max Tokens", 100, 4000, 1000)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    voice = st.selectbox("Voice", ["alloy", "verse", "lumen"])

# ====== MAIN CHAT AREA ======
st.title("😁 Nova AI Chat")

# Show history
for role, msg in st.session_state["chat_history"]:
    if role == "user":
        st.markdown(f"🧑 **You:** {msg}")
    else:
        st.markdown(f"🤖 **Nova:** {msg}")

# User input
user_msg = st.chat_input("Ask Nova…")
if user_msg:
    if not st.session_state["logged_in"]:
        st.warning("🔐 Please login first to chat.")
    else:
        st.session_state["chat_history"].append(("user", user_msg))
        st.markdown(f"🧑 **You:** {user_msg}")

        result = call_openai_api(
            model,
            [{"role": "user", "content": user_msg}],
            max_tokens,
            temperature,
            st.session_state["username"]
        )

        if result:
            response_content, tokens_used = result
            st.session_state["chat_history"].append(("assistant", response_content))
            st.markdown(f"🤖 **Nova:** {response_content}")
            tts_speak(response_content, voice)

# ====== STATISTICS ======
st.header("📊 Usage Statistics")
stats = load_stats()
if stats.get("daily_usage"):
    fig = go.Figure([go.Bar(x=list(stats["daily_usage"].keys()), y=list(stats["daily_usage"].values()))])
    fig.update_layout(title="Daily Usage")
    st.plotly_chart(fig)
else:
    st.info("No usage data yet.")
