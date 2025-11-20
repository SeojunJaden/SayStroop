import streamlit as st
import random
import time
from datetime import datetime
import openai
from openai import OpenAI
import os
from pathlib import Path
from dotenv import load_dotenv
import io
import wave
import array
import uuid
from supabase import create_client

# Page config
st.set_page_config(
    page_title="sayStroop - Stroop Effect Test",
    page_icon="🧠",
    layout="wide"
)

# OpenAI Client and Suoabase setup
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Custom CSS by v0
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
    .countdown-timer {
        font-size: 72px;
        color: #ef4444;
        text-align: center;
        font-weight: bold;
        padding: 40px;
    }
    .FinishedText {
        font-size: 40px;
        color: #ef4444;
        text-align: center;
        font-weight: bold;
        padding: 40px;
    }
    .FinishedText2 {
        font-size: 30px;
        color: #000000;
        text-align: center;
        font-weight: bold;
        padding: 40px;
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
    .finish-container {
        max-width: 600px;
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
    .audio-input-bottom {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    [data-testid="stMetric"] {
        text-align: center;
    }
    [data-testid="stMetricLabel"] {
        font-size: 40px !important;
        font-weight: bold;
        color: #ef4444;
    }
    [data-testid="stMetricValue"] {
        font-size: 36px !important;
        color: #ef4444;
    }

</style>
""", unsafe_allow_html=True)

# Session state
if 'started' not in st.session_state:
    st.session_state.started = False
if 'countdown_complete' not in st.session_state:
    st.session_state.countdown_complete = False
if 'countdown_start_time' not in st.session_state:
    st.session_state.countdown_start_time = None
if 'recording_started' not in st.session_state:
    st.session_state.recording_started = False
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
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'await_finish' not in st.session_state:
    st.session_state.await_finish = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# COLORS AND TRIAL SETTINGS
COUNTDOWN_TIME = 5
TRIAL_TIME_LIMIT = 2 
NUM_TRIALS = 20
COLORS = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
COLOR_MAP = {
    'red': '#ef4444',
    'blue': '#3b82f6',
    'green': '#22c55e',
    'yellow': '#eab308',
    'purple': '#a855f7',
    'orange': '#f97316'
}

def delete_audio_files():
    audio_dir = Path("audio")
    if audio_dir.exists():
        for audio_file in audio_dir.glob("*.wav"):
            try:
                audio_file.unlink()
            except Exception as e:
                print(f"Error deleting {audio_file}: {e}")

def generate_trials():
    trials = []
    for _ in range(NUM_TRIALS):
        word = random.choice(COLORS)
        available_colors = [c for c in COLORS if c != word]
        color = random.choice(available_colors)
        trials.append({'word': word, 'color': color})
    return trials

def segment_audio_wave(audio_bytes, test_start_offset_sec, segment_duration_sec=2, num_segments=20):
    try:
        with wave.open(io.BytesIO(audio_bytes), 'rb') as wav_file:
            n_channels = wav_file.getnchannels()
            sampwidth = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            
            start_frame = int(test_start_offset_sec * framerate)
            start_byte = start_frame * n_channels * sampwidth
            
            all_frames = wav_file.readframes(wav_file.getnframes())
            test_frames = all_frames[start_byte:] 
            
            frames_per_segment = int(framerate * segment_duration_sec)
            segments = []
            
            for i in range(num_segments):
                segment_start = i * frames_per_segment * n_channels * sampwidth
                segment_end = segment_start + frames_per_segment * n_channels * sampwidth
                segment_frames = test_frames[segment_start:segment_end]
                
                segment_buffer = io.BytesIO()
                with wave.open(segment_buffer, 'wb') as segment_wav:
                    segment_wav.setnchannels(n_channels)
                    segment_wav.setsampwidth(sampwidth)
                    segment_wav.setframerate(framerate)
                    segment_wav.writeframes(segment_frames)
                segment_buffer.seek(0)
                segments.append(segment_buffer.getvalue())
            
            return segments
    except Exception as e:
        st.error(f"Error segmenting audio: {str(e)}")
        return None

def transcribe_segment(segment_bytes, segment_index):
    try:
        temp_dir = Path("audio")
        temp_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = temp_dir / f"segment_{segment_index}_{timestamp}.wav"
        with open(audio_path, "wb") as f:
            f.write(segment_bytes)
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en",
                prompt="red, blue, green, yellow, purple, orange"
            )
        #audio_path.unlink()
        
        return transcript.text.lower().strip()
    
    except Exception as e:
        st.error(f"Error transcribing segment {segment_index}: {str(e)}")
        return None

def parse_color_from_transcript(transcript):
    if not transcript:
        return None
    
    for color in COLORS:
        if color in transcript:
            return color
    
    return None

def save_results_to_supabase(results,user_id, user_name):
    try:
        records = []
        for r in results:
            record = {
                'user_id': user_id,
                'name': user_name,
                'trial_number': r['trial'],
                'word_displayed': r['word'].upper(),
                'color_displayed': r['color'],
                'spoken_color': r['answer'] if r['answer'] != 'NO RESPONSE' else None,
                'transcript': r['transcript'],
                'timestamp': r.get('absolute_timestamp',0),
                'reaction_time': r['time'],
                'correct': r['correct']
            }
            records.append(record)
        response = supabase.table('stroop_results').insert(records).execute()
        return True 
    except Exception as e:
        st.error(f"Error saving results to database: {str(e)}")
        return False


def process_segmented_audio(audio_bytes, trials):
    test_start_offset = st.session_state.trial_timestamps[0] if st.session_state.trial_timestamps else 0
    
    segments = segment_audio_wave(
        audio_bytes, 
        test_start_offset_sec=test_start_offset,
        segment_duration_sec=TRIAL_TIME_LIMIT,
        num_segments=NUM_TRIALS
    )
    
    if not segments:
        return None
    
    results = []

    for i, (segment_bytes, trial) in enumerate(zip(segments, trials)):
        transcript = transcribe_segment(segment_bytes, i)
        
        if transcript:
            answer = parse_color_from_transcript(transcript)
        else:
            answer = None
        
        correct = answer == trial['color'] if answer else False
        absolute_timestamp = test_start_offset + (i * TRIAL_TIME_LIMIT)
        
        results.append({
            'trial': i + 1,
            'word': trial['word'],
            'color': trial['color'],
            'answer': answer if answer else 'NO RESPONSE',
            'correct': correct,
            'time': TRIAL_TIME_LIMIT,
            'transcript': transcript if transcript else 'N/A',
            'absolute_timestamp': absolute_timestamp
        })
    
    return results

#WELCOME PAGE
if not st.session_state.started:
    welcome = st.container()
    with welcome:
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
            <li>Click START and allow microphone access</li>
            <li>Recording will begin automatically</li>
            <li>Words will appear every 2 seconds</li>
            <li>Say the COLOR of each word (not the word itself!)</li>
            <li>Complete all 20 trials - we'll match your responses automatically</li>
            <li><strong>For the sake of the experiment please only take it once!</strong></li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='color: black; font-size: 24px; font-weight: 500; margin-bottom: 0px;'>Enter your name:</p>", unsafe_allow_html=True)
        user_name = st.text_input("", key="name_input")
        
        st.markdown("<br>", unsafe_allow_html=True)
    
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("START TEST", type="primary", use_container_width=True):
                #delete_audio_files()
                st.session_state.user_name = user_name if user_name else "Anonymous"
                st.session_state.started = True
                st.session_state.trials = generate_trials()
                st.session_state.current_trial = 0
                st.session_state.countdown_complete = False
                st.session_state.countdown_start_time = time.time()
                st.rerun()
    
        st.markdown("</div>", unsafe_allow_html=True)


#COUNTDOWN WITH RECORDING
elif st.session_state.started and not st.session_state.countdown_complete:
    elapsed = time.time() - st.session_state.countdown_start_time
    time_remaining = COUNTDOWN_TIME - elapsed
    
    st.markdown("<div class='test-container'>", unsafe_allow_html=True)
    
    if time_remaining > 0:
        st.markdown(f"<div class='progress'>Get Ready!</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='countdown-timer'>{int(time_remaining) + 1}</div>", unsafe_allow_html=True)
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; padding: 20px;'>", unsafe_allow_html=True)
        st.markdown(f"<div class='progress'><strong>Make Sure to Press Record!</strong></div>", unsafe_allow_html=True)
        audio_bytes = st.audio_input("", key="full_recording")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if audio_bytes:
            st.session_state.recording_started = True
            st.session_state.audio_data = audio_bytes.read()
        
        time.sleep(0.1)
        st.rerun()
    else:
        st.session_state.countdown_complete = True
        st.session_state.test_start_time = time.time()
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)



#RUNNING THE TEST
elif st.session_state.countdown_complete and not st.session_state.test_complete and not st.session_state.await_finish:
    elapsed = time.time() - st.session_state.test_start_time
    current_trial_index = int(elapsed // TRIAL_TIME_LIMIT)
    
    if current_trial_index >= NUM_TRIALS:
        st.session_state.await_finish = True
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
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; padding: 20px;'>", unsafe_allow_html=True)
        
        audio_bytes = st.audio_input("", key="full_recording")
       
        if audio_bytes:
            st.session_state.audio_data = audio_bytes.read()
        
        st.markdown("</div>", unsafe_allow_html=True) 
        
        time.sleep(0.1)
        st.rerun()

elif st.session_state.await_finish: 
    st.markdown("<div class='test-container'>", unsafe_allow_html=True)
    st.markdown("<div class ='FinishedText2'>Thank You, the Test is Over!</div>", unsafe_allow_html=True)
    st.markdown("<div class ='FinishedText'>Please Stop Your Recording Now<br>Press the Button Below to Finish.</div>", unsafe_allow_html=True)
    audio_bytes = st.audio_input("", key="full_recording")
    if audio_bytes:
        st.session_state.audio_data = audio_bytes.read()
    col_left, col_button, col_right = st.columns([1, 2, 1])
    with col_button:
        if st.button("FINISH TEST!", type="primary", use_container_width=True):
            st.session_state.await_finish = False
            st.session_state.test_complete = True
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

#PROCESSING RESULTS
elif st.session_state.test_complete and not st.session_state.results:
    st.markdown("Processing your responses")
    
    with st.spinner("Segmenting and transcribing audio"):
        results = process_segmented_audio(st.session_state.audio_data, st.session_state.trials)
        
        if results:
            st.session_state.results = results
            with st.spinner("Saving results to database..."):
                save_success = save_results_to_supabase(
                    results, 
                    st.session_state.user_id,
                    st.session_state.user_name
                )
                if save_success:
                    st.success("Results saved successfully!")
                else:
                    st.warning("Results processed but not saved to database")
            st.rerun()
        else:
            st.error("Make sure to Stop the Audio Recording!")
            
            if st.button("Try Again"):
                #delete_audio_files()
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

#SHOW RESULTS
else:
    welcome = st.empty()
    st.markdown("<div class='finish-container'>", unsafe_allow_html=True)
    
    
    correct_count = sum(1 for r in st.session_state.results if r['correct'])
    avg_time = sum(r['time'] for r in st.session_state.results) / len(st.session_state.results)
    
    col1, col2 = st.columns(2)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div style='text-align: center;'>
                <div style='font-size: 32px; font-weight: bold; color: #ef4444; margin-bottom: 10px;'>Correct Answers</div>
                <div style='font-size: 48px; font-weight: bold; color: #ef4444;'>{correct_count}/{NUM_TRIALS}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style='text-align: center;'>
                <div style='font-size: 32px; font-weight: bold; color: #ef4444; margin-bottom: 10px;'>Average Response Time</div>
                <div style='font-size: 48px; font-weight: bold; color: #ef4444;'>{avg_time:.2f}s</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 200px;'></div>", unsafe_allow_html=True)
    col_left, col_button, col_right = st.columns([1, 2, 1])
    with col_button:
        if st.button("Take Test Again", type="secondary", use_container_width=True):
            #delete_audio_files()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            #delete_audio_files()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.markdown("<div style='margin-top: 200px;'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #666; padding: 20px;'>sayStroop Test © 2025</div>", 
           unsafe_allow_html=True)