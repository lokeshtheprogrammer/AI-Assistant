import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Get API key from .env
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ GROQ_API_KEY not found. Please add it to your .env file.")
    st.stop()

# ✅ Initialize Groq client
client = Groq(api_key=api_key)

st.title("🤖 AI Assistant")

# User input
question = st.text_input("Ask me anything:")

if st.button("Get Answer"):
    if question.strip():
        # Prepare prompt
        prompt = f"Answer the user's question directly and briefly.\nQuestion: {question}\nAnswer:"

        try:
            # Call Groq API
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
            )

            # ✅ FIXED: access .content instead of dict-style
            answer = response.choices[0].message.content
            st.success(answer)

        except Exception as e:
            st.error(f"⚠️ Error: {e}")
