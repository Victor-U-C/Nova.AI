import streamlit as st
import json, os
import openai

# ====== API KEY ======
# ✅ Option 1: safer way (use environment variable)
openai.api_key = os.getenv("OPENAI_API_KEY")


# ✅ Option 2: direct (for testing only – replace with your real key!)
# openai.api_key = "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx"

# ====== Glowing background ======
st.markdown("""
<style>
.stApp {
  background: linear-gradient(135deg, #00ff00, #ffff00, #ff6600);
  background-size: 400% 400%;
  animation: gradientMove 10s ease infinite;
  min-height: 100vh;
}
[data-testid="stSidebar"] {
  background: linear-gradient(135deg, #00ff00, #ffff00);
  background-size: 400% 400%;
  animation: gradientMove 10s ease infinite;
}
@keyframes gradientMove {
  0% {background-position: 0% 50%;}
  50% {background-position: 100% 50%;}
  100% {background-position: 0% 50%;}
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
    prompt = st.text_input("Ask Nova…")
    send = st.button("Send")

    if send and prompt.strip():
        # user message
        st.session_state["chat_history"].append({"role": "user", "content": prompt})

        # show pulsing circle while thinking
        loader = st.empty()
        loader.markdown('<div class="loading-circle"></div>', unsafe_allow_html=True)

        # OpenAI Chat
        try:
            resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are Nova, a friendly AI assistant."}]
                         + st.session_state["chat_history"]
            )
            reply = resp.choices[0].message.content
        except Exception as e:
            reply = f"⚠️ Error: {e}"

        loader.empty()  # remove the circle

        st.session_state["chat_history"].append({"role": "assistant", "content": reply})

        # OpenAI TTS (turn text into audio)
        try:
            with open("nova_reply.mp3", "wb") as f:
                tts_resp = openai.audio.speech.create(
                    model="gpt-4o-mini-tts",
                    voice="alloy",
                    input=reply
                )
                f.write(tts_resp.read())
            st.audio("nova_reply.mp3", format="audio/mp3")
        except Exception as e:
            st.warning(f"TTS failed: {e}")

    # render chat
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f"🧑 **You:** {msg['content']}")
        else:
            st.markdown(f"🤖 **Nova:** {msg['content']}")

