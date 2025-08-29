# ====== API KEY ======
import streamlit as st
import os
import json
import openai

# --- API key handling ---
if "OPENAI_API_KEY" in st.secrets:   # Streamlit Cloud
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:                                # Local environment
    openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    st.error("❌ No API key found. Please set OPENAI_API_KEY in Streamlit secrets or environment.")

# ====== Dark Glowing Background & Styling ======
st.markdown("""
<style>
.stApp {
  background: linear-gradient(135deg, #000000, #111111, #222222);
  background-size: 400% 400%;
  animation: gradientMove 10s ease infinite;
  min-height: 100vh;
  color: white !important;
}
[data-testid="stSidebar"] {
  background: linear-gradient(135deg, #111111, #222222);
  background-size: 400% 400%;
  animation: gradientMove 10s ease infinite;
  color: white !important;
}
@keyframes gradientMove {
  0% {background-position: 0% 50%;}
  50% {background-position: 100% 50%;}
  100% {background-position: 0% 50%;}
}

/* Input boxes */
.stTextInput > div > div > input {
    background-color: #1e1e1e !important;
    color: white !important;
    border: 1px solid #00ffcc !important;
    border-radius: 10px;
    padding: 10px;
}
.stTextInput > div > div > input::placeholder {
    color: #cccccc !important;
}

/* Password box */
.stTextInput input[type="password"] {
    background-color: #1e1e1e !important;
    color: white !important;
}

/* Buttons */
.stButton>button {
  background-color: #00ffcc !important;   /* solid cyan so it's visible */
  color: #000000 !important;              /* black text, high contrast */
  font-size: 16px !important;
  border: 2px solid #00ffcc !important;
  border-radius: 8px !important;
  padding: 10px 20px !important;
  font-weight: bold !important;
  cursor: pointer !important;
  box-shadow: 0 0 10px rgba(0,255,204,0.8) !important;
  transition: all 0.25s ease-in-out !important;
}

.stButton>button:hover {
  background-color: #0077ff !important;
  color: #ffffff !important;
  box-shadow: 0 0 18px rgba(0,255,204,1) !important;
  transform: scale(1.05) !important;
}


/* Pulsing circle animation */
@keyframes pulse {
  0% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.5); opacity: 1; }
  100% { transform: scale(1); opacity: 0.6; }
}
.loading-circle {
  width: 25px;
  height: 25px;
  margin: 20px auto;
  border-radius: 50%;
  background-color: #00ffcc;
  animation: pulse 1.5s infinite;
}

/* Force all text to white */
html, body, [class*="css"] {
  color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ====== User DB ======
USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_users(users: dict):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def signup(username, password):
    users = load_users()
    if not username.strip() or not password:
        return False, "Username and password required."
    if username in users:
        return False, "Username already exists."
    users[username] = password
    save_users(users)
    return True, "Signup successful!"

def login(username, password):
    users = load_users()
    if username in users and users[username] == password:
        return True, "Login successful!"
    return False, "Invalid username or password."

# ====== Session state ======
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("username", "")
st.session_state.setdefault("chat_history", [])

# ====== Sidebar ======
st.sidebar.title("📂 Menu")
if st.session_state["logged_in"]:
    st.sidebar.write(f"Logged in as **{st.session_state['username']}**")
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["chat_history"] = []
        st.rerun()

    st.sidebar.subheader("📜 Chat history (preview)")
    for msg in st.session_state["chat_history"][-10:]:
        who = "You" if msg["role"] == "user" else "Nova"
        st.sidebar.write(f"**{who}:** {msg['content'][:60]}")

# ====== Main area ======
st.markdown("<h1 style='text-align:center;'>😁 Nova AI Chat</h1>", unsafe_allow_html=True)

if not st.session_state["logged_in"]:
    # ---- AUTH TABS ----
    login_tab, signup_tab = st.tabs(["🔑 Login", "📝 Sign up"])

    with login_tab:
        with st.form("login_form"):
            u = st.text_input("Username", key="login_user")
            p = st.text_input("Password", type="password", key="login_pass")
            do_login = st.form_submit_button("Log in")
            if do_login:
                ok, msg = login(u, p)
                st.info(msg)
                if ok:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = u
                    st.rerun()

    with signup_tab:
        with st.form("signup_form"):
            u2 = st.text_input("Choose a username", key="signup_user")
            p2 = st.text_input("Choose a password", type="password", key="signup_pass")
            p2c = st.text_input("Confirm password", type="password", key="signup_confirm")
            do_signup = st.form_submit_button("Create account")
            if do_signup:
                if p2 != p2c:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = signup(u2, p2)
                    if ok:
                        st.success(msg)
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = u2
                        st.rerun()
                    else:
                        st.error(msg)

else:
    # ---- Chat UI ----
    prompt = st.text_area("Ask Nova… (Shift+Enter for new line)", height=100)
    send = st.button("Send")

    if send and prompt.strip():
        # user message
        st.session_state["chat_history"].append({"role": "user", "content": prompt})

        # show pulsing circle while thinking
        loader = st.empty()
        loader.markdown('<div class="loading-circle"></div>', unsafe_allow_html=True)

        # OpenAI Chat
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are Nova, a friendly AI assistant."}]
                         + st.session_state["chat_history"]
            )
            reply = resp["choices"][0]["message"]["content"]
        except Exception as e:
            reply = f"⚠️ Error: {e}"

        loader.empty()  # remove the circle

        st.session_state["chat_history"].append({"role": "assistant", "content": reply})

        # (Optional) TTS code for openai==0.28
        try:
            audio_resp = openai.Audio.create(
                model="gpt-3.5-tts",
                voice="alloy",
                input=reply
            )
            with open("nova_reply.mp3", "wb") as f:
                f.write(audio_resp)
            st.audio("nova_reply.mp3", format="audio/mp3")
        except Exception as e:
            st.warning(f"TTS failed: {e}")

    # render chat
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f"🧑 **You:** {msg['content']}")
        else:
            st.markdown(f"🤖 **Nova:** {msg['content']}")

