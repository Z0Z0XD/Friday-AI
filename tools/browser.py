import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
driver = None
# ─── AD BLOCKER SCRIPT ───
AD_BLOCKER_SCRIPT = """
if (!window._fridayAdBlockerActive) {
    window._fridayAdBlockerActive = true;
    setInterval(() => {
        try {
            // Click skip ad buttons
            const skipSelectors = [
                '.ytp-skip-ad-button',
                '.ytp-ad-skip-button',
                '.ytp-ad-skip-button-modern',
                'button.ytp-ad-skip-button',
                '.videoAdUiSkipButton',
                '[id^="skip-button"]'
            ];
            for (const sel of skipSelectors) {
                const btn = document.querySelector(sel);
                if (btn) { btn.click(); }
            }
            // Close overlay ads
            const overlay = document.querySelector('.ytp-ad-overlay-close-button');
            if (overlay) { overlay.click(); }
            // Fast-forward video ads
            const adShowing = document.querySelector('.ad-showing');
            if (adShowing) {
                const v = document.querySelector('video');
                if (v && v.duration && !isNaN(v.duration)) {
                    v.currentTime = v.duration;
                }
            }
        } catch(e) {}
    }, 500);
}
"""
def _inject_ad_blocker():
    """Inject ad blocker into current YouTube page."""
    global driver
    if driver:
        try:
            current_url = driver.current_url or ""
            if "youtube.com" in current_url:
                driver.execute_script(AD_BLOCKER_SCRIPT)
        except Exception:
            pass
def open_chrome():
    """Open Chrome browser with anti-detection flags."""
    global driver
    try:
        chrome_options = Options()
        profile_path = os.path.abspath("friday_browser_profile")
        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        # Anti-detection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        driver = webdriver.Chrome(options=chrome_options)
        # Remove webdriver flag
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
        )
        driver.get("about:blank")
        return driver
    except Exception as e:
        driver = None
        print(f"Friday: Failed to open Chrome — {e}")
        return None
def open_website(url: str):
    """Navigate current tab to a URL."""
    global driver
    if driver:
        driver.get(url)
        time.sleep(2)
        try:
            title = driver.title
            return f"Opened {url} — Page: {title}"
        except Exception:
            return f"Opened {url}"
    return "Error: Chrome is not open."
def search_google(query: str):
    """Search Google in current tab."""
    global driver
    if driver:
        from urllib.parse import quote_plus
        driver.get(f"https://www.google.com/search?q={quote_plus(query)}")
        time.sleep(2)
        try:
            title = driver.title
            return f"Google search loaded for '{query}' — Page: {title}"
        except Exception:
            return f"Google search loaded for '{query}'"
    return "Error: Chrome is not open."
def search_youtube(query: str):
    """Search YouTube in current tab (shows results, does NOT auto-play)."""
    global driver
    if driver:
        from urllib.parse import quote_plus
        url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        driver.get(url)
        time.sleep(2)
        _inject_ad_blocker()
        try:
            title = driver.title
            return f"YouTube search results loaded for '{query}' — Page: {title}"
        except Exception:
            return f"YouTube search results loaded for '{query}'"
    return "Error: Chrome is not open."
def play_youtube(query: str):
    """Search YouTube and auto-play the first video result."""
    global driver
    if driver:
        from urllib.parse import quote_plus
        url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        driver.get(url)
        time.sleep(3)
        try:
            # Find and click first video
            video = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "ytd-video-renderer a#video-title"))
            )
            video_title = video.get_attribute("title") or "Unknown"
            video.click()
            # Wait for video page to load
            for _ in range(16):
                time.sleep(0.5)
                current_url = driver.current_url or ""
                if "/watch" in current_url:
                    break
            time.sleep(2)
            _inject_ad_blocker()
            # Force play if paused
            try:
                driver.execute_script("""
                    var v = document.querySelector('video');
                    if (v && v.paused) { v.play(); }
                """)
            except Exception:
                pass
            return f"Now playing: '{video_title}' on YouTube"
        except Exception as e:
            return f"Opened YouTube search results for '{query}' but could not auto-play — {e}"
    return "Error: Chrome is not open."
def open_new_tab(url: str = "about:blank"):
    """Open a new browser tab."""
    global driver
    if driver:
        driver.execute_script(f"window.open('{url}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)
        if "youtube.com" in url:
            _inject_ad_blocker()
        tab_count = len(driver.window_handles)
        try:
            title = driver.title
            return f"New tab opened — Page: {title} — Total tabs: {tab_count}"
        except Exception:
            return f"New tab opened — Total tabs: {tab_count}"
    return "Error: Chrome is not open."
def close_tab():
    """Close the current tab. If last tab, close Chrome."""
    global driver
    if driver:
        try:
            handles = driver.window_handles
            if len(handles) <= 1:
                driver.quit()
                driver = None
                return "Closed the last tab. Chrome is now closed."
            else:
                driver.close()
                driver.switch_to.window(driver.window_handles[-1])
                try:
                    title = driver.title
                    remaining = len(driver.window_handles)
                    return f"Tab closed. Now on: {title} — Remaining tabs: {remaining}"
                except Exception:
                    return "Tab closed."
        except Exception as e:
            driver = None
            return f"Error closing tab: {e}"
    return "Error: Chrome is not open."
def switch_tab(target: str):
    """Switch to a tab by number (1-indexed) or by keyword match on title/URL."""
    global driver
    if driver:
        try:
            handles = driver.window_handles
            if not handles:
                return "Error: No tabs are open."
            # Try as a number first
            try:
                tab_num = int(target)
                if 1 <= tab_num <= len(handles):
                    driver.switch_to.window(handles[tab_num - 1])
                    time.sleep(1)
                    title = driver.title
                    return f"Switched to tab {tab_num}: {title}"
                else:
                    return f"Error: Tab {tab_num} doesn't exist. You have {len(handles)} tabs open."
            except ValueError:
                pass
            # Try as keyword match
            keyword = target.lower()
            for i, handle in enumerate(handles):
                driver.switch_to.window(handle)
                time.sleep(0.3)
                try:
                    title = driver.title.lower()
                    url = driver.current_url.lower()
                    if keyword in title or keyword in url:
                        return f"Switched to tab {i + 1}: {driver.title}"
                except Exception:
                    continue
            # No match found — go back to original tab
            driver.switch_to.window(handles[-1])
            return f"Error: No tab found matching '{target}'. Use get_tabs to see all open tabs."
        except Exception as e:
            return f"Error switching tab: {e}"
    return "Error: Chrome is not open."
def get_all_tabs():
    """Return a list of all open tabs with their titles."""
    global driver
    if driver:
        try:
            handles = driver.window_handles
            if not handles:
                return "No tabs are open."
            current_handle = driver.current_window_handle
            tabs_info = []
            for i, handle in enumerate(handles):
                driver.switch_to.window(handle)
                time.sleep(0.3)
                try:
                    title = driver.title or "Untitled"
                    url = driver.current_url or ""
                    active = " (active)" if handle == current_handle else ""
                    tabs_info.append(f"{i + 1}. {title}{active} — {url}")
                except Exception:
                    tabs_info.append(f"{i + 1}. Unknown tab")
            # Switch back to the original tab
            driver.switch_to.window(current_handle)
            return "Open tabs:\n" + "\n".join(tabs_info)
        except Exception as e:
            return f"Error listing tabs: {e}"
    return "Error: Chrome is not open."
def pause_video():
    """Pause the video on the current tab."""
    global driver
    if driver:
        try:
            result = driver.execute_script("""
                var v = document.querySelector('video');
                if (!v) return 'no_video';
                if (v.paused) return 'already_paused';
                v.pause();
                return 'paused_at_' + Math.floor(v.currentTime);
            """)
            if result == "no_video":
                return "Error: No video found on this page."
            elif result == "already_paused":
                return "Video is already paused."
            else:
                seconds = int(result.split("_")[-1])
                mins, secs = divmod(seconds, 60)
                return f"Video paused at {mins}:{secs:02d}."
        except Exception as e:
            return f"Error pausing video: {e}"
    return "Error: Chrome is not open."
def resume_video():
    """Resume the video on the current tab."""
    global driver
    if driver:
        try:
            result = driver.execute_script("""
                var v = document.querySelector('video');
                if (!v) return 'no_video';
                if (isNaN(v.duration)) return 'no_real_video';
                if (!v.paused) return 'already_playing';
                v.play();
                return 'resumed_at_' + Math.floor(v.currentTime);
            """)
            if result == "no_video":
                return "Error: No video found on this page."
            elif result == "no_real_video":
                return "Error: No video is loaded on this page. Use play_youtube to play a song."
            elif result == "already_playing":
                return "Video is already playing."
            else:
                seconds = int(result.split("_")[-1])
                mins, secs = divmod(seconds, 60)
                return f"Video resumed from {mins}:{secs:02d}."
        except Exception as e:
            return f"Error resuming video: {e}"
    return "Error: Chrome is not open."
def seek_video(seconds: float):
    """Seek video to an absolute position in seconds."""
    global driver
    if driver:
        try:
            result = driver.execute_script(f"""
                var v = document.querySelector('video');
                if (!v) return 'no_video';
                if (isNaN(v.duration)) return 'no_real_video';
                v.currentTime = {seconds};
                return 'seeked_to_' + Math.floor(v.currentTime);
            """)
            if result == "no_video":
                return "Error: No video found on this page."
            elif result == "no_real_video":
                return "Error: No video is loaded on this page."
            else:
                pos = int(result.split("_")[-1])
                mins, secs = divmod(pos, 60)
                return f"Video jumped to {mins}:{secs:02d}."
        except Exception as e:
            return f"Error seeking video: {e}"
    return "Error: Chrome is not open."
def adjust_video(seconds: float):
    """Adjust video position by relative seconds (negative = rewind, positive = forward)."""
    global driver
    if driver:
        try:
            result = driver.execute_script(f"""
                var v = document.querySelector('video');
                if (!v) return 'no_video';
                if (isNaN(v.duration)) return 'no_real_video';
                v.currentTime = Math.max(0, Math.min(v.duration, v.currentTime + ({seconds})));
                return 'now_at_' + Math.floor(v.currentTime);
            """)
            if result == "no_video":
                return "Error: No video found on this page."
            elif result == "no_real_video":
                return "Error: No video is loaded on this page."
            else:
                pos = int(result.split("_")[-1])
                mins, secs_r = divmod(pos, 60)
                direction = "forward" if seconds > 0 else "back"
                return f"Moved {direction} {abs(seconds)} seconds. Now at {mins}:{secs_r:02d}."
        except Exception as e:
            return f"Error adjusting video: {e}"
    return "Error: Chrome is not open."
def pause_all_tabs():
    """Pause video in ALL open tabs."""
    global driver
    if driver:
        try:
            current_handle = driver.current_window_handle
            paused_count = 0
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                try:
                    result = driver.execute_script("""
                        var v = document.querySelector('video');
                        if (v && !v.paused) { v.pause(); return 'paused'; }
                        return 'none';
                    """)
                    if result == "paused":
                        paused_count += 1
                except Exception:
                    pass
            driver.switch_to.window(current_handle)
            if paused_count > 0:
                return f"Paused video in {paused_count} tab(s)."
            return "No videos were playing."
        except Exception as e:
            return f"Error: {e}"
    return "Error: Chrome is not open."
def get_video_state():
    """Get current video state for the active tab."""
    global driver
    if driver:
        try:
            state = driver.execute_script("""
                var v = document.querySelector('video');
                if (!v) return {exists: false};
                return {
                    exists: true,
                    paused: v.paused,
                    currentTime: v.currentTime,
                    duration: v.duration,
                    title: document.title
                };
            """)
            if not state or not state.get("exists"):
                return "No video on current page."
            duration = state.get("duration", 0)
            if not duration or str(duration) == "NaN":
                return "No video loaded on this page."
            current = int(state.get("currentTime", 0))
            total = int(duration)
            c_min, c_sec = divmod(current, 60)
            t_min, t_sec = divmod(total, 60)
            status = "PAUSED" if state.get("paused") else "PLAYING"
            title = state.get("title", "Unknown")
            return f"Video is {status} at {c_min}:{c_sec:02d}/{t_min}:{t_sec:02d} — {title}"
        except Exception:
            return "Could not get video state."
    return "No browser open."
def is_browser_open() -> bool:
    """Check if Chrome is still running."""
    global driver
    if driver is None:
        return False
    try:
        _ = driver.title
        return True
    except Exception:
        driver = None
        return False
def get_driver():
    """Return driver if browser is open, else None."""
    if is_browser_open():
        return driver
    return None
