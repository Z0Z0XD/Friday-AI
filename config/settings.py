import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FIREWORKS_API_KEY")

API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"

MODEL_NAME = "accounts/fireworks/models/deepseek-v3p1"