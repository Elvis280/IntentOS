"""
app/skills/browser.py

Browser automation skill for IntentOS.
"""
from urllib.parse import quote
from app.executor.executor import Executor

# We instantiate a local executor just to reuse its primitive actions
_executor = Executor()

def open_url(url: str):
    """Open a URL in the default browser."""
    _executor.execute({
        "action": "OPEN_URL",
        "parameters": {"url": url}
    })

def search_google(query: str):
    """Search Google for the given query."""
    url = f"https://www.google.com/search?q={quote(query)}"
    open_url(url)

def search_youtube(query: str):
    """Search YouTube for the given query."""
    url = f"https://www.youtube.com/results?search_query={quote(query)}"
    open_url(url)

def download_file(url: str):
    """Download a file by opening its URL (browser handles the download)."""
    open_url(url)
