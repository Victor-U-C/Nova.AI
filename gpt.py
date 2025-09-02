# ====== IMPORTS ======
import streamlit as st
import os, json, hashlib, base64, tempfile
from typing import Tuple
import openai
import plotly.graph_objects as go

# ====== API KEY ======
if "OPENAI_API_KEY" in st.secrets:   # Streamlit Cloud
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:                                # Local environment
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ====== FILES ======
USER_DATA_FILE = "users.json"
STATS_FILE = "stats.json"

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
        .chat-bubble-user {{
            background-color: rgba(0, 123, 255, 0.8);
            color: white;
            padding: 10px;
            border-radius: 15px;
            margin: 5px;
            max-width: 70%;
        }}
        .chat-bubble-ai {{
            background-color: rgba(255, 255, 255, 0.8);
            padding: 10px;
            border-radius: 15px;
            margin: 5px;
            max-width: 70%;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Ocean background
set_bg("https://images.unsplash.com/photo-1507525428034-b723cf961d3e")

# ====== SESSION STATE ======
if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "username" not in st.session_state:
    st.session_state["username"] = None
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ====== LOGIN / SIGNUP PAGE ======
def login_signup_page():
    st.title("🔐 Welcome to Nova AI Chat")
    users = load_users()

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        uname = st.text_input("Username", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if uname not in users:
                st.error("❌ Username does not exist.")
            else:
                stored_pwd = users[uname]["password"]
                salt = users[uname]["salt"]
                if verify_password(stored_pwd, pwd, salt):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = uname
                    st.session_state["page"] = "app"
                    st.success("✅ Login successful!")
                else:
                    st.error("❌ Incorrect password.")

    with tab2:
        uname_new = st.text_input("New Username", key="signup_user")
        pwd_new = st.text_input("New Password", type="password", key="signup_pass")
        if st.button("Signup"):
            if uname_new in users:
                st.error("❌ Username already exists.")
            else:
                hashed_pwd, salt = hash_password(pwd_new)
                users[uname_new] = {"password": hashed_pwd, "salt": salt}
                save_users(users)
                st.success("✅ Signup successful! Please log in.")

# ====== MAIN APP PAGE ======
def main_app():
    st.sidebar.title("⚙️ Settings")
    st.sidebar.success(f"🟢 Logged in as: {st.session_state['username']}")

    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["page"] = "login"

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

    st.header("📊 Usage Statistics")
    stats = {}
    if stats:
        fig = go.Figure([go.Bar(x=list(stats.keys()), y=list(stats.values()))])
        fig.update_layout(title="Usage")
        st.plotly_chart(fig)
    else:
        st.info("No usage data yet.")

# ====== PAGE ROUTER ======
if st.session_state["page"] == "login":
    login_signup_page()
else:
    main_app()
