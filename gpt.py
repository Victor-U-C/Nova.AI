# ====== IMPORTS & SETUP ======
import streamlit as st
import os
import json
import openai
import time
import hashlib
import re
import uuid
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Tuple, Optional
import requests
from io import BytesIO
import base64
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- API key handling ---
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    ELEVENLABS_API_KEY = st.secrets.get("ELEVENLABS_API_KEY", "")
else:
    openai.api_key = os.getenv("OPENAI_API_KEY", "")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# Initialize OpenAI client for newer API versions
try:
    from openai import OpenAI
    client = OpenAI(api_key=openai.api_key)
except ImportError:
    client = None

# ====== ENHANCED THEME WITH DYNAMIC COLOR SCHEMES ======
def get_custom_css(color_theme="default"):
    themes = {
        "default": {
            "primary": "#00ffcc",
            "secondary": "#0077ff",
            "background": "linear-gradient(135deg, #1a1a1a, #2d2d2d, #1a1a2e)",
            "sidebar": "linear-gradient(135deg, #2d2d2d, #1a1a2e, #333333)"
        },
        "purple": {
            "primary": "#a78bfa",
            "secondary": "#c084fc",
            "background": "linear-gradient(135deg, #1e1b4b, #332c4b, #1e1b4b)",
            "sidebar": "linear-gradient(135deg, #332c4b, #1e1b4b, #4c1d95)"
        },
        "sunset": {
            "primary": "#fb923c",
            "secondary": "#f97316",
            "background": "linear-gradient(135deg, #1c1917, #431407, #7c2d12)",
            "sidebar": "linear-gradient(135deg, #431407, #7c2d12, #9a3412)"
        },
        "ocean": {
            "primary": "#22d3ee",
            "secondary": "#0891b2",
            "background": "linear-gradient(135deg, #0c4a6e, #164e63, #083344)",
            "sidebar": "linear-gradient(135deg, #164e63, #083344, #0e7490)"
        },
        "neon": {
            "primary": "#ff10f0",
            "secondary": "#00ff41",
            "background": "linear-gradient(135deg, #0d0d0d, #1a0d1a, #0d1a0d)",
            "sidebar": "linear-gradient(135deg, #1a0d1a, #0d1a0d, #1a1a0d)"
        }
    }
    
    theme = themes.get(color_theme, themes["default"])
    
    return f"""
<style>
/* Main app background */
.stApp {{
    background: {theme['background']} !important;
    background-size: 400% 400% !important;
    animation: gradientMove 15s ease infinite !important;
    min-height: 100vh !important;
}}

/* Sidebar styling */
[data-testid="stSidebar"] {{
    background: {theme['sidebar']} !important;
    background-size: 400% 400% !important;
    animation: gradientMove 15s ease infinite !important;
}}

/* Gradient animation */
@keyframes gradientMove {{
    0% {{background-position: 0% 50%;}}
    50% {{background-position: 100% 50%;}}
    100% {{background-position: 0% 50%;}}
}}

/* Force ALL text to be visible */
.stApp, .stApp *, .stMarkdown, .stMarkdown *, 
.stText, .stText *, p, span, div, label {{
    color: #ffffff !important;
}}

/* Streamlit specific elements */
.stMarkdown p, .stMarkdown div, .stMarkdown span {{
    color: #ffffff !important;
}}

/* Tab content */
.stTabs [data-baseweb="tab-panel"] {{
    background-color: rgba(45, 45, 45, 0.3) !important;
    padding: 20px !important;
    border-radius: 10px !important;
    border: 1px solid rgba({int(theme['primary'][1:3], 16)},{int(theme['primary'][3:5], 16)},{int(theme['primary'][5:7], 16)},0.2) !important;
}}

/* Headers */
h1, h2, h3, h4, h5, h6 {{
    color: {theme['primary']} !important;
    text-shadow: 0 0 10px rgba({int(theme['primary'][1:3], 16)},{int(theme['primary'][3:5], 16)},{int(theme['primary'][5:7], 16)},0.5);
}}

/* Input fields - ENHANCED VISIBILITY */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    background-color: #3d3d3d !important;
    color: #ffffff !important;
    border: 2px solid {theme['primary']} !important;
    border-radius: 10px !important;
    padding: 15px !important;
    font-size: 16px !important;
    font-weight: normal !important;
}}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {theme['secondary']} !important;
    box-shadow: 0 0 20px rgba({int(theme['primary'][1:3], 16)},{int(theme['primary'][3:5], 16)},{int(theme['primary'][5:7], 16)},0.8) !important;
    outline: none !important;
}}

.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {{
    color: #bbbbbb !important;
    font-style: italic !important;
}}

/* Input labels - MUCH MORE VISIBLE */
.stTextInput > label,
.stTextArea > label {{
    color: {theme['primary']} !important;
    font-weight: bold !important;
    font-size: 18px !important;
    text-shadow: 0 0 5px rgba({int(theme['primary'][1:3], 16)},{int(theme['primary'][3:5], 16)},{int(theme['primary'][5:7], 16)},0.5) !important;
    margin-bottom: 8px !important;
    display: block !important;
}}

/* Buttons with enhanced visibility */
.stButton > button {{
    background: linear-gradient(45deg, {theme['primary']}, {theme['secondary']}) !important;
    color: #000000 !important;
    font-size: 16px !important;
    font-weight: bold !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    cursor: pointer !important;
    box-shadow: 0 4px 15px rgba({int(theme['primary'][1:3], 16)},{int(theme['primary'][3:5], 16)},{int(theme['primary'][5:7], 16)},0.4) !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
}}

.stButton > button:hover {{
    background: linear-gradient(45deg, {theme['secondary']}, {theme['primary']}) !important;
    color: #ffffff !important;
    box-shadow: 0 6px 20px rgba({int(theme['primary'][1:3], 16)},{int(theme['primary'][3:5], 16)},{int(theme['primary'][5:7], 16)},0.8) !important;
    transform: translateY(-2px) scale(1.02) !important;
}}

/* Form containers */
.stForm {{
    background-color: rgba(45, 45, 45, 0.8) !important;
    border: 1px solid {theme['primary']} !important;
    border-radius: 15px !important;
    padding: 20px !important;
    backdrop-filter: blur(10px) !important;
}}

/* Tab styling - FIXED */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px !important;
    background-color: transparent !important;
}}

.stTabs [data-baseweb="tab"] {{
    background-color: #3d3d3d !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    padding: 12px 20px !important;
    border: 2px solid {theme['primary']} !important;
    font-weight: bold !important;
    font-size: 16px !important;
}}

.stTabs [aria-selected="true"] {{
    background-color: {theme['primary']} !important;
    color: #000000 !important;
    border: 2px solid {theme['primary']} !important;
    box-shadow: 0 0 15px rgba({int(theme['primary'][1:3], 16)},{int(theme['primary'][3:5], 16)},{int(theme['primary'][5:7], 16)},0.6) !important;
}}

.stTabs [data-baseweb="tab"]:hover {{
    background-color: #4d4d4d !important;
    box-shadow: 0 0 10px rgba({int(theme['primary'][1:3], 16)},{int(theme['primary'][3:5], 16)},{int(theme['primary'][5:7], 16)},0.3) !important;
}}

/* Messages styling */
.user-message {{
    padding: 15px;
    margin: 10px 0;
    border-radius: 12px;
    border-left: 4px solid {theme['primary']};
    background-color: rgba({int(theme['primary'][1:3], 16)},{int(theme['primary'][3:5], 16)},{int(theme['primary'][5:7], 16)}, 0.1);
    backdrop-filter: blur(5px);
}}

.assistant-message {{
    padding: 15px;
    margin: 10px 0;
    border-radius: 12px;
    border-left: 4px solid {theme['secondary']};
    background-color: rgba({int(theme['secondary'][1:3], 16)},{int(theme['secondary'][3:5], 16)},{int(theme['secondary'][5:7], 16)}, 0.1);
    backdrop-filter: blur(5px);
}}

.system-message {{
    padding: 15px;
    margin: 10px 0;
    border-radius: 12px;
    border-left: 4px solid #9ca3af;
    background-color: rgba(156, 163, 175, 0.1);
    backdrop-filter: blur(5px);
}}

/* Success/Error messages */
.stSuccess {{
    background-color: rgba(0, 255, 100, 0.2) !important;
    color: #00ff64 !important;
    border: 1px solid #00ff64 !important;
}}

.stError {{
    background-color: rgba(255, 100, 100, 0.2) !important;
    color: #ff6464 !important;
    border: 1px solid #ff6464 !important;
}}

.stWarning {{
    background-color: rgba(255, 200, 0, 0.2) !important;
    color: #ffc800 !important;
    border: 1px solid #ffc800 !important;
}}

.stInfo {{
    background-color: rgba(0, 200, 255, 0.2) !important;
    color: #00c8ff !important;
    border: 1px solid #00c8ff !important;
}}

/* Loading animation */
@keyframes pulse {{
    0% {{ transform: scale(1); opacity: 0.6; }}
    50% {{ transform: scale(1.5); opacity: 1; }}
    100% {{ transform: scale(1); opacity: 0.6; }}
}}

.loading-circle {{
    width: 30px;
    height: 30px;
    margin: 20px auto;
    border-radius: 50%;
    background: linear-gradient(45deg, {theme['primary']}, {theme['secondary']});
    animation: pulse 1.5s infinite;
    box-shadow: 0 0 20px rgba({int(theme['primary'][1:3], 16)},{int(theme['primary'][3:5], 16)},{int(theme['primary'][5:7], 16)},0.8);
}}

/* Sidebar text visibility */
.sidebar .element-container {{
    color: #ffffff !important;
}}

/* Audio player styling */
audio {{
    width: 100% !important;
    margin: 10px 0 !important;
    border-radius: 20px;
    background: #3d3d3d;
}}

/* Custom scrollbar */
::-webkit-scrollbar {{
    width: 8px;
}}

::-webkit-scrollbar-track {{
    background: rgba(45, 45, 45, 0.5);
    border-radius: 10px;
}}

::-webkit-scrollbar-thumb {{
    background: {theme['primary']};
    border-radius: 10px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: {theme['secondary']};
}}

/* Code block styling */
code {{
    background-color: #2d2d2d !important;
    padding: 2px 5px !important;
    border-radius: 4px !important;
    color: {theme['primary']} !important;
    font-family: 'Fira Code', monospace !important;
}}

pre {{
    background-color: #2d2d2d !important;
    padding: 15px !important;
    border-radius: 8px !important;
    border-left: 4px solid {theme['primary']} !important;
    overflow-x: auto !important;
}}

pre code {{
    background-color: transparent !important;
    color: #ffffff !important;
}}

/* Progress bars */
.stProgress > div > div > div {{
    background-color: {theme['primary']} !important;
}}

/* Metrics */
[data-testid="metric-container"] {{
    background-color: rgba(45, 45, 45, 0.5) !important;
    border: 1px solid {theme['primary']} !important;
    border-radius: 10px !important;
    padding: 15px !important;
    backdrop-filter: blur(5px) !important;
}}

[data-testid="metric-container"] > div {{
    color: #ffffff !important;
}}

/* Charts */
.js-plotly-plot .plotly .user-select-none {{
    background-color: rgba(45, 45, 45, 0.8) !important;
    border-radius: 10px !important;
}}
</style>
"""

# ====== ENHANCED USER MANAGEMENT ======
USER_FILE = "users.json"
SESSION_FILE = "sessions.json"
STATS_FILE = "user_stats.json"

def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
    """Hash password with salt using SHA-256"""
    if salt is None:
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    pwdhash = base64.b64encode(pwdhash).decode('ascii')
    return pwdhash, salt

def verify_password(stored_password: str, provided_password: str, salt: str) -> bool:
    """Verify a stored password against one provided by user"""
    pwdhash, _ = hash_password(provided_password, salt)
    return pwdhash == stored_password

def load_data(filename: str, default: dict = None) -> dict:
    """Load JSON data from file"""
    if default is None:
        default = {}
    
    if not os.path.exists(filename):
        return default
        
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default

def save_data(data: dict, filename: str):
    """Save JSON data to file"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False

def create_user(username: str, password: str, email: str = None) -> Tuple[bool, str]:
    """Create a new user account"""
    if not username.strip() or not password:
        return False, "Username and password are required."
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    
    # Check for strong password (at least one letter, one number, one special char)
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', password):
        return False, "Password must contain at least one letter, one number, and one special character."
    
    users = load_data(USER_FILE, {})
    
    if username in users:
        return False, "Username already exists."
    
    # Hash password with salt
    hashed_password, salt = hash_password(password)
    
    # Create user record
    users[username] = {
        "password": hashed_password,
        "salt": salt,
        "email": email,
        "created_at": datetime.now(pytz.UTC).isoformat(),
        "last_login": None,
        "preferences": {
            "theme": "default",
            "tts_enabled": False,
            "voice": "alloy",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }
    
    if save_data(users, USER_FILE):
        # Initialize user stats
        init_user_stats(username)
        return True, "Account created successfully!"
    else:
        return False, "Error saving user data."

def authenticate_user(username: str, password: str) -> Tuple[bool, str]:
    """Authenticate a user"""
    users = load_data(USER_FILE, {})
    
    if username not in users:
        return False, "Invalid username or password."
    
    user_data = users[username]
    salt = user_data.get("salt", "")
    
    if verify_password(user_data["password"], password, salt):
        # Update last login
        users[username]["last_login"] = datetime.now(pytz.UTC).isoformat()
        save_data(users, USER_FILE)
        return True, "Login successful!"
    
    return False, "Invalid username or password."

def create_session(username: str) -> str:
    """Create a new session for the user"""
    sessions = load_data(SESSION_FILE, {})
    
    # Generate session token
    session_token = str(uuid.uuid4())
    
    # Store session with expiration (24 hours)
    expires = datetime.now(pytz.UTC) + timedelta(hours=24)
    sessions[session_token] = {
        "username": username,
        "created_at": datetime.now(pytz.UTC).isoformat(),
        "expires_at": expires.isoformat()
    }
    
    save_data(sessions, SESSION_FILE)
    return session_token

def validate_session(session_token: str) -> Tuple[bool, str]:
    """Validate a session token"""
    if not session_token:
        return False, ""
    
    sessions = load_data(SESSION_FILE, {})
    
    if session_token not in sessions:
        return False, ""
    
    session_data = sessions[session_token]
    expires_at = datetime.fromisoformat(session_data["expires_at"])
    
    if datetime.now(pytz.UTC) > expires_at:
        # Session expired
        del sessions[session_token]
        save_data(sessions, SESSION_FILE)
        return False, ""
    
    # Extend session (refresh on each validation)
    new_expires = datetime.now(pytz.UTC) + timedelta(hours=24)
    sessions[session_token]["expires_at"] = new_expires.isoformat()
    save_data(sessions, SESSION_FILE)
    
    return True, session_data["username"]

def delete_session(session_token: str):
    """Delete a session"""
    sessions = load_data(SESSION_FILE, {})
    
    if session_token in sessions:
        del sessions[session_token]
        save_data(sessions, SESSION_FILE)

def get_user_preferences(username: str) -> dict:
    """Get user preferences"""
    users = load_data(USER_FILE, {})
    
    if username in users:
        return users[username].get("preferences", {})
    
    return {}

def update_user_preferences(username: str, preferences: dict):
    """Update user preferences"""
    users = load_data(USER_FILE, {})
    
    if username in users:
        if "preferences" not in users[username]:
            users[username]["preferences"] = {}
        
        users[username]["preferences"].update(preferences)
        save_data(users, USER_FILE)

# ====== USER STATISTICS ======
def init_user_stats(username: str):
    """Initialize user statistics"""
    stats = load_data(STATS_FILE, {})
    
    if username not in stats:
        stats[username] = {
            "total_messages": 0,
            "total_tokens_used": 0,
            "favorite_model": "gpt-3.5-turbo",
            "total_sessions": 0,
            "average_session_length": 0,
            "most_active_day": None,
            "joined_date": datetime.now(pytz.UTC).isoformat(),
            "daily_usage": {},
            "monthly_usage": {},
            "model_usage": {},
            "conversation_topics": []
        }
        
        save_data(stats, STATS_FILE)

def update_user_stats(username: str, message_count: int = 0, tokens_used: int = 0, model: str = None):
    """Update user statistics"""
    stats = load_data(STATS_FILE, {})
    
    if username not in stats:
        init_user_stats(username)
        stats = load_data(STATS_FILE, {})
    
    user_stats = stats[username]
    today = datetime.now(pytz.UTC).strftime("%Y-%m-%d")
    month = datetime.now(pytz.UTC).strftime("%Y-%m")
    
    # Update totals
    user_stats["total_messages"] += message_count
    user_stats["total_tokens_used"] += tokens_used
    
    # Update daily usage
    if today not in user_stats["daily_usage"]:
        user_stats["daily_usage"][today] = {"messages": 0, "tokens": 0}
    
    user_stats["daily_usage"][today]["messages"] += message_count
    user_stats["daily_usage"][today]["tokens"] += tokens_used
    
    # Update monthly usage
    if month not in user_stats["monthly_usage"]:
        user_stats["monthly_usage"][month] = {"messages": 0, "tokens": 0}
    
    user_stats["monthly_usage"][month]["messages"] += message_count
    user_stats["monthly_usage"][month]["tokens"] += tokens_used
    
    # Update model usage
    if model:
        if model not in user_stats["model_usage"]:
            user_stats["model_usage"][model] = 0
        user_stats["model_usage"][model] += message_count
        
        # Update favorite model
        if user_stats["model_usage"][model] > user_stats["model_usage"].get(user_stats["favorite_model"], 0):
            user_stats["favorite_model"] = model
    
    # Find most active day
    if user_stats["daily_usage"]:
        most_active = max(user_stats["daily_usage"].items(), key=lambda x: x[1]["messages"])
        user_stats["most_active_day"] = most_active[0]
    
    stats[username] = user_stats
    save_data(stats, STATS_FILE)

def get_user_stats(username: str) -> dict:
    """Get user statistics"""
    stats = load_data(STATS_FILE, {})
    
    if username not in stats:
        init_user_stats(username)
        return get_user_stats(username)
    
    return stats[username]

# ====== AI FUNCTIONALITY ENHANCEMENTS ======
def call_openai_api(messages: List[Dict], model: str = "gpt-3.5-turbo", 
                   max_tokens: int = 1000, temperature: float = 0.7) -> Tuple[str, int]:
    """Call OpenAI API with enhanced error handling and token counting"""
    if not openai.api_key:
        return "⚠️ API key not configured. Please check your settings.", 0
    
    try:
        # Try with newer OpenAI client first
        if client:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
            return content, tokens_used
        else:
            # Fallback to older API
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            content = response["choices"][0]["message"]["content"]
            tokens_used = response.get("usage", {}).get("total_tokens", 0)
            return content, tokens_used
            
    except openai.error.APIConnectionError:
        return "⚠️ Network error. Please check your internet connection.", 0
    except openai.error.RateLimitError:
        return "⚠️ Rate limit exceeded. Please try again in a moment.", 0
    except openai.error.AuthenticationError:
        return "⚠️ Authentication error. Please check your API key.", 0
    except openai.error.InvalidRequestError as e:
        return f"⚠️ Invalid request: {str(e)}", 0
    except Exception as e:
        return f"⚠️ An unexpected error occurred: {str(e)}", 0

def generate_tts_audio(text: str, voice: str = "alloy") -> Optional[BytesIO]:
    """Generate TTS audio using OpenAI's TTS API"""
    if not openai.api_key or not text.strip():
        return None
    
    try:
        if client:
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text[:4096]  # Limit text length for TTS
            )
            
            # Convert to bytes buffer
            audio_buffer = BytesIO()
            for chunk in response.iter_bytes():
                audio_buffer.write(chunk)
            
            audio_buffer.seek(0)
            return audio_buffer
        else:
            # Fallback for older versions
            return None
    except Exception:
        return None

def generate_with_elevenlabs(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> Optional[BytesIO]:
    """Generate TTS audio using ElevenLabs API"""
    if not ELEVENLABS_API_KEY or not text.strip():
        return None
    
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text[:5000],  # Limit text length
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            audio_buffer = BytesIO(response.content)
            audio_buffer.seek(0)
            return audio_buffer
        else:
            return None
    except Exception:
        return None

# ====== SESSION STATE MANAGEMENT ======
def init_session_state():
    """Initialize session state with all required variables"""
    defaults = {
        "logged_in": False,
        "username": "",
        "session_token": "",
        "chat_history": [],
        "current_model": "gpt-3.5-turbo",
        "tts_enabled": False,
        "tts_service": "openai",  # openai or elevenlabs
        "voice": "alloy",
        "theme": "default",
        "api_available": bool(openai.api_key),
        "conversation_starters": [
            "What can you help me with?",
            "Tell me a fun fact!",
            "How does AI work?",
            "Write a short poem about technology",
            "Explain quantum computing simply",
            "What's the weather like?",
            "Help me brainstorm ideas",
            "Translate something for me",
            "Write code for me",
            "Tell me a joke"
        ],
        "current_page": "chat",
        "user_settings": {},
        "unread_notifications": 0,
        "temperature": 0.7,
        "max_tokens": 1000,
        "system_prompt": "You are Nova, a helpful, creative, and intelligent AI assistant. Be conversational, friendly, and informative in your responses.",
        "auto_scroll": True,
        "show_typing_indicator": True,
        "dark_mode": True
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ====== UI COMPONENTS ======
def render_login_page():
    """Render the login/signup page"""
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
                    ok, msg = authenticate_user(u, p)
                    if ok:
                        session_token = create_session(u)
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = u
                        st.session_state["session_token"] = session_token
                        
                        # Load user preferences
                        prefs = get_user_preferences(u)
                        st.session_state.update(prefs)
                        
                        st.success(msg)
                        time.sleep(1)  # Brief pause for UX
                        st.rerun()
                    else:
                        st.error(msg)
    
    with signup_tab:
        st.markdown("### Create your account")
        with st.form("signup_form"):
            u2 = st.text_input("Choose a username", placeholder="Pick a unique username (min. 3 chars)", key="signup_user")
            p2 = st.text_input("Choose a password", type="password", 
                              placeholder="Create a strong password (min. 8 chars with letters, numbers, and special chars)", 
                              key="signup_pass")
            p2c = st.text_input("Confirm password", type="password", 
                               placeholder="Confirm your password", 
                               key="signup_confirm")
            email = st.text_input("Email (optional)", placeholder="Your email address", key="signup_email")
            
            do_signup = st.form_submit_button("✨ Create account")
            
            if do_signup:
                if not u2 or not p2 or not p2c:
                    st.error("Please fill in all required fields.")
                elif len(u2) < 3:
                    st.error("Username must be at least 3 characters.")
                elif p2 != p2c:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = create_user(u2, p2, email if email else None)
                    if ok:
                        st.success(msg)
                        # Auto-login after signup
                        session_token = create_session(u2)
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = u2
                        st.session_state["session_token"] = session_token
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)

def render_sidebar():
    """Render the application sidebar"""
    with st.sidebar:
        st.title("📂 Nova Menu")
        st.markdown(f"**🟢 Logged in as:** {st.session_state['username']}")
        
        # Theme selector
        theme = st.selectbox(
            "🎨 Theme",
            ["default", "purple", "sunset", "ocean", "neon"],
            index=["default", "purple", "sunset", "ocean", "neon"].index(st.session_state.get("theme", "default")),
            key="theme_selector"
        )
        
        if theme != st.session_state.get("theme", "default"):
            st.session_state["theme"] = theme
            update_user_preferences(st.session_state["username"], {"theme": theme})
            st.rerun()
        
        # Model selector
        model = st.selectbox(
            "🧠 AI Model",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            index=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"].index(st.session_state.get("current_model", "gpt-3.5-turbo")),
            key="model_selector",
            disabled=not st.session_state["api_available"]
        )
        
        if model != st.session_state.get("current_model", "gpt-3.5-turbo"):
            st.session_state["current_model"] = model
            update_user_preferences(st.session_state["username"], {"model": model})
        
        # Advanced Settings
        with st.expander("⚙️ Advanced Settings"):
            temperature = st.slider(
                "🌡️ Temperature (Creativity)",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state.get("temperature", 0.7),
                step=0.1,
                help="Higher values make output more creative but less focused"
            )
            
            max_tokens = st.slider(
                "📝 Max Response Length",
                min_value=100,
                max_value=4000,
                value=st.session_state.get("max_tokens", 1000),
                step=100,
                help="Maximum length of AI responses"
            )
            
            if temperature != st.session_state.get("temperature", 0.7):
                st.session_state["temperature"] = temperature
                update_user_preferences(st.session_state["username"], {"temperature": temperature})
            
            if max_tokens != st.session_state.get("max_tokens", 1000):
                st.session_state["max_tokens"] = max_tokens
                update_user_preferences(st.session_state["username"], {"max_tokens": max_tokens})
        
        # TTS settings
        st.subheader("🔊 Speech Settings")
        tts_enabled = st.checkbox(
            "Enable Text-to-Speech", 
            value=st.session_state.get("tts_enabled", False),
            key="tts_checkbox"
        )
        
        if tts_enabled != st.session_state.get("tts_enabled", False):
            st.session_state["tts_enabled"] = tts_enabled
            update_user_preferences(st.session_state["username"], {"tts_enabled": tts_enabled})
        
        if tts_enabled:
            tts_service = st.radio(
                "TTS Service",
                ["openai", "elevenlabs"],
                index=0 if st.session_state.get("tts_service", "openai") == "openai" else 1,
                horizontal=True,
                key="tts_service_selector"
            )
            
            if tts_service != st.session_state.get("tts_service", "openai"):
                st.session_state["tts_service"] = tts_service
                update_user_preferences(st.session_state["username"], {"tts_service": tts_service})
            
            if tts_service == "openai":
                voice = st.selectbox(
                    "Voice",
                    ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                    index=["alloy", "echo", "fable", "onyx", "nova", "shimmer"].index(
                        st.session_state.get("voice", "alloy")
                    ),
                    key="voice_selector"
                )
                
                if voice != st.session_state.get("voice", "alloy"):
                    st.session_state["voice"] = voice
                    update_user_preferences(st.session_state["username"], {"voice": voice})
            
            elif tts_service == "elevenlabs" and not ELEVENLABS_API_KEY:
                st.warning("ElevenLabs API key not configured. Using OpenAI TTS.")
                st.session_state["tts_service"] = "openai"
        
        # Navigation
        st.subheader("🔍 Navigation")
        page = st.radio(
            "Go to",
            ["💬 Chat", "⚙️ Settings", "📊 Statistics", "ℹ️ About"],
            key="nav_radio"
        )
        
        if "Chat" in page:
            st.session_state["current_page"] = "chat"
        elif "Settings" in page:
            st.session_state["current_page"] = "settings"
        elif "Statistics" in page:
            st.session_state["current_page"] = "stats"
        elif "About" in page:
            st.session_state["current_page"] = "about"
        
        # Actions
        st.subheader("🛠️ Actions")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state["chat_history"] = []
            st.rerun()
        
        if st.button("📥 Export Chat", use_container_width=True):
            export_chat_history()
        
        if st.button("🚪 Logout", use_container_width=True):
            delete_session(st.session_state["session_token"])
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["session_token"] = ""
            st.session_state["chat_history"] = []
            st.rerun()
        
        # Recent messages
        if st.session_state["chat_history"]:
            st.subheader("📜 Recent Messages")
            for i, msg in enumerate(st.session_state["chat_history"][-5:]):
                who = "You" if msg["role"] == "user" else "Nova"
                preview = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
                st.markdown(f"**{who}:** {preview}")

def render_chat_page():
    """Render the main chat page"""
    st.markdown("---")
    
    # Quick action buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🎲 Random Topic", use_container_width=True):
            topics = [
                "Tell me about space exploration",
                "How do neural networks work?",
                "Write a creative story",
                "Explain blockchain technology",
                "What's new in AI research?",
                "Help me learn something new"
            ]
            random_topic = random.choice(topics)
            st.session_state["quick_input"] = random_topic
    
    with col2:
        if st.button("💡 Get Inspired", use_container_width=True):
            inspirations = [
                "Give me 5 creative project ideas",
                "What's an interesting fact about the universe?",
                "Suggest a productivity technique",
                "Recommend a book to read",
                "Share a motivational quote"
            ]
            inspiration = random.choice(inspirations)
            st.session_state["quick_input"] = inspiration
    
    with col3:
        if st.button("🔧 Technical Help", use_container_width=True):
            tech_prompts = [
                "Help me debug this code",
                "Explain a programming concept",
                "Review my project architecture",
                "Suggest best practices",
                "Help with API integration"
            ]
            tech_prompt = random.choice(tech_prompts)
            st.session_state["quick_input"] = tech_prompt
    
    with col4:
        if st.button("🎨 Creative Writing", use_container_width=True):
            creative_prompts = [
                "Write a short story",
                "Create a poem",
                "Help brainstorm characters",
                "Suggest plot twists",
                "Write dialogue for a scene"
            ]
            creative_prompt = random.choice(creative_prompts)
            st.session_state["quick_input"] = creative_prompt
    
    # Display chat history
    if st.session_state["chat_history"]:
        st.subheader("💬 Conversation")
        
        for i, msg in enumerate(st.session_state["chat_history"]):
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong style='color: #00ffcc;'>🧑 You:</strong><br>
                    <span style='color: #ffffff; font-size: 16px;'>{msg['content']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    <strong style='color: #0077ff;'>🤖 Nova:</strong><br>
                    <span style='color: #ffffff; font-size: 16px;'>{msg['content']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Add TTS audio if enabled
                if st.session_state.get("tts_enabled", False):
                    if st.session_state.get("tts_service", "openai") == "openai":
                        audio_data = generate_tts_audio(msg['content'], st.session_state.get("voice", "alloy"))
                    else:
                        audio_data = generate_with_elevenlabs(msg['content'])
                    
                    if audio_data:
                        st.audio(audio_data, format="audio/wav")
    else:
        # Welcome message for new users
        st.markdown("""
        <div style='text-align: center; padding: 40px; background: rgba(45, 45, 45, 0.3); border-radius: 15px; margin: 20px 0;'>
            <h2 style='color: #00ffcc; margin-bottom: 20px;'>👋 Welcome to Nova AI Chat!</h2>
            <p style='font-size: 18px; color: #ffffff; margin-bottom: 30px;'>
                I'm Nova, your intelligent AI assistant. I can help you with:
            </p>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;'>
                <div style='background: rgba(0, 255, 204, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #00ffcc;'>
                    <strong>💡 Creative Tasks</strong><br>
                    Writing, brainstorming, storytelling
                </div>
                <div style='background: rgba(0, 119, 255, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #0077ff;'>
                    <strong>🔧 Technical Help</strong><br>
                    Coding, debugging, explanations
                </div>
                <div style='background: rgba(255, 100, 255, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #ff64ff;'>
                    <strong>📚 Learning</strong><br>
                    Research, explanations, tutorials
                </div>
                <div style='background: rgba(255, 200, 0, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #ffc800;'>
                    <strong>🎯 Problem Solving</strong><br>
                    Analysis, planning, solutions
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Conversation starters
        st.markdown("### 🚀 Quick Start")
        starter_cols = st.columns(2)
        
        for i, starter in enumerate(st.session_state["conversation_starters"][:6]):
            col = starter_cols[i % 2]
            with col:
                if st.button(f"💭 {starter}", key=f"starter_{i}", use_container_width=True):
                    st.session_state["quick_input"] = starter
    
    # Chat input
    st.markdown("---")
    
    # Use quick input if available
    initial_input = st.session_state.get("quick_input", "")
    if "quick_input" in st.session_state:
        del st.session_state["quick_input"]
    
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "💬 Your Message",
            value=initial_input,
            placeholder="Type your message here... Ask me anything!",
            height=100,
            key="user_message_input"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            send_button = st.form_submit_button("🚀 Send", use_container_width=True)
        with col2:
            if st.form_submit_button("🔄 Regenerate", use_container_width=True):
                if st.session_state["chat_history"]:
                    # Remove last assistant message and regenerate
                    if st.session_state["chat_history"][-1]["role"] == "assistant":
                        st.session_state["chat_history"].pop()
                        if st.session_state["chat_history"]:
                            last_user_msg = st.session_state["chat_history"][-1]["content"]
                            handle_user_input(last_user_msg, regenerate=True)
    
    if send_button and user_input.strip():
        handle_user_input(user_input.strip())

def handle_user_input(user_input: str, regenerate: bool = False):
    """Handle user input and generate AI response"""
    if not regenerate:
        # Add user message to history
        st.session_state["chat_history"].append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        })
    
    # Show typing indicator
    if st.session_state.get("show_typing_indicator", True):
        typing_placeholder = st.empty()
        with typing_placeholder:
            st.markdown("""
            <div class="assistant-message">
                <strong style='color: #0077ff;'>🤖 Nova:</strong><br>
                <span style='color: #ffffff; font-size: 16px;'>
                    <div class="loading-circle"></div>
                    Thinking...
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        time.sleep(1)  # Brief pause for UX
        typing_placeholder.empty()
    
    # Prepare messages for API
    messages = [
        {"role": "system", "content": st.session_state.get("system_prompt", "")}
    ]
    
    # Add conversation history (last 10 messages to stay within token limits)
    recent_history = st.session_state["chat_history"][-10:]
    for msg in recent_history:
        if msg["role"] in ["user", "assistant"]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    # Call OpenAI API
    response_content, tokens_used = call_openai_api(
        messages=messages,
        model=st.session_state.get("current_model", "gpt-3.5-turbo"),
        max_tokens=st.session_state.get("max_tokens", 1000),
        temperature=st.session_state.get("temperature", 0.7)
    )
    
    # Add assistant response to history
    st.session_state["chat_history"].append({
        "role": "assistant",
        "content": response_content,
        "timestamp": datetime.now(pytz.UTC).isoformat(),
        "tokens_used": tokens_used
    })
    
    # Update user statistics
    update_user_stats(
        st.session_state["username"],
        message_count=1,
        tokens_used=tokens_used,
        model=st.session_state.get("current_model", "gpt-3.5-turbo")
    )
    
    st.rerun()

def render_settings_page():
    """Render the settings page"""
    st.title("⚙️ Settings")
    st.markdown("---")
    
    # User Profile
    st.header("👤 User Profile")
    users = load_data(USER_FILE, {})
    user_data = users.get(st.session_state["username"], {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Username:** {st.session_state['username']}")
        st.info(f"**Member since:** {user_data.get('created_at', 'Unknown')[:10]}")
        st.info(f"**Last login:** {user_data.get('last_login', 'Unknown')[:10] if user_data.get('last_login') else 'Unknown'}")
    
    with col2:
        st.info(f"**Email:** {user_data.get('email', 'Not provided')}")
        st.info(f"**Current theme:** {st.session_state.get('theme', 'default').title()}")
        st.info(f"**Preferred model:** {st.session_state.get('current_model', 'gpt-3.5-turbo')}")
    
    # System Prompt
    st.header("🎭 AI Personality")
    system_prompt = st.text_area(
        "System Prompt",
        value=st.session_state.get("system_prompt", "You are Nova, a helpful, creative, and intelligent AI assistant."),
        height=150,
        help="This defines how the AI should behave and respond. Changes will affect future conversations."
    )
    
    if system_prompt != st.session_state.get("system_prompt", ""):
        st.session_state["system_prompt"] = system_prompt
        update_user_preferences(st.session_state["username"], {"system_prompt": system_prompt})
    
    # UI Preferences
    st.header("🎨 Interface Preferences")
    
    col1, col2 = st.columns(2)
    with col1:
        auto_scroll = st.checkbox(
            "Auto-scroll to new messages",
            value=st.session_state.get("auto_scroll", True),
            help="Automatically scroll to the bottom when new messages arrive"
        )
        
        show_typing = st.checkbox(
            "Show typing indicator",
            value=st.session_state.get("show_typing_indicator", True),
            help="Display a typing indicator while AI is generating responses"
        )
    
    with col2:
        dark_mode = st.checkbox(
            "Dark mode",
            value=st.session_state.get("dark_mode", True),
            help="Use dark theme for better eye comfort"
        )
    
    # Update preferences
    preferences_to_update = {}
    if auto_scroll != st.session_state.get("auto_scroll", True):
        st.session_state["auto_scroll"] = auto_scroll
        preferences_to_update["auto_scroll"] = auto_scroll
    
    if show_typing != st.session_state.get("show_typing_indicator", True):
        st.session_state["show_typing_indicator"] = show_typing
        preferences_to_update["show_typing_indicator"] = show_typing
    
    if dark_mode != st.session_state.get("dark_mode", True):
        st.session_state["dark_mode"] = dark_mode
        preferences_to_update["dark_mode"] = dark_mode
    
    if preferences_to_update:
        update_user_preferences(st.session_state["username"], preferences_to_update)
    
    # Data Management
    st.header("📊 Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export All Data", use_container_width=True):
            export_user_data()
    
    with col2:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            if st.button("⚠️ Confirm Clear", use_container_width=True):
                st.session_state["chat_history"] = []
                st.success("Chat history cleared!")
                st.rerun()
    
    with col3:
        if st.button("❌ Delete Account", use_container_width=True):
            st.error("This action cannot be undone!")
            confirm = st.text_input("Type 'DELETE' to confirm:", key="delete_confirm")
            if confirm == "DELETE" and st.button("🗑️ Delete Forever", use_container_width=True):
                delete_user_account(st.session_state["username"])
    
    # API Configuration
    st.header("🔑 API Configuration")
    
    if st.session_state["api_available"]:
        st.success("✅ OpenAI API is configured and working!")
    else:
        st.error("❌ OpenAI API key not found. Some features may not work.")
        st.markdown("""
        To use Nova AI Chat fully, you need to configure your OpenAI API key:
        1. Get your API key from [OpenAI](https://platform.openai.com/api-keys)
        2. Add it to your Streamlit secrets or environment variables
        3. Restart the application
        """)
    
    if ELEVENLABS_API_KEY:
        st.success("✅ ElevenLabs API is configured for enhanced TTS!")
    else:
        st.warning("⚠️ ElevenLabs API key not found. Using OpenAI TTS only.")

def render_statistics_page():
    """Render the statistics page"""
    st.title("📊 Statistics")
    st.markdown("---")
    
    # Get user stats
    stats = get_user_stats(st.session_state["username"])
    
    # Overview metrics
    st.header("📈 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Messages",
            stats.get("total_messages", 0),
            delta=None
        )
    
    with col2:
        st.metric(
            "Tokens Used",
            f"{stats.get('total_tokens_used', 0):,}",
            delta=None
        )
    
    with col3:
        st.metric(
            "Favorite Model",
            stats.get("favorite_model", "N/A"),
            delta=None
        )
    
    with col4:
        days_active = len(stats.get("daily_usage", {}))
        st.metric(
            "Days Active",
            days_active,
            delta=None
        )
    
    # Usage charts
    if stats.get("daily_usage"):
        st.header("📅 Daily Usage")
        
        # Prepare data for charts
        daily_data = []
        for date, usage in stats["daily_usage"].items():
            daily_data.append({
                "Date": pd.to_datetime(date),
                "Messages": usage["messages"],
                "Tokens": usage["tokens"]
            })
        
        df_daily = pd.DataFrame(daily_data)
        df_daily = df_daily.sort_values("Date")
        
        # Messages over time
        fig_messages = px.line(
            df_daily, 
            x="Date", 
            y="Messages",
            title="Daily Messages",
            color_discrete_sequence=["#00ffcc"]
        )
        fig_messages.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff"
        )
        st.plotly_chart(fig_messages, use_container_width=True)
        
        # Tokens over time
        fig_tokens = px.area(
            df_daily, 
            x="Date", 
            y="Tokens",
            title="Daily Token Usage",
            color_discrete_sequence=["#0077ff"]
        )
        fig_tokens.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff"
        )
        st.plotly_chart(fig_tokens, use_container_width=True)
    
    # Model usage
    if stats.get("model_usage"):
        st.header("🧠 Model Usage")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart of model usage
            model_data = list(stats["model_usage"].items())
            df_models = pd.DataFrame(model_data, columns=["Model", "Usage"])
            
            fig_pie = px.pie(
                df_models,
                values="Usage",
                names="Model",
                title="Model Usage Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#ffffff"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Bar chart of model usage
            fig_bar = px.bar(
                df_models,
                x="Model",
                y="Usage",
                title="Messages by Model",
                color="Usage",
                color_continuous_scale="Viridis"
            )
            fig_bar.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#ffffff"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Monthly trends
    if stats.get("monthly_usage"):
        st.header("📊 Monthly Trends")
        
        monthly_data = []
        for month, usage in stats["monthly_usage"].items():
            monthly_data.append({
                "Month": month,
                "Messages": usage["messages"],
                "Tokens": usage["tokens"]
            })
        
        df_monthly = pd.DataFrame(monthly_data)
        df_monthly = df_monthly.sort_values("Month")
        
        fig_monthly = px.bar(
            df_monthly,
            x="Month",
            y=["Messages", "Tokens"],)
