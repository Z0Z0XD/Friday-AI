import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo.
    Returns formatted results with titles, URLs, and snippets.
    No browser needed — pure HTTP request.
    """
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "No results found."
        formatted = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "No title")
            url = r.get("href", r.get("link", "No URL"))
            snippet = r.get("body", r.get("snippet", "No description"))
            formatted.append(f"{i}. {title}\n   URL: {url}\n   {snippet}")
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Search failed: {e}"
def read_page(url: str, max_chars: int = 3000) -> str:
    """
    Fetch a webpage and extract readable text content.
    Strips scripts, styles, nav, footer, ads.
    Returns clean text up to max_chars.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Remove non-content elements
        for tag in soup(["script", "style", "nav", "footer", "header",
                         "aside", "form", "iframe", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        # Clean up excessive blank lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)
        if not clean_text:
            return "Could not extract readable content from this page."
        if len(clean_text) > max_chars:
            clean_text = clean_text[:max_chars] + "\n\n[Content truncated]"
        return clean_text
    except requests.exceptions.Timeout:
        return "Page load timed out."
    except requests.exceptions.RequestException as e:
        return f"Failed to read page: {e}"
