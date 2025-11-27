import streamlit as st
import speech_recognition as sr
import webbrowser
import requests
from openai import OpenAI
from gtts import gTTS
import pygame
import os
import time
from datetime import datetime

# --- CONFIGURATION ---
NEWS_API_KEY = "YOUR_NEWS_API KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# Initialize recognizer
recognizer = sr.Recognizer()

# Initialize pygame mixer for audio playback
if not pygame.mixer.get_init():
    pygame.mixer.init()

# Music library
music = {
    "song1": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "despacito": "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
    "shape": "https://www.youtube.com/watch?v=JGwWNGJdvx8",
    "stealth": "https://www.youtube.com/watch?v=U47Tr9BB_wE",
    "march": "https://www.youtube.com/watch?v=Xqeq4b5u_Xw",
    "skyfall": "https://www.youtube.com/watch?v=DeumyOzKqgI&pp=ygUHc2t5ZmFsbA%3D%3D",
    "wolf": "https://www.youtube.com/watch?v=ThCH0U6aJpU&list=PLnrGi_-oOR6wm0Vi-1OsiLiV5ePSPs9oF&index=21"

}

# --- BACKEND LOGIC ---

def stop_audio():
    """Stop any currently playing audio and release the file lock"""
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        # CRITICAL FIX: Unload releases the file so it can be overwritten
        pygame.mixer.music.unload()
    except Exception as e:
        pass

def speak(text):
    """Convert text to speech and play it asynchronously with file handling"""
    try:
        stop_audio()
        
        # Give the OS a tiny moment to release the file lock
        time.sleep(0.1)
        
        # Safely remove the old file if it exists
        if os.path.exists('temp.mp3'):
            try:
                os.remove('temp.mp3')
            except PermissionError:
                st.warning("Audio file is locked. Please wait a moment.")
                return

        tts = gTTS(text)
        tts.save('temp.mp3')
        pygame.mixer.music.load('temp.mp3')
        pygame.mixer.music.play()
    except Exception as e:
        st.error(f"Audio Error: {e}")

def aiProcess(command):
    """Process command using OpenAI GPT-4o"""
    client = OpenAI(api_key=OPENAI_API_KEY)
    system_instruction = (
        "You are Jarvis, a highly advanced AI assistant inspired by Iron Man's AI. "
        f"Current context: Today is {datetime.now().strftime('%B %d, %Y')}. "
        "The current President of the United States is Donald Trump. "
        "Give short, witty, and highly intelligent responses with a touch of British sophistication."
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": command}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"OpenAI Error: {e}"

def processCommand(c):
    """Process user commands"""
    c_lower = c.lower()
    
    if "open google" in c_lower:
        webbrowser.open("https://google.com")
        return "Opening Google, sir."
    
    elif "open facebook" in c_lower:
        webbrowser.open("https://facebook.com")
        return "Accessing Facebook now."
    
    elif "open youtube" in c_lower:
        webbrowser.open("https://youtube.com")
        return "Opening YouTube for you."
    
    elif c_lower.startswith("play"):
        try:
            # Safer split logic
            parts = c_lower.split(" ", 1)
            song = parts[1] if len(parts) > 1 else ""
            
            if song in music:
                webbrowser.open(music[song])
                return f"Playing {song} now, sir."
            else:
                return f"I couldn't find '{song}' in your music library."
        except:
            return "Please specify a song name."
    
    elif "news" in c_lower:
        try:
            r = requests.get(
                f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}",
                timeout=5
            )
            if r.status_code == 200:
                data = r.json()
                headlines = [a['title'] for a in data.get('articles', [])[:3]]
                if headlines:
                    return "Top headlines: " + ". ".join(headlines)
                return "No headlines available at the moment."
            return "Unable to fetch news. Please check your API key."
        except Exception as e:
            return f"Error connecting to news service: {str(e)}"
    
    else:
        return aiProcess(c)

def listen_mic(status_placeholder):
    """Listen to microphone input and convert to text"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        status_placeholder.markdown(
            "<p class='status-text blink'>LISTENING...</p>", 
            unsafe_allow_html=True
        )
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=8, phrase_time_limit=15)
            status_placeholder.markdown(
                "<p class='status-text'>PROCESSING...</p>", 
                unsafe_allow_html=True
            )
            word = r.recognize_google(audio)
            return word
        except sr.WaitTimeoutError:
            status_placeholder.markdown(
                "<p class='status-text' style='color:#ff4b4b;'>NO INPUT DETECTED</p>", 
                unsafe_allow_html=True
            )
            return None
        except sr.UnknownValueError:
            status_placeholder.markdown(
                "<p class='status-text' style='color:#ff4b4b;'>COULD NOT UNDERSTAND</p>", 
                unsafe_allow_html=True
            )
            return None
        except Exception as e:
            status_placeholder.markdown(
                f"<p class='status-text' style='color:#ff4b4b;'>ERROR: {str(e)}</p>", 
                unsafe_allow_html=True
            )
            return None

# --- FRONTEND UI ---

st.set_page_config(page_title="J.A.R.V.I.S", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    /* Global Background */
    .stApp { 
        background-color: #0E1117; 
    }
    
    /* Header Styles */
    .main-header { 
        font-family: 'Courier New', monospace; 
        text-align: center; 
        color: #00ADB5; 
        text-shadow: 0 0 20px #00ADB5, 0 0 40px #00ADB5;
        font-size: 5rem; 
        font-weight: bold; 
        margin-bottom: 0px; 
        padding-bottom: 0px;
        letter-spacing: 15px;
    }
    
    .sub-header { 
        text-align: center; 
        color: #EEEEEE; 
        margin-bottom: 40px;
        margin-top: 10px;
        font-size: 1.2rem; 
        letter-spacing: 8px; 
        opacity: 0.8;
        font-family: 'Courier New', monospace;
    }
    
    /* Button Container Centering */
    div.stButton {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    /* Button Base Styling */
    div.stButton > button {
        width: 100%;                
        height: 60px;
        border-radius: 5px;        
        font-size: 18px; 
        font-weight: bold; 
        letter-spacing: 3px;
        text-transform: uppercase;
        border: none;
        transition: all 0.3s ease;
        display: block;
        margin: 0 auto !important;
        margin-bottom: 20px !important;
        font-family: 'Courier New', monospace;
        cursor: pointer;
    }
    
    /* ACTIVATE BUTTON (Cyan) */
    div.stButton > button:not([kind="primary"]) {
        background: linear-gradient(135deg, #00ADB5 0%, #007B82 100%);
        color: white;
        box-shadow: 0 0 15px rgba(0, 173, 181, 0.5);
    }
    
    div.stButton > button:not([kind="primary"]):hover {
        background: linear-gradient(135deg, #00E5FF 0%, #00ADB5 100%);
        box-shadow: 0 0 30px #00ADB5, 0 0 50px #00ADB5;
        transform: scale(1.05);
    }

    /* STOP BUTTON (Red) */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2b0a0a 0%, #1a0505 100%) !important;
        color: #ff4b4b !important; 
        border: 2px solid #ff4b4b !important;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.3) !important;
    }
    
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #ff4b4b 0%, #cc0000 100%) !important;
        color: white !important; 
        box-shadow: 0 0 30px #ff4b4b, 0 0 50px #ff4b4b !important;
        transform: scale(1.05);
    }

    /* Status Text */
    .status-text {
        text-align: center; 
        font-family: 'Courier New', monospace;
        color: #00ADB5; 
        font-size: 1.5rem; 
        font-weight: bold; 
        margin-top: 30px;
        margin-bottom: 20px;
        letter-spacing: 3px;
    }
    
    /* Blinking Animation */
    @keyframes blinker { 
        0% { opacity: 1; }
        50% { opacity: 0.3; } 
        100% { opacity: 1; }
    }
    
    .blink { 
        animation: blinker 1.2s ease-in-out infinite; 
    }
    
    /* Response Box */
    .response-box {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        border: 1px solid #30363d;
        border-left: 5px solid #00ADB5;
        border-radius: 8px;
        padding: 30px; 
        margin-top: 40px; 
        color: #e0e0e0; 
        font-family: 'Segoe UI', sans-serif;
        box-shadow: 0 4px 20px rgba(0, 173, 181, 0.2);
    }
    
    .response-box hr {
        border: none;
        border-top: 1px solid #30363d;
        margin: 20px 0;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove top padding */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h1 class='main-header'>J.A.R.V.I.S</h1>", unsafe_allow_html=True)

# --- BUTTON LAYOUT: Perfect Centering ---
# Using [1.5, 1, 1.5] for reliable centering
col1, col2, col3 = st.columns([1.5, 1, 1.5])

with col2:
    # ACTIVATE BUTTON
    activate_btn = st.button("🎙️ ACTIVATE SYSTEM")
    
    # STOP BUTTON
    stop_btn = st.button("🔴 TERMINATE AUDIO", type="primary")
    
    # STATUS PLACEHOLDER
    status_placeholder = st.empty()

# --- LOGIC ---

# Handle stop button
if stop_btn:
    stop_audio()
    status_placeholder.markdown(
        "<p class='status-text' style='color:#ff4b4b;'>AUDIO TERMINATED</p>", 
        unsafe_allow_html=True
    )

# Handle activate button
if activate_btn:
    stop_audio()
    user_input = listen_mic(status_placeholder)
    
    if user_input:
        status_placeholder.empty()
        response = processCommand(user_input)
        
        # Store in session state
        if "history" not in st.session_state:
            st.session_state.history = []
        st.session_state.history.insert(0, {"user": user_input, "jarvis": response})
        
        # Speak the response
        speak(response)

# --- DISPLAY CHAT HISTORY ---
if "history" in st.session_state and st.session_state.history:
    latest = st.session_state.history[0]
    st.markdown(f"""
    <div style="max-width: 900px; margin: 0 auto;">
        <div class='response-box'>
            <p style="color:#888; font-size:0.85rem; margin-bottom:8px; letter-spacing:2px;">USER COMMAND:</p>
            <p style="font-size:1.5rem; margin-bottom:20px; color:#00E5FF;"><b>"{latest['user']}"</b></p>
            <hr>
            <p style="color:#00ADB5; font-size:0.85rem; margin-bottom:8px; letter-spacing:2px;">JARVIS RESPONSE:</p>
            <p style="line-height: 1.8; font-size: 1.15rem;">{latest['jarvis']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- FOOTER INFO ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align: center; color: #555; font-size: 0.8rem; font-family: monospace;'>
Powered by OpenAI GPT-4o | Speech Recognition | Google TTS
</p>
""", unsafe_allow_html=True)