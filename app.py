import streamlit as st
import random
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="sayStroop - Stroop Effect Test",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS to match the design
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
        padding: 50px;
        text-transform: uppercase;
        letter-spacing: -2px;
    }
    .timer {
        font-size: 48px;
        font-weight: bold;
        text-align: right;
    }
    .progress {
        font-size: 18px;
        color: #666;
        text-align: right;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
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

def handle_answer(answer):
    """Process the user's answer"""
    reaction_time = time.time() - st.session_state.start_time
    correct = answer == st.session_state.current_color
    
    st.session_state.results.append({
        'trial': st.session_state.current_trial,
        'correct': correct,
        'time': reaction_time
    })
    
    if st.session_state.current_trial < 10:
        st.session_state.current_trial += 1
        st.session_state.current_word, st.session_state.current_color = generate_trial()
        st.session_state.start_time = time.time()
    else:
        st.session_state.started = False
        correct_count = sum(1 for r in st.session_state.results if r['correct'])
        avg_time = sum(r['time'] for r in st.session_state.results) / len(st.session_state.results)
        st.success(f"Test Complete! You got {correct_count} out of 10 correct! Average reaction time: {avg_time:.2f}s")
        st.balloons()

# Layout
col1, col2 = st.columns([1, 2])

# Left sidebar
with col1:
    st.markdown("### <span style='color: black;'> DS3 Fall Projects", unsafe_allow_html=True)
    st.markdown("<span style='color: black;'>Jaden Lee • Kylan Huynh • Yash Date • Max Ha</span>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='color: black;'>sayStroop</h1>", unsafe_allow_html=True)
    
    st.markdown("### :red[Welcome! Ready to Test Your Brain?]")
    st.markdown("""
    <div style='color: black;'>
    Our project this quarter explored the Stroop Effect, a fascinating study on 
    attention and reaction time. This website lets you take the Stroop test and 
    help us discover whether the effect really works!
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<h4 style='color: black;'>🕐 Stroop Test</h4>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: #ef4444; padding: 40px; border-radius: 10px; text-align: center;'>
        <h2 style='color: white; font-size: 32px; margin: 0;'>
            Display Random Word In Corresponding color
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    if st.button("START", type="secondary"):
        st.session_state.started = True
        st.session_state.current_trial = 1
        st.session_state.results = []
        st.session_state.current_word, st.session_state.current_color = generate_trial()
        st.session_state.start_time = time.time()
        st.rerun()

# Right test area
with col2:
    if st.session_state.started:
        #Background
        st.markdown("---")
        
        # Display Stroop word
        word_color = COLOR_MAP[st.session_state.current_color]
        st.markdown(f"""
        <div class='stroop-word' style='color: {word_color};'>
            {st.session_state.current_word}
        </div>
        <div style='text-align: center; color: black; font-size: 14px;'>
            {st.session_state.current_color}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Answer buttons
        st.markdown("<div style='text-align: center; padding: 20px;'>", unsafe_allow_html=True)
        cols = st.columns(6)
        for idx, color in enumerate(COLORS):
            with cols[idx]:
                button_html = f"""
                <style>
                    div[data-testid="stButton"] > button[key="btn_{color}"] {{
                        background-color: {COLOR_MAP[color]} !important;
                        color: white !important;
                        border: none !important;
                    }}
                </style>
                """
                st.markdown(button_html, unsafe_allow_html=True)
                if st.button(color.capitalize(), key=f"btn_{color}", use_container_width=True):
                    handle_answer(color)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        st.markdown("""
        <div style='height: 600px; display: flex; align-items: center; justify-content: center; color: black;'>
            <h2>Click START to begin the test</h2>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666; padding: 20px;'>sayStroop Test © 2025</div>", unsafe_allow_html=True)