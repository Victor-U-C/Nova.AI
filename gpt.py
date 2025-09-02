# ====== IMPORTS ======
import streamlit as st
import os, json, hashlib, base64, tempfile
from typing import Tuple
import openai

# ====== API KEY ======
if "OPENAI_API_KEY" in st.secrets:   # Streamlit Cloud
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:                                # Local
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ====== FILES ======
USER_DATA_FILE = "users.json"

# ====== PASSWORD HELPERS ======
def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
    if salt is None:
        salt = hashlib.sha256(os.urandom(60)).hexdigest()
    pwdhash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
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

# ====== TTS ======
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

# ====== BACKGROUND & STYLE ======
def set_bg():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #fff;
        }
        .chat-bubble-user {
            background-color: rgba(0, 123, 255, 0.8);
            color: white;
            padding: 10px;
            border-radius: 15px;
            margin: 5px;
            max-width: 70%;
        }
        .chat-bubble-ai {
            background-color: rgba(255, 255, 255, 0.85);
            color: black;
            padding: 10px;
            border-radius: 15px;
            margin: 5px;
            max-width: 70%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg()

# ====== SESSION STATE ======
if "page" not in st.session_state:
    st.session_state["page"] = "auth"
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# ====== AUTH PAGE ======
def auth_page():
    st.markdown("<h1 style='text-align:center;'>🔐 Nova AI Chat</h1>", unsafe_allow_html=True)
    users = load_users()

    login_tab, signup_tab = st.tabs(["🔑 Login", "📝 Sign up"])

    with login_tab:
        with st.form("login_form"):
            uname = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("🚀 Log in"):
                if uname not in users:
                    st.error("❌ Username does not exist.")
                else:
                    stored_pwd = users[uname]["password"]
                    salt = users[uname]["salt"]
                    if verify_password(stored_pwd, pwd, salt):
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = uname
                        st.session_state["page"] = "chat"
                        st.rerun()
                    else:
                        st.error("❌ Incorrect password.")

    with signup_tab:
        with st.form("signup_form"):
            uname_new = st.text_input("Choose a username")
            pwd_new = st.text_input("Password", type="password")
            pwd_confirm = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("✨ Sign up"):
                if uname_new in users:
                    st.error("❌ Username already exists.")
                elif not uname_new or not pwd_new or not pwd_confirm:
                    st.error("❌ Please fill all fields.")
                elif pwd_new != pwd_confirm:
                    st.error("❌ Passwords do not match.")
                else:
                    hashed_pwd, salt = hash_password(pwd_new)
                    users[uname_new] = {"password": hashed_pwd, "salt": salt}
                    save_users(users)
                    st.success("✅ Signup successful! Please login now.")

# ====== CHAT PAGE ======
def chat_page():
    st.sidebar.title("⚙️ Settings")
    st.sidebar.success(f"🟢 Logged in as: {st.session_state['username']}")

    if st.sidebar.button("🚪 Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["page"] = "auth"
        st.rerun()

    model = st.sidebar.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-3.5-turbo"])
    max_tokens = st.sidebar.slider("Max Tokens", 100, 4000, 1000)
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
    voice = st.sidebar.selectbox("Voice", ["alloy", "verse", "lumen"])

    st.title("😁 Nova AI Chat")

    for role, msg in st.session_state["chat_history"]:
        if role == "user":
            st.markdown(f"<div class='chat-bubble-user'>🧑 {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-ai'>🤖 {msg}</div>", unsafe_allow_html=True)

    user_msg = st.chat_input("Ask Nova…")
    if user_msg:
        st.session_state["chat_history"].append(("user", user_msg))
        st.markdown(f"<div class='chat-bubble-user'>🧑 {user_msg}</div>", unsafe_allow_html=True)

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
            st.markdown(f"<div class='chat-bubble-ai'>🤖 {response_content}</div>", unsafe_allow_html=True)
            tts_speak(response_content, voice)

# ====== PAGE ROUTER ======
if st.session_state["page"] == "auth":
    auth_page()
elif st.session_state["page"] == "chat":
    chat_page()
