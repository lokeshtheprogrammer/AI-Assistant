import streamlit as st
import json
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("MODEL", "llama3-8b-8192")

# Load prompts
with open("prompts.json", "r", encoding="utf-8") as f:
    PROMPTS = json.load(f)

st.title("🤖 AI Assistant")

# 1. Function selection
function_keys = list(PROMPTS["functions"].keys())
function_labels = [PROMPTS["functions"][k]["name"] for k in function_keys]
function_idx = st.selectbox("Choose a function:", range(len(function_labels)), format_func=lambda i: function_labels[i])
function_key = function_keys[function_idx]
function_obj = PROMPTS["functions"][function_key]


# 2. Prompt style selection
prompt_options = function_obj["prompts"]
prompt_labels = [p["label"] for p in prompt_options]
prompt_idx = st.selectbox("Choose a prompt style:", range(len(prompt_labels)), format_func=lambda i: prompt_labels[i])
selected_prompt = prompt_options[prompt_idx]

# 2b. Prompt customization (advanced)
with st.expander("Advanced: Edit the prompt template before sending"):
    custom_prompt = st.text_area("Edit prompt template:", value=selected_prompt["template"], key="custom_prompt")

# 3. User input (dynamic label)
st.write(":microphone: Click the button below to use voice input (if supported by your browser)")
user_input = st.text_area("Enter your input:", key="user_input_text")
st.markdown("<button onclick=\"window.startDictation && window.startDictation('user_input_text')\">🎤 Speak</button>", unsafe_allow_html=True)

# For creative/idea prompts, add genre if needed
genre = ""
if function_key == "creative" and selected_prompt["label"].lower().startswith("idea"):
    genre = st.text_input("Enter a genre (e.g., science fiction, fantasy, mystery):")

# Prepare prompt_vars for replacement
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

if st.button("Get Response"):
    if not API_KEY:
        st.error("API key not found. Please set GROQ_API_KEY in your .env file.")
    elif not any(v.strip() for v in prompt_vars.values()):
        st.warning("Please enter your input.")
    else:
        # Prepare prompt text (use custom if edited)
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
            # Text-to-speech output (browser-based)
            st.markdown("<button onclick=\"window.speechSynthesis.speak(new SpeechSynthesisUtterance('" + output.replace("'", " ").replace("\n", " ") + "'))\">🔊 Listen to Response</button>", unsafe_allow_html=True)
            # 4. Feedback
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
