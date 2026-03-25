import json
import re
from agent.planner import ask_ai
from agent.executor import execute_task
from agent.memory import add_history_entry
from tools.browser import get_driver, get_video_state
# ── Browser tools that need Chrome to be open ──
BROWSER_TOOLS = {
    "search_google",
    "search_youtube",
    "open_website",
    "open_new_tab",
    "play_youtube",
    "close_tab",
    "pause_video",
    "resume_video",
    "seek_video",
    "adjust_video",
    "pause_all_tabs",
}
# ── Tasks where user clearly wants Chrome (auto-open, no permission) ──
EXPLICIT_INTENT_TASKS = {
    "play_youtube",
    "search_youtube",
    "search_google",
    "open_website",
    "open_new_tab",
}
# ── Search-type tasks that should not repeat ──
SEARCH_TASKS = {
    "search_google",
    "search_youtube",
    "web_search",
    "play_youtube",
}
MAX_STEPS = 20
# ── Session history (persists across calls within one terminal session) ──
_session_history: list[dict] = []
def _add_to_session(role: str, content: str):
    """Add a message to session history, trimmed to last 20."""
    _session_history.append({"role": role, "content": content})
    while len(_session_history) > 20:
        _session_history.pop(0)
def _browser_state() -> str:
    """Return a string describing the current browser and video state."""
    if not get_driver():
        return "Chrome browser is CLOSED."
    state = "Chrome browser is OPEN."
    video = get_video_state()
    if video and video != "No browser open.":
        state += f" {video}"
    return state
def _extract_json(text: str) -> dict | None:
    """Extract the first JSON object from a string. Handles one level of nesting."""
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    match = re.search(r"\{(?:[^{}]|\{[^{}]*\})*\}", cleaned, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None
def _clean_response(text: str) -> str:
    """Remove JSON from a response, return only the plain text part."""
    cleaned = re.sub(r"\{(?:[^{}]|\{[^{}]*\})*\}", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"```(?:json)?", "", cleaned)
    cleaned = cleaned.strip()
    return cleaned if cleaned else "Done."
def run_agent(user_input: str) -> str:
    """Main agent loop. Routes input through the LLM and executes tools."""
    # Add user message to session history
    _add_to_session("user", user_input)
    # Build messages: session history + current browser state
    messages = list(_session_history)
    messages.append({
        "role": "user",
        "content": f"[Current state: {_browser_state()}]",
    })
    last_task: dict | None = None
    last_task_type: str | None = None
    task_type_log: str | None = None
    failed_action_count = 0
    for step in range(MAX_STEPS):
        raw_response = ask_ai(messages)
        messages.append({"role": "assistant", "content": raw_response})
        task = _extract_json(raw_response)
        # ── No JSON = conversation or task complete ──
        if task is None:
            final = raw_response
            _add_to_session("assistant", final)
            add_history_entry(user_input, final, task_type_log)
            return final
        # ── Duplicate exact task guard ──
        if task == last_task:
            final = _clean_response(raw_response)
            _add_to_session("assistant", final)
            add_history_entry(user_input, final, task_type_log)
            return final
        task_type = task.get("task", "")
        task_type_log = task_type
        # ── Same task TYPE repeated (e.g. search_google → search_google) ──
        if task_type in SEARCH_TASKS and task_type == last_task_type:
            final = _clean_response(raw_response)
            _add_to_session("assistant", final)
            add_history_entry(user_input, final, task_type_log)
            return final
        last_task = task
        last_task_type = task_type
        # ── Chrome permission gate ──
        if task_type in BROWSER_TOOLS and not get_driver():
            if task_type in EXPLICIT_INTENT_TASKS:
                # User clearly wants Chrome — auto-open
                open_result = execute_task({"task": "open_chrome"})
                if "error" in open_result.lower() or "failed" in open_result.lower():
                    final = f"Could not open Chrome — {open_result}"
                    _add_to_session("assistant", final)
                    add_history_entry(user_input, final, task_type_log)
                    return final
                obs = f"Observation: {open_result}\nCurrent state: {_browser_state()}"
                messages.append({"role": "user", "content": obs})
                last_task = None
                last_task_type = None
                continue
            else:
                # LLM decided to use Chrome but user didn't explicitly ask
                confirm = input(
                    "\nFriday: I need to open Chrome to do that. Allow it? (yes/no): "
                ).strip().lower()
                if confirm not in ("yes", "y"):
                    final = "Understood. I won't open Chrome."
                    _add_to_session("assistant", final)
                    add_history_entry(user_input, final, task_type_log)
                    return final
                open_result = execute_task({"task": "open_chrome"})
                if "error" in open_result.lower() or "failed" in open_result.lower():
                    final = f"Could not open Chrome — {open_result}"
                    _add_to_session("assistant", final)
                    add_history_entry(user_input, final, task_type_log)
                    return final
                obs = f"Observation: {open_result}\nCurrent state: {_browser_state()}"
                messages.append({"role": "user", "content": obs})
                last_task = None
                last_task_type = None
                continue
        # ── Execute the task ──
        result = execute_task(task)
        # ── Failed action guard ──
        is_failure = any(
            marker in result.lower()
            for marker in ["error:", "no video is loaded", "could not", "failed"]
        )
        if is_failure:
            failed_action_count += 1
            if failed_action_count >= 2:
                final = _clean_response(raw_response)
                if not final or final == "Done.":
                    final = f"Something went wrong: {result}"
                _add_to_session("assistant", final)
                add_history_entry(user_input, final, task_type_log)
                return final
        else:
            failed_action_count = 0
        obs = f"Observation: {result}\nCurrent state: {_browser_state()}"
        messages.append({"role": "user", "content": obs})
    # ── Step limit reached ──
    final = "I couldn't complete the task within the step limit."
    _add_to_session("assistant", final)
    add_history_entry(user_input, final, task_type_log)
    return final
