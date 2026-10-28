from pathlib import Path
from typing import List, Dict
import fnmatch

from config import DEFAULT_EXCLUDE_PATTERNS
from core.hasher import get_file_info

def should_exclude(path: Path, exclude_patterns: List[str]) -> bool:
    path_str = str(path)
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(path_str, pattern):
            return True
    return False


def scan_directory(directory: Path, exclude_patterns: List[str] = None) -> List[Dict]:
    """Recursively scan directory and return file info list."""
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDE_PATTERNS.copy()

    files_info = []
    directory = directory.absolute()

    try:
        for item in directory.rglob("*"):
            if item.is_file():
                if should_exclude(item, exclude_patterns):
                    continue
                file_info = get_file_info(item)
                if file_info:
                    files_info.append(file_info)
    except Exception as e:
        print(f"❌ Error scanning {directory}: {e}")

    return files_info