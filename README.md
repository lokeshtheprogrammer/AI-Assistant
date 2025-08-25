# AI Assistant – Prompt Engineering Major Project

This project showcases prompt design and an AI Assistant that supports three functions:
1. **Answer Questions**
2. **Summarize Text**
3. **Generate Creative Content**

Two interfaces are provided:
- **CLI** (`python main.py`)
- **Web App** (`streamlit run app.py`)

## Quick Start

1. **Python 3.10+ recommended**
2. Create a virtual environment and install deps:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Set your OpenAI API key** (or equivalent) in `.env`:
   ```
   OPENAI_API_KEY=sk-...
   MODEL=gpt-4o-mini
   ```
4. **Run the CLI:**
   ```bash
   python main.py
   ```
5. **Run the Web App:**
   ```bash
   streamlit run app.py
   ```

> If you don't have an API key, you can toggle **Demo Mode** in both the CLI and Web App to see how prompts are constructed. Demo mode fabricates safe sample responses so you can test the UX and feedback loop.

## Project Highlights

- **Prompt catalog** (`prompts.json`) with three alternative prompts per function, varying tone, structure, and specificity.
- **Feedback loop**: After each response, the user can mark helpful (yes/no) and add comments. The app stores feedback in `feedback.jsonl` and lightly adapts future prompts (adds constraints, changes style) based on aggregated feedback.
- **Separation of concerns**: Prompt templates are external; the code composes them with variables and function-specific guardrails.
- **Reproducibility**: All inputs/outputs are logged to `session_logs/` with timestamps.

## Files
- `main.py` – CLI entry point.
- `app.py` – Streamlit UI.
- `prompts.json` – Prompt templates.
- `feedback.jsonl` – Appends after each run (created automatically).
- `session_logs/` – JSON dumps per interaction.
- `requirements.txt` – Python deps.
- `AI_Assistant_User_Guide.pptx` – Brief user guide (also included below).

## Example Prompts

**Answer Questions**
- "What is the capital of France?"
- "Can you explain the significance of the Eiffel Tower?"
- "Tell me three facts about Paris."

**Summarize Text**
- "Summarize the following article: [paste text]"
- "What are the main points of this text: [paste text]?"
- "Provide a brief overview of this document: [paste text]."

**Generate Creative Content**
- "Write a short story about a dragon and a princess."
- "Create a poem about autumn."
- "Generate an idea for a science fiction novel."

## License
MIT