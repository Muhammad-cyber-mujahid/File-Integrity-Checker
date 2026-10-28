import hashlib
from pathlib import Path
from typing import Dict


def get_file_hash(file_path: Path) -> str:
    """
    Calculate SHA-256 hash of a file.
    Returns the hex digest.
    """
    try:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read in chunks to handle large files efficiently
            for byte_block in iter(lambda: f.read(4096), b""):
                hasher.update(byte_block)
        return hasher.hexdigest()
    except Exception as e:
        print(f"⚠️  Error hashing {file_path}: {e}")
        return ""


def get_file_info(file_path: Path) -> Dict:
    """
    Return file information: hash and size.
    """
    try:
        if not file_path.is_file():
            return {}

        file_hash = get_file_hash(file_path)
        file_size = file_path.stat().st_size

        return {
            "path": str(file_path),
            "hash": file_hash,
            "size": file_size,
            "size_human": f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.1f} MB"
        }
    except Exception as e:
        print(f"⚠️  Error getting info for {file_path}: {e}")
        return {}


# For testing
if __name__ == "__main__":
    test_file = Path("fim_checker.py")
    if test_file.exists():
        info = get_file_info(test_file)
        print(f"Hash: {info.get('hash')}")
        print(f"Size: {info.get('size_human')}")