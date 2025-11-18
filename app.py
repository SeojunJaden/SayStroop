import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import random
import time
from datetime import datetime
import openai
from openai import OpenAI
import os
from pathlib import Path
from dotenv import load_dotenv
import av
import numpy as np
import io

# Page config
st.set_page_config(
    page_title="sayStroop - Stroop Effect Test",
    page_icon="🧠",
    layout="wide"
)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Custom CSS
st.markdown("""
<style>
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
    .countdown {
        font-size: 48px;
        color: #ef4444;
        text-align: center;
        font-weight: bold;
        padding: 20px;
    }
    .welcome-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 10px 40px;
        background-color: white;
    }
    .test-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        padding-top: 20px;
        width: 100%;
        background-color: white;
    }
    .recording-status {
        text-align: center;
        color: #ef4444;
        font-size: 20px;
        padding: 10px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'started' not in st.session_state:
    st.session_state.started = False
if 'test_running' not in st.session_state:
    st.session_state.test_running = False
if 'test_complete' not in st.session_state:
    st.session_state.test_complete = False
if 'current_trial' not in st.session_state:
    st.session_state.current_trial = 0
if 'trials' not in st.session_state:
    st.session_state.trials = []
if 'trial_timestamps' not in st.session_state:
    st.session_state.trial_timestamps = []
if 'results' not in st.session_state:
    st.session_state.results = []
if 'test_start_time' not in st.session_state:
    st.session_state.test_start_time = None
if 'audio_frames' not in st.session_state:
    st.session_state.audio_frames = []
if 'recording_active' not in st.session_state:
    st.session_state.recording_active = False

# Colors and time limit
TRIAL_TIME_LIMIT = 1
NUM_TRIALS = 10
COLORS = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
COLOR_MAP = {
    'red': '#ef4444',
    'blue': '#3b82f6',
    'green': '#22c55e',
    'yellow': '#eab308',
    'purple': '#a855f7',
    'orange': '#f97316'
}

def generate_trials():
    trials = []
    for _ in range(NUM_TRIALS):
        word = random.choice(COLORS)
        available_colors = [c for c in COLORS if c != word]
        color = random.choice(available_colors)
        trials.append({'word': word, 'color': color})
    return trials

def audio_frame_callback(frame):
    if st.session_state.recording_active:
        sound = frame.to_ndarray()
        st.session_state.audio_frames.append(sound)
    return frame

def save_audio_to_wav(audio_frames, sample_rate=48000):
    if not audio_frames:
        return None
    
    audio_data = np.concatenate(audio_frames, axis=0)
    audio_data = (audio_data * 32767).astype(np.int16)
    import wave
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    buffer.seek(0)
    return buffer.read()

def transcribe_with_timestamps(audio_bytes):
    try:
        temp_dir = Path("audio")
        temp_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = temp_dir / f"full_test_{timestamp}.wav"
        
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
        
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en",
                response_format="verbose_json",
                timestamp_granularities=["word"],
                prompt="red, blue, green, yellow, purple, orange"
            )
        
        audio_path.unlink()
        
        return transcript
    
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

def match_responses_to_trials(transcript, trial_timestamps):
    results = []    
    words = transcript.words
    
    for i, (trial, trial_start) in enumerate(zip(st.session_state.trials, trial_timestamps)):
        trial_end = trial_start + TRIAL_TIME_LIMIT
        
        trial_words = [
            w for w in words 
            if trial_start <= w['start'] < trial_end
        ]
        
        if trial_words:
            spoken_text = ' '.join([w['word'] for w in trial_words]).lower()
            answer = None
            
            for color in COLORS:
                if color in spoken_text:
                    answer = color
                    break
            
            reaction_time = trial_words[0]['start'] - trial_start if answer else None
        else:
            answer = None
            reaction_time = None
        
        correct = answer == trial['color'] if answer else False
        
        results.append({
            'trial': i + 1,
            'word': trial['word'],
            'color': trial['color'],
            'answer': answer if answer else 'NO RESPONSE',
            'correct': correct,
            'time': reaction_time if reaction_time else TRIAL_TIME_LIMIT,
            'transcript': ' '.join([w['word'] for w in trial_words]) if trial_words else 'N/A'
        })
    
    return results

# WELCOME PAGE
if not st.session_state.started:
    st.markdown("<div class='welcome-container'>", unsafe_allow_html=True)
    
    st.markdown("### <span style='color: black;'>DS3 Fall Projects</span>", unsafe_allow_html=True)
    st.markdown("<span style='color: black;'>Jaden Lee • Kylan Huynh • Yash Date • Max Ha</span>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='color: black; font-size: 72px;'>sayStroop</h1>", unsafe_allow_html=True)
    
    st.markdown("### :red[Welcome! Ready to Test Your Brain?]")
    st.markdown("""
    <div style='color: black; font-size: 18px; line-height: 1.8;'>
    Our project explored the <strong>Stroop Effect</strong>. This test uses continuous voice recording!
    <br><br>
    <strong>How it works:</strong>
    <ul>
        <li>Click START to begin</li>
        <li>Click "START" on the audio recorder</li>
        <li>Words will appear every 3 seconds</li>
        <li>Say the COLOR of each word (not the word itself!)</li>
        <li>Complete all 20 trials - we'll match your responses automatically</li>
    </ul>
    <br>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("START TEST", type="primary", use_container_width=True):
            st.session_state.started = True
            st.session_state.trials = generate_trials()
            st.session_state.current_trial = 0
            st.session_state.audio_frames = []
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# RECORDING SETUP + TEST RUNNING
elif st.session_state.started and not st.session_state.test_complete:
    with st.sidebar:
        st.markdown("Click START below:")
        
        webrtc_ctx = webrtc_streamer(
            key="speech-to-text",
            mode=WebRtcMode.SENDONLY,
            audio_receiver_size=1024,
            media_stream_constraints={"audio": True, "video": False},
            audio_frame_callback=audio_frame_callback,
        )
        
        if webrtc_ctx.state.playing:
            st.session_state.recording_active = True
            if not st.session_state.test_running:
                st.session_state.test_running = True
                st.session_state.test_start_time = time.time()
        else:
            st.session_state.recording_active = False
    
    if st.session_state.test_running:
        elapsed = time.time() - st.session_state.test_start_time
        current_trial_index = int(elapsed // TRIAL_TIME_LIMIT)
        
        if current_trial_index >= NUM_TRIALS:
            st.session_state.test_complete = True
            st.session_state.test_running = False
            st.rerun()
        else:
            st.session_state.current_trial = current_trial_index
            trial = st.session_state.trials[current_trial_index]
            if len(st.session_state.trial_timestamps) <= current_trial_index:
                st.session_state.trial_timestamps.append(elapsed)
            st.markdown("<div class='test-container'>", unsafe_allow_html=True)      
            word_color = COLOR_MAP[trial['color']]
            st.markdown(f"<div class='stroop-word' style='color: {word_color};'>{trial['word']}</div>", 
                        unsafe_allow_html=True)
            

            
            time.sleep(0.1)
            st.rerun()
    else:
        st.markdown("### Click START on the audio recorder in the sidebar to begin!")


elif st.session_state.test_complete and not st.session_state.results:
    
    with st.spinner("Converting and transcribing audio..."):
        audio_bytes = save_audio_to_wav(st.session_state.audio_frames)
        
        if audio_bytes:
            transcript = transcribe_with_timestamps(audio_bytes)
            
            if transcript:
                results = match_responses_to_trials(transcript, st.session_state.trial_timestamps)
                
                if results:
                    st.session_state.results = results
                    st.rerun()
                else:
                    st.error("Could not process results. Please try again.")
        else:
            st.error("No audio was recorded. Please try again.")

else:
    st.markdown("<div class='welcome-container'>", unsafe_allow_html=True)
    correct_count = sum(1 for r in st.session_state.results if r['correct'])
    avg_time = sum(r['time'] for r in st.session_state.results) / len(st.session_state.results)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Correct Answers", f"{correct_count}/10")
    with col2:
        st.metric("Average Response Time", f"{avg_time:.2f}s")
    
    if st.button("Take Test Again"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666; padding: 20px;'>sayStroop Test © 2025</div>", 
           unsafe_allow_html=True)