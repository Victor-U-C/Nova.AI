# gpt.py - Nova AI Chat (new OpenAI SDK + multi-line chat input)
import streamlit as st
import os
import json
from openai import OpenAI

# ====== API KEY / client ======
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ No API key found. Please set OPENAI_API_KEY in Streamlit secrets or environment.")
    st.stop()

client = OpenAI(api_key=api_key)

# ====== CSS: Dark glowing background + white text + input styling ======
st.markdown("""
<style>
.stApp {
  background: linear-gradient(135deg, #0d1b2a, #1b263b, #0d1b2a);
  background-size: 400% 400%;
  animation: gradientMove 12s ease infinite;
  min-height: 100vh;
  color: white !important;
}
[data-testid="stSidebar"] {
  background: linear-gradient(135deg, #1b263b, #0d1b2a);
  color: white !important;
}
@keyframes gradientMove {
  0% {background-position: 0% 50%;}
  50% {background-position: 100% 50%;}
  100% {background-position: 0% 50%;}
}

/* Force all text to white */
* { color: white !important; }

/* Tabs text (Login / Sign up) */
[data-baseweb="tab"] { color: white !important; font-weight: bold; }
[data-baseweb="tab"] [data-testid="stMarkdownContainer"] p { color: white !important; }

/* Input boxes */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #1e1e1e !important;
    color: white !important;
    border: 1px solid #00ffcc !important;
    border-radius: 10px;
    padding: 10px;
}

/* Placeholder text */
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #bfbfbf !important;
}

/* Buttons */
.stButton button {
    background: linear-gradient(90deg, #00ffcc, #0077ff);
    color: white !important;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: bold;
    transition: 0.12s transform;
}
.stButton button:hover { transform: scale(1.02); }

/* Pulsing circle animation */
@keyframes pulse {
  0% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.5); opacity: 1; }
  100% { transform: scale(1); opacity: 0.6; }
}
.loading-circle {
  width: 20px;
  height: 20px;
  margin: 12px auto;
  border-radius: 50%;
  background-color: #00ffcc;
  animation: pulse 1.2s infinite;
}
</style>
""", unsafe_allow_html=True)

# ====== User DB (safe load) ======
USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:
                return {}
            return json.loads(data)
    except (json.JSONDecodeError, ValueError):
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
        st.experimental_rerun()

    st.sidebar.subheader("📜 Chat history (preview)")
    for msg in st.session_state["chat_history"][-10:]:
        who = "You" if msg["role"] == "user" else "Nova"
        st.sidebar.write(f"**{who}:** {msg['content'][:60]}")

# ====== Main area ======
st.markdown("<h1 style='text-align:center;'>😁 Nova AI Chat</h1>", unsafe_allow_html=True)

if not st.session_state["logged_in"]:
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
                    st.experimental_rerun()

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
                        st.experimental_rerun()
                    else:
                        st.error(msg)

else:
    # Use a multi-line text_area so Enter creates a newline.
    # Instructions: Enter = newline, click Send to submit. (If you want Enter-to-send + Shift+Enter newline, I can add a custom component.)
    prompt = st.text_area("Ask Nova… (press Enter for newline — click Send to submit)", height=120, key="chat_input")
    send = st.button("Send")

    if send and prompt and prompt.strip():
        st.session_state["chat_history"].append({"role": "user", "content": prompt})

        # show pulsing circle while thinking
        loader = st.empty()
        loader.markdown('<div class="loading-circle"></div>', unsafe_allow_html=True)

        # Build messages: system prompt + chat history
        messages = [{"role": "system", "content": "You are Nova, a friendly AI assistant."}]
        # ensure chat_history is in correct format (list of dicts)
        messages += st.session_state["chat_history"]

        # Chat (new OpenAI SDK)
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            # extract reply
            reply = resp.choices[0].message.content
        except Exception as e:
            reply = f"⚠️ Error: {e}"

        loader.empty()  # remove loading indicator

        st.session_state["chat_history"].append({"role": "assistant", "content": reply})

        # TTS (new SDK) - uses tts-1 model and streaming-to-file
        try:
            speech_file = "nova_reply.mp3"
            with client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="alloy",
                input=reply
            ) as response:
                response.stream_to_file(speech_file)
            st.audio(speech_file, format="audio/mp3")
        except Exception as e:
            st.warning(f"TTS failed: {e}")

    # render chat history (simple)
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f"🧑 **You:** {msg['content']}")
        else:
            st.markdown(f"🤖 **Nova:** {msg['content']}")
