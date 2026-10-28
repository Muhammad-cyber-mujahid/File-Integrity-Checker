import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

def create_baseline(base_dir: Path, files: List[Dict], baseline_path: Path) -> bool:
    """Create and save a named baseline"""
    base_dir = base_dir.absolute()
    baseline_data = {
        "base_directory": str(base_dir),
        "created_at": datetime.now().isoformat(),
        "total_files": len(files),
        "files": {}
    }

    for file_info in files:
        try:
            rel_path = str(Path(file_info["path"]).relative_to(base_dir))
            baseline_data["files"][rel_path] = {
                "hash": file_info["hash"],
                "size": file_info["size"]
            }
        except Exception:
            continue

    try:
        with open(baseline_path, "w", encoding="utf-8") as f:
            json.dump(baseline_data, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ Error saving baseline: {e}")
        return False


def load_baseline(baseline_path: Path) -> Dict:
    """Load a specific baseline"""
    if not baseline_path.exists():
        return {}
    try:
        with open(baseline_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading baseline: {e}")
        return {}


def compare_with_baseline(baseline_data: Dict, current_files: List[Dict]) -> Dict:
    """Compare logic"""
    changes = {"new": [], "modified": [], "deleted": [], "unchanged": 0}

    if not baseline_data or "files" not in baseline_data:
        return changes

    base_dir = Path(baseline_data["base_directory"])
    baseline_files = baseline_data["files"]

    current_dict = {}
    for f in current_files:
        try:
            rel_path = str(Path(f["path"]).relative_to(base_dir))
            current_dict[rel_path] = f
        except Exception:
            continue

    # Check modified & unchanged
    for rel_path, baseline_info in baseline_files.items():
        if rel_path in current_dict:
            curr = current_dict[rel_path]
            if curr["hash"] != baseline_info["hash"] or curr["size"] != baseline_info.get("size"):
                changes["modified"].append({
                    "path": rel_path,
                    "old_hash": baseline_info["hash"],
                    "new_hash": curr["hash"],
                    "old_size": baseline_info.get("size", 0),
                    "new_size": curr["size"],
                    "summary": f"Size changed {baseline_info.get('size', 0)} → {curr['size']} bytes"
                })
            else:
                changes["unchanged"] += 1
        else:
            changes["deleted"].append({"path": rel_path})

    # Check new files
    for rel_path, curr in current_dict.items():
        if rel_path not in baseline_files:
            changes["new"].append({
                "path": rel_path,
                "hash": curr["hash"],
                "size": curr["size"]
            })

    return changes