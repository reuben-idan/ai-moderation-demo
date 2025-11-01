#!/usr/bin/env python3
"""
ai_moderator.py

Small CLI script that:
- accepts a user prompt (stdin / input)
- does simple input moderation using banned keywords
- sends the prompt + a system prompt to OpenAI Chat Completions API
- does simple output moderation (redact banned keywords)
- prints moderated output or a violation message

Requirements:
- Python 3.8+
- pip install requests python-dotenv (optional)
- Set environment variable OPENAI_API_KEY before running
"""

import os
import sys
import requests
import json
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -------- CONFIGURATION --------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("ERROR: Please set OPENAI_API_KEY as an environment variable.")
    print("E.g., export OPENAI_API_KEY='sk-...' (Unix) or setx OPENAI_API_KEY \"sk-...\" (Windows)")
    sys.exit(1)

# Choose model (stable common choice)
MODEL = "gpt-3.5-turbo"  # change if you have access to other models

# Simple banned keywords list (case-insensitive)
BANNED_KEYWORDS = ["kill", "hack", "bomb"]

# System prompt: defines assistant behavior
SYSTEM_PROMPT = (
    "You are a helpful, professional assistant. Keep responses safe and do not provide instructions "
    "for illegal activities or harm. If a user asks for disallowed or unsafe content, politely refuse."
)

# OpenAI endpoints
CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
MODERATIONS_URL = "https://api.openai.com/v1/moderations"  # optional use


# -------- Helpers --------
def contains_banned_keyword(text: str) -> bool:
    pattern = r"\\b(" + "|".join(re.escape(k) for k in BANNED_KEYWORDS) + r")\\b"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def redact_banned_keywords(text: str) -> str:
    def _replace(match):
        return "[REDACTED]"
    pattern = r"\\b(" + "|".join(re.escape(k) for k in BANNED_KEYWORDS) + r")\\b"
    return re.sub(pattern, _replace, text, flags=re.IGNORECASE)


# Optional: show how to call OpenAI Moderation API (not required by task; shown as example)
def call_moderation_api(text: str):
    """
    Demonstration of how to call OpenAI's moderation endpoint.
    This function is optional — the task asks for a simple keyword check.
    """
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"input": text}
    resp = requests.post(MODERATIONS_URL, headers=headers, json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()


def call_chat_completion(system_prompt: str, user_prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 500,
        "temperature": 0.7,
    }
    resp = requests.post(CHAT_COMPLETIONS_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


# -------- Main CLI flow --------
def main():
    print("AI Moderator CLI")
    print("Enter your prompt. Press Enter when done.")
    try:
        user_prompt = input("> ").strip()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return

    if not user_prompt:
        print("No prompt provided. Exiting.")
        return

    # 1) Simple input moderation (reject before sending to API)
    if contains_banned_keyword(user_prompt):
        print("Your input violated the moderation policy (banned keywords detected).")
        return

    # Optional: you could also call the moderation endpoint for a richer check:
    # moderation_result = call_moderation_api(user_prompt)
    # print("Moderation API result (optional):", moderation_result)

    # 2) Call OpenAI Chat Completions
    try:
        api_response = call_chat_completion(SYSTEM_PROMPT, user_prompt)
    except requests.HTTPError as e:
        print("API request failed:", e)
        # optionally show error body:
        try:
            print(e.response.json())
        except Exception:
            pass
        return
    except Exception as e:
        print("Error while calling API:", e)
        return

    # Parse assistant text (this follows OpenAI Chat Completions response schema)
    try:
        assistant_text = api_response["choices"][0]["message"]["content"]
    except Exception:
        print("Unexpected API response format:")
        print(json.dumps(api_response, indent=2))
        return

    # 3) Output moderation: redact banned keywords in the assistant response
    if contains_banned_keyword(assistant_text):
        redacted = redact_banned_keywords(assistant_text)
        # Depending on policy, you might want to block entirely rather than redact:
        print("AI response contained disallowed content and has been redacted:")
        print(redacted)
    else:
        # Safe: print result
        print("AI response:")
        print(assistant_text)


if __name__ == "__main__":
    main()

