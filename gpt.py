# ====== API KEY ======
import streamlit as st
import os
import json
import openai
from datetime import datetime
import uuid

# --- API key handling ---
if "OPENAI_API_KEY" in st.secrets:   # Streamlit Cloud
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:                                # Local environment
    openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    st.error("❌ No API key found. Please set OPENAI_API_KEY in Streamlit secrets or environment.")

# ====== Enhanced Dark Theme with ChatGPT-style Layout ======
st.markdown("""
<style>
/* Main app background */
.stApp {
    background: linear-gradient(135deg, #1a1a1a, #2d2d2d, #1a1a2e) !important;
    background-size: 400% 400% !important;
    animation: gradientMove 15s ease infinite !important;
    min-height: 100vh !important;
}

/* Sidebar styling - ChatGPT-like */
[data-testid="stSidebar"] {
    background: #1e1e1e !important;
    border-right: 1px solid #333 !important;
    width: 320px !important;
}

[data-testid="stSidebar"] > div {
    background: #1e1e1e !important;
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

/* Tab content */
.stTabs [data-baseweb="tab-panel"] {
    background-color: rgba(45, 45, 45, 0.3) !important;
    padding: 20px !important;
    border-radius: 10px !important;
    border: 1px solid rgba(0,255,204,0.2) !important;
}

/* Chat conversation item styling */
.chat-item {
    background: rgba(45, 45, 45, 0.6) !important;
    border: 1px solid rgba(0,255,204,0.3) !important;
    border-radius: 10px !important;
    padding: 12px !important;
    margin: 8px 0 !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
}

.chat-item:hover {
    background: rgba(0,255,204,0.1) !important;
    border-color: #00ffcc !important;
    box-shadow: 0 0 10px rgba(0,255,204,0.4) !important;
}

.chat-item.active {
    background: rgba(0,255,204,0.2) !important;
    border-color: #00ffcc !important;
    box-shadow: 0 0 15px rgba(0,255,204,0.6) !important;
}

/* Message styling */
.user-message {
    background: rgba(0,255,204,0.1) !important;
    padding: 15px !important;
    margin: 10px 0 !important;
    border-radius: 12px !important;
    border-left: 4px solid #00ffcc !important;
    color: #ffffff !important;
}

.assistant-message {
    background: rgba(0,119,255,0.1) !important;
    padding: 15px !important;
    margin: 10px 0 !important;
    border-radius: 12px !important;
    border-left: 4px solid #0077ff !important;
    color: #ffffff !important;
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

/* Sidebar content styling */
.sidebar-content {
    color: #ffffff !important;
}

/* Audio player styling */
audio {
    width: 100% !important;
    margin: 10px 0 !important;
}

/* New chat button special styling */
.new-chat-btn {
    background: linear-gradient(45deg, #00ff64, #00ffcc) !important;
    color: #000000 !important;
    font-weight: bold !important;
    margin-bottom: 15px !important;
}
</style>
""", unsafe_allow_html=True)

# ====== Chat Management Functions ======
CHATS_FILE = "user_chats.json"

def load_user_chats():
    if not os.path.exists(CHATS_FILE):
        return {}
    try:
        with open(CHATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_user_chats(chats_data):
    with open(CHATS_FILE, "w", encoding="utf-8") as f:
        json.dump(chats_data, f, indent=2, ensure_ascii=False)

def create_new_chat(username):
    chat_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "id": chat_id,
        "title": "New Chat",
        "created": timestamp,
        "last_updated": timestamp,
        "messages": []
    }

def get_chat_title(messages):
    if not messages:
        return "New Chat"
    first_user_msg = next((msg["content"] for msg in messages if msg["role"] == "user"), "")
    if first_user_msg:
        # Take first 30 characters for title
        title = first_user_msg[:30].strip()
        return title + "..." if len(first_user_msg) > 30 else title
    return "New Chat"

def update_chat_title(chats_data, username, chat_id):
    if username in chats_data and chat_id in chats_data[username]:
        chat = chats_data[username][chat_id]
        chat["title"] = get_chat_title(chat["messages"])
        chat["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_user_chats(chats_data)

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
st.session_state.setdefault("current_chat_id", "")
st.session_state.setdefault("current_messages", [])

# ====== Sidebar - ChatGPT Style ======
if st.session_state["logged_in"]:
    with st.sidebar:
        st.markdown(f"""
        <div style='background: rgba(0,255,204,0.1); padding: 15px; border-radius: 10px; 
                   border: 1px solid #00ffcc; margin-bottom: 20px; text-align: center;'>
            <h3 style='margin: 0; color: #00ffcc;'>👤 {st.session_state['username']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # New Chat Button
        if st.button("✨ New Chat", key="new_chat", help="Start a fresh conversation"):
            chats_data = load_user_chats()
            username = st.session_state["username"]
            
            # Initialize user's chats if not exists
            if username not in chats_data:
                chats_data[username] = {}
            
            # Create new chat
            new_chat = create_new_chat(username)
            chats_data[username][new_chat["id"]] = new_chat
            save_user_chats(chats_data)
            
            # Switch to new chat
            st.session_state["current_chat_id"] = new_chat["id"]
            st.session_state["current_messages"] = []
            st.rerun()

        st.markdown("---")
        st.subheader("💬 Chat History")
        
        # Load and display chats
        chats_data = load_user_chats()
        username = st.session_state["username"]
        
        if username in chats_data and chats_data[username]:
            # Sort chats by last_updated (most recent first)
            sorted_chats = sorted(
                chats_data[username].items(),
                key=lambda x: x[1]["last_updated"],
                reverse=True
            )
            
            for chat_id, chat in sorted_chats:
                # Create a container for each chat
                chat_container = st.container()
                
                with chat_container:
                    # Check if this is the active chat
                    is_active = (chat_id == st.session_state["current_chat_id"])
                    
                    # Style based on active state
                    if is_active:
                        bg_style = "background: rgba(0,255,204,0.2); border: 2px solid #00ffcc;"
                    else:
                        bg_style = "background: rgba(45,45,45,0.4); border: 1px solid rgba(0,255,204,0.2);"
                    
                    # Chat item button
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        if st.button(
                            f"📄 {chat['title']}", 
                            key=f"chat_{chat_id}",
                            help=f"Created: {chat['created']}"
                        ):
                            st.session_state["current_chat_id"] = chat_id
                            st.session_state["current_messages"] = chat["messages"].copy()
                            st.rerun()
                    
                    with col2:
                        if st.button("🗑️", key=f"delete_{chat_id}", help="Delete this chat"):
                            del chats_data[username][chat_id]
                            save_user_chats(chats_data)
                            if chat_id == st.session_state["current_chat_id"]:
                                st.session_state["current_chat_id"] = ""
                                st.session_state["current_messages"] = []
                            st.rerun()
                    
                    # Show message count and date
                    msg_count = len(chat["messages"]) // 2  # Divide by 2 since we count user+assistant pairs
                    st.markdown(f"""
                    <div style='{bg_style} padding: 8px; border-radius: 8px; margin-bottom: 8px;'>
                        <small style='color: #cccccc;'>
                            💭 {msg_count} messages • {chat['created'][:10]}
                        </small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='text-align: center; padding: 20px; color: #888;'>
                <p>No chat history yet.<br>Start a new conversation!</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["current_chat_id"] = ""
            st.session_state["current_messages"] = []
            st.rerun()

# ====== Main area ======
if not st.session_state["logged_in"]:
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='font-size: 3em; background: linear-gradient(45deg, #00ffcc, #0077ff); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       text-shadow: 0 0 30px rgba(0,255,204,0.8);'>
                🤖 Nova AI Chat
            </h1>
            <p style='font-size: 1.2em; color: #cccccc; margin-top: 10px;'>
                Your intelligent AI assistant with persistent chat history
            </p>
        </div>
        """, unsafe_allow_html=True)

        # ---- AUTH TABS ----
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
                u2 = st.text_input("Choose a username", placeholder="Pick a unique username", key="signup_user")
                p2 = st.text_input("Choose a password", type="password", placeholder="Create a strong password", key="signup_pass")
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
    # ---- Main Chat Interface ----
    # Header
    if st.session_state["current_chat_id"]:
        chats_data = load_user_chats()
        username = st.session_state["username"]
        current_chat = chats_data.get(username, {}).get(st.session_state["current_chat_id"], {})
        chat_title = current_chat.get("title", "Chat")
        
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h2 style='color: #00ffcc; margin: 0;'>💬 {chat_title}</h2>
            <p style='color: #888; margin: 5px 0;'>
                Created: {current_chat.get("created", "Unknown")[:16]}
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h2 style='color: #00ffcc;'>🤖 Nova AI Chat</h2>
            <p style='color: #888;'>Select a chat from the sidebar or start a new one!</p>
        </div>
        """, unsafe_allow_html=True)

    # Display current chat messages
    if st.session_state["current_messages"]:
        st.markdown("### 📜 Conversation")
        
        for msg in st.session_state["current_messages"]:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong style='color: #00ffcc;'>🧑 You:</strong><br>
                    <span style='color: #ffffff; font-size: 16px; line-height: 1.5;'>{msg['content']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    <strong style='color: #0077ff;'>🤖 Nova:</strong><br>
                    <span style='color: #ffffff; font-size: 16px; line-height: 1.5;'>{msg['content']}</span>
                </div>
                """, unsafe_allow_html=True)

    # Message input area
    st.markdown("---")
    st.markdown("### 💭 Send a message")
    
    prompt = st.text_area(
        "Your message:", 
        placeholder="Ask Nova anything... (Shift+Enter for new line)",
        height=120,
        key="user_input"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        send = st.button("🚀 Send Message", use_container_width=True)

    if send and prompt.strip():
        # Ensure we have a current chat
        if not st.session_state["current_chat_id"]:
            # Create new chat if none exists
            chats_data = load_user_chats()
            username = st.session_state["username"]
            
            if username not in chats_data:
                chats_data[username] = {}
            
            new_chat = create_new_chat(username)
            chats_data[username][new_chat["id"]] = new_chat
            save_user_chats(chats_data)
            
            st.session_state["current_chat_id"] = new_chat["id"]
            st.session_state["current_messages"] = []

        # Add user message
        user_message = {"role": "user", "content": prompt}
        st.session_state["current_messages"].append(user_message)

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
                # Try newer API first
                from openai import OpenAI
                client = OpenAI(api_key=openai.api_key)
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "You are Nova, a friendly and helpful AI assistant. Provide clear, concise, and engaging responses."}]
                             + st.session_state["current_messages"],
                    max_tokens=800,
                    temperature=0.7
                )
                reply = response.choices[0].message.content
                
            except Exception as e:
                # Fallback for older openai versions
                try:
                    resp = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": "You are Nova, a friendly and helpful AI assistant."}]
                                 + st.session_state["current_messages"],
                        max_tokens=800,
                        temperature=0.7
                    )
                    reply = resp["choices"][0]["message"]["content"]
                except Exception as e2:
                    reply = f"⚠️ Sorry, I'm having trouble connecting right now. Please check your API key and try again."

            loader.empty()

        # Add assistant response
        assistant_message = {"role": "assistant", "content": reply}
        st.session_state["current_messages"].append(assistant_message)

        # Save to persistent storage
        chats_data = load_user_chats()
        username = st.session_state["username"]
        chat_id = st.session_state["current_chat_id"]
        
        if username in chats_data and chat_id in chats_data[username]:
            chats_data[username][chat_id]["messages"] = st.session_state["current_messages"].copy()
            update_chat_title(chats_data, username, chat_id)

        # Clear input and refresh
        st.rerun()

    # Welcome message for empty chats
    if not st.session_state["current_messages"]:
        st.markdown("""
        <div style='text-align: center; margin-top: 40px; padding: 30px; 
                   background: rgba(0,255,204,0.05); border-radius: 20px; 
                   border: 1px solid rgba(0,255,204,0.2);'>
            <h3 style='color: #00ffcc; margin-bottom: 20px;'>👋 Welcome to Nova AI!</h3>
            <p style='color: #ffffff; font-size: 18px; line-height: 1.6; margin-bottom: 25px;'>
                Start a conversation by typing a message below. I can help with:
            </p>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 25px;'>
                <div style='background: rgba(0,119,255,0.1); padding: 20px; border-radius: 12px; border: 1px solid #0077ff;'>
                    <strong style='color: #0077ff; font-size: 18px;'>💡 Questions & Answers</strong><br>
                    <span style='color: #cccccc; margin-top: 8px; display: block;'>Ask me anything you want to know!</span>
                </div>
                <div style='background: rgba(0,255,204,0.1); padding: 20px; border-radius: 12px; border: 1px solid #00ffcc;'>
                    <strong style='color: #00ffcc; font-size: 18px;'>🛠️ Problem Solving</strong><br>
                    <span style='color: #cccccc; margin-top: 8px; display: block;'>Get help with coding, math, and tasks</span>
                </div>
                <div style='background: rgba(255,100,255,0.1); padding: 20px; border-radius: 12px; border: 1px solid #ff64ff;'>
                    <strong style='color: #ff64ff; font-size: 18px;'>💭 Creative Writing</strong><br>
                    <span style='color: #cccccc; margin-top: 8px; display: block;'>Stories, ideas, and brainstorming</span>
                </div>
            </div>
            <div style='margin-top: 30px; padding: 15px; background: rgba(0,255,204,0.05); border-radius: 10px;'>
                <p style='color: #00ffcc; font-size: 16px; margin: 0;'>
                    💡 <strong>Tip:</strong> Your conversations are automatically saved! Switch between chats using the sidebar.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    # Show login page with better styling
    st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='font-size: 3.5em; background: linear-gradient(45deg, #00ffcc, #0077ff); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   text-shadow: 0 0 30px rgba(0,255,204,0.8); margin-bottom: 10px;'>
            🤖 Nova AI Chat
