import os

def read_file(path: str) -> str:
    """Read contents of a text file."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path: str, content: str):
    """Write contents to a text file."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def list_directory(path: str) -> list:
    """List files in a directory."""
    return os.listdir(path)
