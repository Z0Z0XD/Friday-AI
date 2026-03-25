import json
import os
from datetime import datetime
# ── File paths ──
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "..", "memory")
PROFILE_PATH = os.path.join(MEMORY_DIR, "profile.json")
HISTORY_PATH = os.path.join(MEMORY_DIR, "history.json")
# Maximum history entries to keep
MAX_HISTORY = 50
def _ensure_memory_dir():
    """Creates the memory/ directory if it doesn't exist."""
    if not os.path.exists(MEMORY_DIR):
        os.makedirs(MEMORY_DIR)
# ── Profile functions ──
def load_profile() -> dict:
    """Loads profile.json. Returns empty dict if file doesn't exist."""
    if not os.path.exists(PROFILE_PATH):
        return {}
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}
def save_profile(profile: dict):
    """Saves profile dict to profile.json."""
    _ensure_memory_dir()
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
def update_profile_field(field: str, value) -> str:
    """
    Updates a single field in the user profile.
    Supported fields:
      - name: string
      - preferences: dict (merges with existing)
      - facts: list of strings (appends, no duplicates)
    Returns a confirmation string.
    """
    profile = load_profile()
    if field == "name":
        profile["name"] = str(value)
        save_profile(profile)
        return f"Saved — I'll remember your name is {value}."
    elif field == "preferences":
        existing = profile.get("preferences", {})
        if isinstance(value, dict):
            existing.update(value)
        else:
            existing["general"] = str(value)
        profile["preferences"] = existing
        save_profile(profile)
        return f"Saved preference — {value}."
    elif field == "facts":
        existing = profile.get("facts", [])
        fact_str = str(value)
        if fact_str not in existing:
            existing.append(fact_str)
        profile["facts"] = existing
        save_profile(profile)
        return f"Noted — {fact_str}."
    else:
        return f"Unknown memory field: {field}"
# ── History functions ──
def load_history() -> list:
    """Loads history.json. Returns empty list if file doesn't exist."""
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []
def save_history(history: list):
    """Saves history list to history.json."""
    _ensure_memory_dir()
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
def add_history_entry(
    user_input: str,
    friday_response: str,
    task_type: str | None = None
):
    """
    Logs one interaction to history.json.
    Keeps only the last MAX_HISTORY entries.
    """
    history = load_history()
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user_input,
        "friday": friday_response[:200]
    }
    if task_type:
        entry["task"] = task_type
    history.append(entry)
    # Trim to max
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
    save_history(history)
# ── Memory context builder ──
def get_memory_context() -> str:
    """
    Builds a text summary of everything Friday knows.
    This gets injected into the system prompt every LLM call.
    """
    profile = load_profile()
    history = load_history()
    lines = []
    # Name
    name = profile.get("name")
    if name:
        lines.append(f"User's name: {name}")
    # Preferences
    prefs = profile.get("preferences", {})
    if prefs:
        pref_parts = []
        for key, val in prefs.items():
            pref_parts.append(f"{key}: {val}")
        lines.append("Preferences: " + ", ".join(pref_parts))
    # Facts
    facts = profile.get("facts", [])
    if facts:
        lines.append("Known facts: " + "; ".join(facts))
    # Recent history (last 5)
    if history:
        recent = history[-5:]
        lines.append("Recent interactions:")
        for entry in recent:
            timestamp = entry.get("timestamp", "")
            user = entry.get("user", "")
            task = entry.get("task", "conversation")
            lines.append(f"  [{timestamp}] User: {user} → Task: {task}")
    if not lines:
        return "No memory stored yet."
    return "\n".join(lines)
