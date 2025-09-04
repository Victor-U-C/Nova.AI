# ====== API KEY ======
import streamlit as st
import os
import json
import openai
import time
from datetime import datetime
import base64
from io import BytesIO

# --- API key handling ---
if "OPENAI_API_KEY" in st.secrets:   # Streamlit Cloud
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:                                # Local environment
    openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    st.error("❌ No API key found. Please set OPENAI_API_KEY in Streamlit secrets or environment.")

# ====== Enhanced Dark Theme with Better Visibility ======
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

/* Gradient animation */
@keyframes gradientMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Force ALL text to be visible */
.stApp, .stApp *, .stMarkdown, .stMarkdown *, 
.stText, .stText *, p, span, div, label {
    color: #ffffff !important;
}

/* Streamlit specific elements */
.stMarkdown p, .stMarkdown div, .stMarkdown span {
    color: #ffffff !important;
}

/* Tab content */
.stTabs [data-baseweb="tab-panel"] {
    background-color: rgba(45, 45, 45, 0.3) !important;
    padding: 20px !important;
    border-radius: 10px !important;
    border: 1px solid rgba(0,255,204,0.2) !important;
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
    color: #00ffcc !important;
    text-shadow: 0 0 10px rgba(0,255,204,0.5);
}

/* Input fields - ENHANCED VISIBILITY */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #3d3d3d !important;
    color: #ffffff !important;
    border: 2px solid #00ffcc !important;
    border-radius: 10px !important;
    padding: 15px !important;
    font-size: 16px !important;
    font-weight: normal !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #0077ff !important;
    box-shadow: 0 0 20px rgba(0,255,204,0.8) !important;
    outline: none !important;
}

.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #bbbbbb !important;
    font-style: italic !important;
}

/* Input labels - MUCH MORE VISIBLE */
.stTextInput > label,
.stTextArea > label {
    color: #00ffcc !important;
    font-weight: bold !important;
    font-size: 18px !important;
    text-shadow: 0 0 5px rgba(0,255,204,0.5) !important;
    margin-bottom: 8px !important;
    display: block !important;
}

/* Buttons with enhanced visibility */
.stButton > button {
    background: linear-gradient(45deg, #00ffcc, #0077ff) !important;
    color: #000000 !important;
    font-size: 16px !important;
    font-weight: bold !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    cursor: pointer !important;
    box-shadow: 0 4px 15px rgba(0,255,204,0.4) !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: linear-gradient(45deg, #0077ff, #00ffcc) !important;
    color: #ffffff !important;
    box-shadow: 0 6px 20px rgba(0,255,204,0.8) !important;
    transform: translateY(-2px) scale(1.02) !important;
}

/* Form containers */
.stForm {
    background-color: rgba(45, 45, 45, 0.8) !important;
    border: 1px solid #00ffcc !important;
    border-radius: 15px !important;
    padding: 20px !important;
    backdrop-filter: blur(10px) !important;
}

/* Tab styling - FIXED */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px !important;
    background-color: transparent !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: #3d3d3d !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    padding: 12px 20px !important;
    border: 2px solid #00ffcc !important;
    font-weight: bold !important;
    font-size: 16px !important;
}

.stTabs [aria-selected="true"] {
    background-color: #00ffcc !important;
    color: #000000 !important;
    border: 2px solid #00ffcc !important;
    box-shadow: 0 0 15px rgba(0,255,204,0.6) !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: #4d4d4d !important;
    box-shadow: 0 0 10px rgba(0,255,204,0.3) !important;
}

/* Messages styling */
.chat-message {
    padding: 15px;
    margin: 10px 0;
    border-radius: 12px;
    border-left: 4px solid #00ffcc;
    background-color: rgba(45, 45, 45, 0.7);
    backdrop-filter: blur(5px);
}

/* Success/Error messages */
.stSuccess {
    background-color: rgba(0, 255, 100, 0.2) !important;
    color: #00ff64 !important;
    border: 1px solid #00ff64 !important;
}

.stError {
    background-color: rgba(255, 100, 100, 0.2) !important;
    color: #ff6464 !important;
    border: 1px solid #ff6464 !important;
}

.stWarning {
    background-color: rgba(255, 200, 0, 0.2) !important;
    color: #ffc800 !important;
    border: 1px solid #ffc800 !important;
}

.stInfo {
    background-color: rgba(0, 200, 255, 0.2) !important;
    color: #00c8ff !important;
    border: 1px solid #00c8ff !important;
}

/* Loading animation */
@keyframes pulse {
    0% { transform: scale(1); opacity: 0.6; }
    50% { transform: scale(1.5); opacity: 1; }
    100% { transform: scale(1); opacity: 0.6; }
}

.loading-circle {
    width: 30px;
    height: 30px;
    margin: 20px auto;
    border-radius: 50%;
    background: linear-gradient(45deg, #00ffcc, #0077ff);
    animation: pulse 1.5s infinite;
    box-shadow: 0 0 20px rgba(0,255,204,0.8);
}

/* Sidebar text visibility */
.sidebar .element-container {
    color: #ffffff !important;
}

/* Audio player styling */
audio {
    width: 100% !important;
    margin: 10px 0 !important;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #2d2d2d;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: #00ffcc;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #0077ff;
}

/* Code block styling */
code {
    background-color: #2d2d2d;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
}

pre {
    background-color: #2d2d2d;
    padding: 12px;
    border-radius: 8px;
    overflow-x: auto;
    border-left: 4px solid #00ffcc;
}

/* Chat message animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.chat-message {
    animation: fadeIn 0.3s ease;
}

/* Tooltip styling */
.tooltip {
    position: relative;
    display: inline-block;
}

.tooltip .tooltiptext {
    visibility: hidden;
    width: 120px;
    background-color: #00ffcc;
    color: #000;
    text-align: center;
    border-radius: 6px;
    padding: 5px;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    left: 50%;
    margin-left: -60px;
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
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
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
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
st.session_state.setdefault("current_model", "gpt-3.5-turbo")
st.session_state.setdefault("temperature", 0.7)
st.session_state.setdefault("max_tokens", 500)
st.session_state.setdefault("conversation_started", False)

# ====== AI Models ======
MODELS = {
    "GPT-3.5 Turbo": "gpt-3.5-turbo",
    "GPT-4": "gpt-4",
    "GPT-4 Turbo": "gpt-4-turbo-preview"
}

# ====== Sidebar ======
st.sidebar.title("📂 Menu")
if st.session_state["logged_in"]:
    st.sidebar.markdown(f"**🟢 Logged in as:** {st.session_state['username']}")
    
    # Model selection
    st.sidebar.subheader("🤖 AI Model")
    selected_model = st.sidebar.selectbox(
        "Choose AI Model",
        options=list(MODELS.keys()),
        index=list(MODELS.values()).index(st.session_state["current_model"]) if st.session_state["current_model"] in MODELS.values() else 0,
        help="Select which AI model to use for responses"
    )
    st.session_state["current_model"] = MODELS[selected_model]
    
    # Settings
    st.sidebar.subheader("⚙️ Settings")
    st.session_state["temperature"] = st.sidebar.slider(
        "Temperature", 
        min_value=0.0, 
        max_value=1.0, 
        value=st.session_state["temperature"],
        help="Higher values make output more random, lower values more deterministic"
    )
    st.session_state["max_tokens"] = st.sidebar.slider(
        "Max Response Length", 
        min_value=100, 
        max_value=2000, 
        value=st.session_state["max_tokens"],
        step=100,
        help="Maximum number of tokens in the response"
    )
    
    # Conversation tools
    st.sidebar.subheader("🛠️ Tools")
    if st.sidebar.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state["chat_history"] = []
        st.session_state["conversation_started"] = False
        st.rerun()
    
    if st.sidebar.button("💾 Export Chat", use_container_width=True):
        # Create a downloadable text file of the conversation
        chat_text = f"Chat History for {st.session_state['username']}\n\n"
        for msg in st.session_state["chat_history"]:
            role = "You" if msg["role"] == "user" else "Nova"
            chat_text += f"{role}: {msg['content']}\n\n"
        
        # Create download link
        b64 = base64.b64encode(chat_text.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="chat_history.txt">Download Chat History</a>'
        st.sidebar.markdown(href, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["chat_history"] = []
        st.session_state["conversation_started"] = False
        st.rerun()

    # Recent messages
    st.sidebar.subheader("📜 Recent Messages")
    if st.session_state["chat_history"]:
        for i, msg in enumerate(st.session_state["chat_history"][-5:]):
            who = "You" if msg["role"] == "user" else "Nova"
            preview = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
            st.sidebar.markdown(f"**{who}:** {preview}")
    else:
        st.sidebar.info("No messages yet. Start a conversation!")
    
    # App info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ About")
    st.sidebar.info("Nova AI Chat v2.0\n\nPowered by OpenAI GPT models")

# ====== Main area ======
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

if not st.session_state["logged_in"]:
    # ---- AUTH TABS with better visibility ----
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
                        st.rerun()
                    else:
                        st.error(msg)

else:
    # ---- Chat UI with improved visibility ----
    st.markdown("---")
    
    # Display chat history first
    if st.session_state["chat_history"]:
        st.subheader("💬 Conversation")
        for msg in st.session_state["chat_history"]:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-message" style='background: rgba(0,255,204,0.1); border-left: 4px solid #00ffcc;'>
                    <strong style='color: #00ffcc;'>🧑 You:</strong><br>
                    <span style='color: #ffffff; font-size: 16px;'>{msg['content']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message" style='background: rgba(0,119,255,0.1); border-left: 4px solid #0077ff;'>
                    <strong style='color: #0077ff;'>🤖 Nova:</strong><br>
                    <span style='color: #ffffff; font-size: 16px;'>{msg['content']}</span>
                    <div style='margin-top: 10px; font-size: 12px; color: #888;'>
                        Model: {st.session_state['current_model']} • Temp: {st.session_state['temperature']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("---")

    # Input area with enhanced features
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

    if send and prompt.strip():
        # Mark conversation as started
        st.session_state["conversation_started"] = True
        
        # Add user message
        st.session_state["chat_history"].append({"role": "user", "content": prompt})

        # Show loading indicator
        with st.spinner("🤔 Nova is thinking..."):
            loader = st.empty()
            loader.markdown("""
            <div style='text-align: center; margin: 20px 0;'>
                <div class="loading-circle"></div>
                <p style='color: #00ffcc; margin-top: 10px;'>Processing your request...</p>
            </div>
            """, unsafe_allow_html=True)

            # OpenAI API call
            try:
                # Updated API call for openai>=1.0
                from openai import OpenAI
                client = OpenAI(api_key=openai.api_key)
                
                response = client.chat.completions.create(
                    model=st.session_state["current_model"],
                messages = [
    {
        "role": "system",
        "content": (
            f"You are Nova 🤖, a friendly, helpful, and engaging AI assistant. "
            f"You were created by Mr. Chukwujindu Victor Onyekachi 👨‍💻 from Schoolville Academy, Delta State 🏫. "
            f"Always provide clear, concise, and supportive responses ✨, and use emojis 🎉😎🔥 "
            f"to make conversations more fun and engaging. "
            f"Current date: {datetime.now().strftime('%Y-%m-%d')}"
        )
    }
]

                             + st.session_state["chat_history"],
                    max_tokens=st.session_state["max_tokens"],
                    temperature=st.session_state["temperature"]
                )
                reply = response.choices[0].message.content
                
            except Exception as e:
                # Fallback for older openai versions
                try:
                    resp = openai.ChatCompletion.create(
                        model=st.session_state["current_model"],
                        messages=[{"role": "system", "content": "You are Nova, a friendly and helpful AI assistant."}]
                                 + st.session_state["chat_history"],
                        max_tokens=st.session_state["max_tokens"],
                        temperature=st.session_state["temperature"]
                    )
                    reply = resp["choices"][0]["message"]["content"]
                except Exception as e2:
                    reply = f"⚠️ Sorry, I'm having trouble connecting right now. Error: {str(e2)[:100]}"

            loader.empty()

        # Add assistant response
        st.session_state["chat_history"].append({"role": "assistant", "content": reply})
        st.rerun()

    # Instructions and features
    if not st.session_state["conversation_started"]:
        st.markdown("""
        <div style='text-align: center; margin-top: 40px; padding: 20px; 
                   background: rgba(0,255,204,0.1); border-radius: 15px; 
                   border: 1px solid rgba(0,255,204,0.3);'>
            <h3 style='color: #00ffcc; margin-bottom: 15px;'>👋 Welcome to Nova AI!</h3>
            <p style='color: #ffffff; font-size: 16px; line-height: 1.5;'>
                Start a conversation by typing a message above. I can help with:
            </p>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px;'>
                <div style='background: rgba(0,119,255,0.1); padding: 15px; border-radius: 10px; border: 1px solid #0077ff;'>
                    <strong style='color: #0077ff;'>💡 Questions & Answers</strong><br>
                    <span style='color: #cccccc;'>Ask me anything!</span>
                </div>
                <div style='background: rgba(0,255,204,0.1); padding: 15px; border-radius: 10px; border: 1px solid #00ffcc;'>
                    <strong style='color: #00ffcc;'>🛠️ Problem Solving</strong><br>
                    <span style='color: #cccccc;'>Get help with tasks</span>
                </div>
                <div style='background: rgba(255,100,255,0.1); padding: 15px; border-radius: 10px; border: 1px solid #ff64ff;'>
                    <strong style='color: #ff64ff;'>💭 Creative Writing</strong><br>
                    <span style='color: #cccccc;'>Stories, ideas, brainstorming</span>
                </div>
                <div style='background: rgba(255,180,0,0.1); padding: 15px; border-radius: 10px; border: 1px solid #ffb400;'>
                    <strong style='color: #ffb400;'>📊 Data Analysis</strong><br>
                    <span style='color: #cccccc;'>Interpret data and trends</span>
                </div>
                <div style='background: rgba(100,200,100,0.1); padding: 15px; border-radius: 10px; border: 1px solid #64c864;'>
                    <strong style='color: #64c864;'>📖 Learning</strong><br>
                    <span style='color: #cccccc;'>Explain complex concepts</span>
                </div>
                <div style='background: rgba(200,100,200,0.1); padding: 15px; border-radius: 10px; border: 1px solid #c864c8;'>
                    <strong style='color: #c864c8;'>🎯 Decision Making</strong><br>
                    <span style='color: #cccccc;'>Weigh options and pros/cons</span>
                </div>
            </div>
            
            <div style='margin-top: 30px; padding: 15px; background: rgba(45,45,45,0.5); border-radius: 10px;'>
                <h4 style='color: #00ffcc; margin-bottom: 10px;'>💡 Pro Tips</h4>
                <ul style='text-align: left; color: #cccccc;'>
                    <li>Use the sidebar to switch between AI models (GPT-3.5, GPT-4, etc.)</li>
                    <li>Adjust temperature for more creative (higher) or focused (lower) responses</li>
                    <li>Export your conversations for future reference</li>
                    <li>Try the quick prompts above to get started quickly</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Show conversation tips when conversation is active
        st.markdown("""
        <div style='margin-top: 20px; padding: 15px; background: rgba(45,45,45,0.5); border-radius: 10px;'>
            <h4 style='color: #00ffcc; margin-bottom: 10px;'>💡 Conversation Tips</h4>
            <ul style='color: #cccccc;'>
                <li>Ask follow-up questions for more details</li>
                <li>Use "explain like I'm 5" for simpler explanations</li>
                <li>Request examples to better understand concepts</li>
                <li>Ask for pros and cons when making decisions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


