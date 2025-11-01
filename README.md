# AI Moderation Demo

A Python script that demonstrates AI content moderation using OpenAI's API with input/output filtering.

## Features

- **Input Moderation**: Blocks harmful content before sending to AI
- **Output Moderation**: Filters AI responses for unsafe content
- **System Prompt**: Guides AI behavior for safe responses
- **Keyword Filtering**: Simple banned word detection and redaction

## Setup

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Run the script:
```bash
python ai_moderator.py
```

Enter your prompt when prompted. The system will:
1. Check input for banned keywords
2. Send safe prompts to OpenAI API
3. Filter AI responses for harmful content
4. Display moderated results

## Moderation Policy

- **Banned Keywords**: kill, hack, bomb
- **Input Violation**: Prompt rejected entirely
- **Output Violation**: Harmful words replaced with [REDACTED]