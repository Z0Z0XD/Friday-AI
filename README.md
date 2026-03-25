# Friday – Personal AI Assistant

A locally-run personal AI assistant built in Python, 
inspired by voice/chat assistant concepts. Friday 
uses a ReAct-style agent loop to reason through 
tasks, integrates a third-party LLM API, and can 
automate browser actions — all running on your 
local machine.

---

## What it does

- Understands and responds to natural language input
- Uses a ReAct-style loop (Reasoning + Acting) to 
  plan and execute tasks step by step
- Integrates Fireworks AI API with DeepSeek V3 as 
  the language model backend
- Automates browser actions using Selenium 
  (web search, URL navigation, content extraction)
- Maintains memory across sessions using 
  profile.json and history.json
- Injects dynamic context (date, time, user info) 
  into the system prompt for better responses

---

## Tech Stack

- Python 3.x
- Fireworks AI API (DeepSeek V3)
- Selenium WebDriver
- JSON (for persistent memory)
- Git & GitHub

---

## Project Structure
```
friday-ai/
├── main.py            – Entry point, main loop
├── controller.py      – Manages conversation flow
├── planner.py         – Breaks tasks into steps
├── executor.py        – Executes planned actions
├── browser_tools.py   – Selenium browser automation
├── memory.py          – Handles profile & history
├── profile.json       – Stores user context
├── history.json       – Stores conversation history
└── requirements.txt   – Python dependencies
```

---

## How to run it

1. Clone the repository
   git clone https://github.com/YOURUSERNAME/friday-ai.git

2. Install dependencies
   pip install -r requirements.txt

3. Set your API key as an environment variable
   Windows: set FIREWORKS_API_KEY=your_key_here
   Linux/Mac: export FIREWORKS_API_KEY=your_key_here

4. Run
   python main.py

---

## Current Status

Actively in development. Core features working:
- Conversational loop with memory
- Browser automation via Selenium
- Persistent session memory via JSON files

Planned next: improved memory system, 
better error handling, voice input support.

---

## About

Built as a self-learning project to understand 
agentic AI systems, prompt engineering, and 
real-world API integration from the ground up.