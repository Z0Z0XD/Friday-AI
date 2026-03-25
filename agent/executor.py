from tools.browser import (
    open_chrome,
    open_new_tab,
    open_website,
    search_google,
    search_youtube,
    play_youtube,
    close_tab,
    switch_tab,
    get_all_tabs,
    pause_video,
    resume_video,
    seek_video,
    adjust_video,
    pause_all_tabs,
)
from tools.research import web_search, read_page
from agent.memory import update_profile_field
def execute_task(task: dict) -> str:
    task_type = task.get("task")
    # ─── BROWSER: Open Chrome ───
    if task_type == "open_chrome":
        print("Friday: Opening Chrome...")
        result = open_chrome()
        if result:
            return "Chrome opened successfully."
        return "Error: Failed to open Chrome."
    # ─── BROWSER: Open Website ───
    elif task_type == "open_website":
        url = task.get("url", "").strip()
        if not url:
            return "Error: open_website requires a url parameter."
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        print(f"Friday: Opening {url}...")
        return open_website(url)
    # ─── BROWSER: Search Google ───
    elif task_type == "search_google":
        query = task.get("query", "").strip()
        if not query:
            return "Error: search_google requires a query parameter."
        print(f"Friday: Searching Google for '{query}'...")
        return search_google(query)
    # ─── BROWSER: Search YouTube ───
    elif task_type == "search_youtube":
        query = task.get("query", "").strip()
        if not query:
            return "Error: search_youtube requires a query parameter."
        print(f"Friday: Searching YouTube for '{query}'...")
        return search_youtube(query)
    # ─── BROWSER: Play YouTube ───
    elif task_type == "play_youtube":
        query = task.get("query", "").strip()
        if not query:
            return "Error: play_youtube requires a query parameter."
        print(f"Friday: Playing '{query}' on YouTube...")
        return play_youtube(query)
    # ─── BROWSER: Open New Tab ───
    elif task_type == "open_new_tab":
        url = task.get("url", "").strip()
        if url and not url.startswith(("http://", "https://")):
            url = "https://" + url
        target = url or "about:blank"
        print(f"Friday: Opening new tab → {target}...")
        return open_new_tab(target)
    # ─── BROWSER: Close Tab ───
    elif task_type == "close_tab":
        print("Friday: Closing tab...")
        return close_tab()
    # ─── BROWSER: Switch Tab ───
    elif task_type == "switch_tab":
        target = task.get("target", "").strip()
        if not target:
            return "Error: switch_tab requires a target (tab number or keyword)."
        print(f"Friday: Switching to tab '{target}'...")
        return switch_tab(target)
    # ─── BROWSER: Get All Tabs ───
    elif task_type == "get_tabs":
        print("Friday: Checking open tabs...")
        return get_all_tabs()
    # ─── VIDEO: Pause ───
    elif task_type == "pause_video":
        print("Friday: Pausing video...")
        return pause_video()
    # ─── VIDEO: Resume ───
    elif task_type == "resume_video":
        print("Friday: Resuming video...")
        return resume_video()
    # ─── VIDEO: Seek to position ───
    elif task_type == "seek_video":
        time_str = str(task.get("time", task.get("seconds", "0"))).strip()
        # Parse timestamp formats: "2:30", "1:45:00", or raw seconds
        parts = time_str.split(":")
        try:
            if len(parts) == 3:
                total = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2:
                total = int(parts[0]) * 60 + int(parts[1])
            else:
                total = float(parts[0])
        except ValueError:
            return f"Error: Could not parse time '{time_str}'."
        print(f"Friday: Seeking to {time_str}...")
        return seek_video(total)
    # ─── VIDEO: Adjust (rewind/forward) ───
    elif task_type == "adjust_video":
        try:
            seconds = float(task.get("seconds", 0))
        except (ValueError, TypeError):
            return "Error: adjust_video requires a numeric 'seconds' value."
        if seconds == 0:
            return "Error: adjust_video requires a non-zero 'seconds' value."
        direction = "Fast-forwarding" if seconds > 0 else "Rewinding"
        print(f"Friday: {direction} {abs(seconds)} seconds...")
        return adjust_video(seconds)
    # ─── VIDEO: Pause All Tabs ───
    elif task_type == "pause_all_tabs":
        print("Friday: Pausing all tabs...")
        return pause_all_tabs()
    # ─── RESEARCH: Web Search ───
    elif task_type == "web_search":
        query = task.get("query", "").strip()
        if not query:
            return "Error: web_search requires a query parameter."
        print(f"Friday: Researching '{query}'...")
        return web_search(query)
    # ─── RESEARCH: Read Page ───
    elif task_type == "read_page":
        url = task.get("url", "").strip()
        if not url:
            return "Error: read_page requires a url parameter."
        print(f"Friday: Reading {url}...")
        return read_page(url)
    # ─── MEMORY: Update Memory ───
    elif task_type == "update_memory":
        field = task.get("field", "").strip()
        value = task.get("value", "")
        if not field:
            return "Error: update_memory requires a 'field' parameter."
        if not value:
            return "Error: update_memory requires a 'value' parameter."
        return update_profile_field(field, value)
    # ─── UNKNOWN TASK ───
    else:
        return f"Error: Unknown task type '{task_type}'."
