
import streamlit as st
import json
import os
from dotenv import load_dotenv
from groq import Groq

from io import BytesIO
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

load_dotenv()
import streamlit as st
import json
import os
from dotenv import load_dotenv
from groq import Groq


st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

# Custom CSS for modern look and improved contrast
st.markdown('''
    <style>
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', 'Roboto', 'Montserrat', 'Helvetica Neue', Arial, sans-serif;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
    }
    .stApp {
        background: linear-gradient(120deg, #f8fafc 0%, #f1f5f9 100%) !important;
    }
    .st-bb, .st-cq, .st-cv, .st-cw, .st-cx, .st-cy, .st-cz, .st-da, .st-db, .st-dc, .st-dd, .st-de, .st-df, .st-dg, .st-dh, .st-di, .st-dj, .st-dk, .st-dl, .st-dm, .st-dn, .st-do, .st-dp, .st-dq, .st-dr, .st-ds, .st-dt, .st-du, .st-dv, .st-dw, .st-dx, .st-dy, .st-dz {
        background: #fff !important;
        border-radius: 18px !important;
        box-shadow: 0 4px 24px 0 rgba(80,80,180,0.08) !important;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #22d3ee 100%) !important;
        color: #fff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        padding: 0.5em 1.5em !important;
        border: none !important;
        box-shadow: 0 2px 8px 0 rgba(80,80,180,0.10) !important;
        transition: background 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #22d3ee 0%, #6366f1 100%) !important;
    }
    .stTextInput>div>input, .stTextArea textarea {
        border-radius: 8px !important;
        border: 1.5px solid #6366f1 !important;
        font-size: 1.08rem !important;
        background: #f8fafc !important;
        color: #22223b !important;
    }
    .stSelectbox>div>div>div>div {
        font-size: 1.08rem !important;
    }
    .stRadio>div>label {
        font-size: 1.08rem !important;
    }
    .stExpanderHeader {
        font-size: 1.08rem !important;
        color: #0ea5e9 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        font-family: 'Montserrat', 'Segoe UI', Arial, sans-serif !important;
        color: #0ea5e9 !important;
        letter-spacing: 0.5px;
    }
    .stCodeBlock, .stCodeBlock pre {
        background: #e0e7ff !important;
        color: #1e293b !important;
        border-radius: 8px !important;
    }
    </style>
''', unsafe_allow_html=True)

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("MODEL", "llama3-8b-8192")

# Load prompts
with open("prompts.json", "r", encoding="utf-8") as f:
    PROMPTS = json.load(f)

# Sidebar for navigation and info
with st.sidebar:
    st.title("🤖 AI Assistant")
    st.markdown("""
    **Features:**
    - Multi-function (QA, Summarize, Creative)
    - Prompt style selection
    - Advanced prompt editing
    - Voice input/output
    - Feedback logging
    """)
    st.info("Built with Streamlit, Groq API, and prompt engineering best practices.")

st.markdown("<h1 style='text-align: center; color: #4F8BF9;'>AI Assistant</h1>", unsafe_allow_html=True)

cols = st.columns([1, 2, 1])
with cols[1]:
    st.subheader("1. Select Function & Prompt Style")
    function_keys = list(PROMPTS["functions"].keys())
    function_labels = [PROMPTS["functions"][k]["name"] for k in function_keys]
    function_idx = st.selectbox("Choose a function:", range(len(function_labels)), format_func=lambda i: function_labels[i])
    function_key = function_keys[function_idx]
    function_obj = PROMPTS["functions"][function_key]

    prompt_options = function_obj["prompts"]
    prompt_labels = [p["label"] for p in prompt_options]
    prompt_idx = st.selectbox("Choose a prompt style:", range(len(prompt_labels)), format_func=lambda i: prompt_labels[i])
    selected_prompt = prompt_options[prompt_idx]

    with st.expander("Advanced: Edit the prompt template before sending"):
        custom_prompt = st.text_area("Edit prompt template:", value=selected_prompt["template"], key="custom_prompt")

    st.subheader("2. Enter Your Input")
    st.write(":microphone: Click the button below to use voice input (if supported by your browser)")
    user_input = st.text_area("Enter your input:", key="user_input_text")
    st.markdown("<button onclick=\"window.startDictation && window.startDictation('user_input_text')\">🎤 Speak</button>", unsafe_allow_html=True)

    genre = ""
    if function_key == "creative" and selected_prompt["label"].lower().startswith("idea"):
        genre = st.text_input("Enter a genre (e.g., science fiction, fantasy, mystery):")

    prompt_vars = {}
    if function_key == "qa":
        prompt_vars = {"question": user_input}
    elif function_key == "summarize":
        prompt_vars = {"content": user_input}
    elif function_key == "creative":
        if selected_prompt["label"].lower().startswith("idea"):
            prompt_vars = {"genre": genre or "any", "prompt": user_input}
        else:
            prompt_vars = {"prompt": user_input}
    else:
        prompt_vars = {"input": user_input}

    st.subheader("3. Get AI Response")
    if st.button("Get Response"):
        if not API_KEY:
            st.error("API key not found. Please set GROQ_API_KEY in your .env file.")
        elif not any(v.strip() for v in prompt_vars.values()):
            st.warning("Please enter your input.")
        else:
            prompt_text = custom_prompt
            for k, v in prompt_vars.items():
                prompt_text = prompt_text.replace(f"{{{k}}}", v)
            try:
                client = Groq(api_key=API_KEY)
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": prompt_text}]
                )
                output = response.choices[0].message.content
                st.markdown("**Response:**")
                st.write(output)
                st.markdown("**Prompt Used:**")
                st.code(prompt_text)
                # Voice output: Downloadable audio (gTTS fallback)
                if gTTS is not None:
                    if st.button("🔊 Download & Play Response Audio"):
                        tts = gTTS(text=output, lang='en')
                        mp3_fp = BytesIO()
                        tts.write_to_fp(mp3_fp)
                        mp3_fp.seek(0)
                        st.audio(mp3_fp, format='audio/mp3')
                        st.download_button("Download Audio", mp3_fp, file_name="response.mp3", mime="audio/mp3")
                else:
                    st.info("Install gTTS for audio download: pip install gTTS")
                feedback = st.radio("Was this response helpful?", ("Yes", "No"), key="feedback_radio")
                if st.button("Submit Feedback", key="feedback_button"):
                    feedback_entry = {
                        "function": function_obj["name"],
                        "prompt_label": selected_prompt["label"],
                        "prompt": prompt_text,
                        "user_input": user_input,
                        "output": output[:100],
                        "helpful": feedback,
                    }
                    with open("feedback.jsonl", "a", encoding="utf-8") as fb:
                        fb.write(json.dumps(feedback_entry) + "\n")
                    st.success("Thank you for your feedback!")
            except Exception as e:
                st.error(f"Error: {e}")
