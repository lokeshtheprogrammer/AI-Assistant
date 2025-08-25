import json
import os
import datetime
from typing import Dict, Any

# Load .env (optional but recommended)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# === Configs (Groq) ===
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
MODEL = os.getenv("MODEL", "llama3-8b-8192")  # e.g., llama3-8b-8192 or llama3-70b-8192
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

system_base = (
    "You are a helpful, honest, concise AI assistant. "
    "Always answer clearly and structure long answers with brief bullets when helpful."
)

# === Helpers ===
def load_prompts(path="prompts.json") -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompts file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_log(payload: Dict[str, Any]):
    os.makedirs("session_logs", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    with open(f"session_logs/{ts}.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

def adapt_prompt(prompt_text: str, helpful: bool, comment: str) -> str:
    if helpful:
        return prompt_text
    additions = []
    if "length" not in prompt_text.lower():
        additions.append(" Keep the response under 150 words.")
    if "examples" not in prompt_text.lower():
        additions.append(" Provide 1 relevant example if applicable.")
    if "bullets" not in prompt_text.lower():
        additions.append(" Use up to five short bullet points if listing items.")
    if comment.strip():
        additions.append(f" Address this user note explicitly: '{comment.strip()}'.")
    return prompt_text + "".join(additions)

def call_model(messages: list) -> str:
    """Call Groq model (Chat Completions) or return demo output."""
    if DEMO_MODE:
        return "[DEMO MODE] This is a fabricated sample response based on your prompt."

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "[Error] GROQ_API_KEY is not set. Add it to your environment or .env file."

    try:
        from groq import Groq
    except Exception as e:
        return f"[Error] groq package not installed: {e}. Try: pip install groq"

    try:
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=TEMPERATURE,
        )
        return resp.choices[0].message.content
    except Exception as e:
        # Common causes: wrong model name, network issues, invalid key
        return f"[Error calling Groq: {e}]"

def choose_option(title: str, options: list) -> int:
    print(f"\n{title}")
    for i, opt in enumerate(options, start=1):
        print(f"  {i}. {opt}")
    while True:
        sel = input("Enter choice number: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(options):
            return int(sel) - 1
        print("Invalid choice. Try again.")

# === Main ===
def main():
    try:
        prompts_catalog = load_prompts()
    except FileNotFoundError:
        print("Error: prompts.json file not found. Please keep it next to main.py.")
        return

    print("=== AI Assistant (CLI) — Groq ===")
    print("Functions: 1) Answer Questions  2) Summarize Text  3) Creative Generation")

    funcs = list(prompts_catalog["functions"].keys())
    func_idx = choose_option("Pick a function:", [prompts_catalog["functions"][k]["name"] for k in funcs])
    func_key = funcs[func_idx]
    fn = prompts_catalog["functions"][func_key]

    # Pick prompt variant
    variant_idx = choose_option("Pick a prompt style:", [p["label"] for p in fn["prompts"]])
    template = fn["prompts"][variant_idx]["template"]

    # Collect input
    if func_key == "qa":
        question = input("Enter your question: ")
        filled = template.format(question=question)
        user_instruction = question
    elif func_key == "summarize":
        content = input("Paste text to summarize:\n")
        filled = template.format(content=content)
        user_instruction = content[:1200]
    else:  # creative
        if "{genre}" in template:
            genre = input("Enter a genre (e.g., science fiction, fantasy, thriller): ")
            filled = template.format(genre=genre)
            user_instruction = f"genre={genre}"
        else:
            prompt = input("Enter your creative prompt (e.g., 'a dragon and a princess'): ")
            filled = template.format(prompt=prompt)
            user_instruction = prompt

    # Compose messages
    messages = [
        {"role": "system", "content": system_base},
        {"role": "user", "content": filled},
    ]

    print("\n--- Composed Prompt ---")
    print(filled)
    print("\n--- Model Response ---")
    output = call_model(messages)
    print(output)

    # Feedback
    helpful = input("\nWas this response helpful? (yes/no): ").strip().lower().startswith("y")
    comment = input("Any feedback to improve the response? (optional): ").strip()

    adapted = adapt_prompt(filled, helpful, comment)
    if adapted != filled:
        print("\n--- Adapted Prompt for Next Time ---")
        print(adapted)

    # Persist feedback and logs
    fb = {
        "ts": datetime.datetime.now().isoformat(),
        "function": func_key,
        "prompt_label": fn["prompts"][variant_idx]["label"],
        "original_prompt": filled,
        "adapted_prompt": adapted,
        "helpful": helpful,
        "comment": comment,
        "output_preview": (output or "")[:500],
        "model": MODEL,
    }
    with open("feedback.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(fb, ensure_ascii=False) + "\n")

    save_log({"messages": messages, "output": output, "feedback": fb, "demo_mode": DEMO_MODE})

if __name__ == "__main__":
    main()
