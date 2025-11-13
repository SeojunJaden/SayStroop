import streamlit as st
import random
import time
from datetime import datetime
import openai
from openai import OpenAI
import os
from pathlib import Path
import base64
from dotenv import load_dotenv

# Page config
st.set_page_config(
    page_title="sayStroop - Stroop Effect Test",
    page_icon="🧠",
    layout="wide"
)

#api key from .env!! 
load_dotenv()
st.write("Key loaded:", bool(os.getenv("OPENAI_API_KEY")))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Custom CSS and JavaScript 
st.markdown("""
<style>
    .main {
        background-color: #000000;
    }
    .stApp {
        background-color: white;
    }
    .stroop-word {
        font-size: 120px;
        font-weight: bold;
        text-align: center;
        padding: 20px 50px;
        text-transform: uppercase;
        letter-spacing: -2px;
    }
    .progress {
        font-size: 24px;
        color: #666;
        text-align: center;
        margin-bottom: 15px;
        margin-top: 20px;
    }
    .recording-indicator {
        text-align: center;
        color: #ef4444;
        font-size: 28px;
        padding: 20px;
        animation: pulse 1.5s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .centered-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        padding-top: 40px;
        min-height: 100vh;
    }
    .test-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        padding-top: 20px;
        width: 100%;
    }
    .welcome-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 10px 40px;
    }
    .mic-button {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background-color: #ef4444;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px auto;
        font-size: 48px;
        transition: all 0.3s;
    }
    .mic-button:hover {
        background-color: #dc2626;
        transform: scale(1.1);
    }
    .mic-button.recording {
        background-color: #22c55e;
        animation: recording-pulse 1s ease-in-out infinite;
    }
    @keyframes recording-pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
</style>
""", unsafe_allow_html=True)

#session state
if 'started' not in st.session_state:
    st.session_state.started = False
if 'current_trial' not in st.session_state:
    st.session_state.current_trial = 1
if 'results' not in st.session_state:
    st.session_state.results = []
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'current_word' not in st.session_state:
    st.session_state.current_word = None
if 'current_color' not in st.session_state:
    st.session_state.current_color = None
if 'audio_files' not in st.session_state:
    st.session_state.audio_files = []
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'mic_enabled' not in st.session_state:
    st.session_state.mic_enabled = False

# Color definitions
COLORS = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
COLOR_MAP = {
    'red': '#ef4444',
    'blue': '#3b82f6',
    'green': '#22c55e',
    'yellow': '#eab308',
    'purple': '#a855f7',
    'orange': '#f97316'
}

def generate_trial():
    """Generate a new Stroop trial with mismatched word and color"""
    word = random.choice(COLORS)
    available_colors = [c for c in COLORS if c != word]
    color = random.choice(available_colors)
    return word, color

def transcribe_audio(audio_bytes):
    try:
        temp_dir = Path("audio")
        temp_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        trial_num = st.session_state.current_trial
        audio_path = temp_dir / f"trial_{trial_num}_{timestamp}.wav"
        
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
        
        with open(audio_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en",
                prompt="red, blue, green, yellow, purple, orange"
            )
        
        st.session_state.audio_files.append({
            'path': str(audio_path),
            'trial': trial_num,
            'timestamp': timestamp,
            'transcript': transcript.text
        })
        
        return transcript.text.lower().strip()
    
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

def parse_color_from_transcript(transcript):
    """Extract color from transcript"""
    if not transcript:
        return None
    
    for color in COLORS:
        if color in transcript:
            return color
    
    return None

def handle_answer(answer, reaction_time=None, transcript=None):
    if reaction_time is None:
        reaction_time = time.time() - st.session_state.start_time
    
    correct = answer == st.session_state.current_color
    
    result = {
        'trial': st.session_state.current_trial,
        'word': st.session_state.current_word,
        'color': st.session_state.current_color,
        'answer': answer,
        'correct': correct,
        'time': reaction_time
    }
    
    if transcript:
        result['transcript'] = transcript
    
    st.session_state.results.append(result)
    
    if st.session_state.current_trial < 10:
        st.session_state.current_trial += 1
        st.session_state.current_word, st.session_state.current_color = generate_trial()
        st.session_state.start_time = time.time()
    else:
        st.session_state.started = False

def show_results():
    """Display test results"""
    st.markdown("<div class='centered-container'>", unsafe_allow_html=True)
    
    correct_count = sum(1 for r in st.session_state.results if r['correct'])
    avg_time = sum(r['time'] for r in st.session_state.results) / len(st.session_state.results)
    
    st.success(f"You got {correct_count} out of 10 correct!")
    st.info(f"Average reaction time: {avg_time:.2f}s")
    st.balloons()
    
    with st.expander("View Detailed Results"):
        for result in st.session_state.results:
            emoji = "✅" if result['correct'] else "❌"
            transcript_info = f" - Heard: '{result.get('transcript', 'N/A')}'" if 'transcript' in result else ""
            st.write(f"{emoji} Trial {result['trial']}: Word '{result['word']}' in **{result['color']}** - "
                    f"You answered: **{result['answer']}** ({result['time']:.2f}s){transcript_info}")
    
    if st.session_state.results:
        results_text = "Trial,Word,Color,Answer,Correct,Time(s),Transcript\n"
        for r in st.session_state.results:
            results_text += f"{r['trial']},{r['word']},{r['color']},{r['answer']},{r['correct']},{r['time']:.2f},{r.get('transcript', 'N/A')}\n"
        
        st.download_button(
            label="📊 Download Results CSV",
            data=results_text,
            file_name=f"stroop_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


# Main app logic
if not st.session_state.started and len(st.session_state.results) == 0:
    # WELCOME PAGE
    st.markdown("<div class='welcome-container'>", unsafe_allow_html=True)
    
    st.markdown("### <span style='color: black;'>DS3 Fall Projects</span>", unsafe_allow_html=True)
    st.markdown("<span style='color: black;'>Jaden Lee • Kylan Huynh • Yash Date • Max Ha</span>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='color: black; font-size: 72px;'>sayStroop</h1>", unsafe_allow_html=True)
    
    st.markdown("### :red[Welcome! Ready to Test Your Brain?]")
    st.markdown("""
    <div style='color: black; font-size: 18px; line-height: 1.8;'>
    Our project this quarter explored the <strong>Stroop Effect</strong>, a fascinating study on 
    attention and reaction time. This website lets you take the Stroop test using voice recognition 
    and helps us discover whether the effect really works!
    <br><br>
    <strong>How it works:</strong>
    <ul>
        <li>You'll see color words displayed in different colors</li>
        <li>Say the COLOR of the text out loud (not the word itself!)</li>
        <li>For example, if you see <span style='color: #ef4444;'>BLUE</span>, say "red"</li>
        <li>Complete 10 trials as quickly and accurately as possible</li>
        
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("START TEST", type="primary", use_container_width=True):
            st.session_state.started = True
            st.session_state.current_trial = 1
            st.session_state.results = []
            st.session_state.audio_files = []
            st.session_state.current_word, st.session_state.current_color = generate_trial()
            st.session_state.start_time = time.time()
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.started:
    st.markdown("<div class='test-container'>", unsafe_allow_html=True)
    
    # Display Stroop word
    word_color = COLOR_MAP[st.session_state.current_color]
    st.markdown(f"""
    <div class='stroop-word' style='color: {word_color};'>
        {st.session_state.current_word}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666;'>Say the color you see</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    audio_bytes = st.audio_input("Record your answer", label_visibility="collapsed")
    
    if audio_bytes:
        st.markdown("<div class='recording-indicator'>🎤 Processing your answer...</div>", 
                   unsafe_allow_html=True)
        
        audio_data = audio_bytes.read()
        transcript = transcribe_audio(audio_data)
        
        if transcript:
            st.info(f"You said: '{transcript}'")
            color_answer = parse_color_from_transcript(transcript)
            
            if color_answer:
                reaction_time = time.time() - st.session_state.start_time
                handle_answer(color_answer, reaction_time, transcript)
                time.sleep(0.5)
                st.rerun()
            else:
                st.warning("❌ No color detected. Try again - say: red, blue, green, yellow, purple, or orange")
    
    st.markdown("</div>", unsafe_allow_html=True)

else:
    show_results()

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666; padding: 20px;'>sayStroop Test © 2025</div>", 
           unsafe_allow_html=True)