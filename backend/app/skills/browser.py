import webbrowser
import os
import subprocess

def navigate(url: str):
    """Navigate to a URL using the default browser."""
    webbrowser.open(url)

def search(query: str):
    """Search Google in the default browser."""
    webbrowser.open(f"https://www.google.com/search?q={query}")
