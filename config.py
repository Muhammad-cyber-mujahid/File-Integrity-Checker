from pathlib import Path

# ====================== PATH SETTINGS ======================
BASE_DIR = Path(__file__).parent
BASELINES_DIR = BASE_DIR / "baselines"
REPORTS_DIR = BASE_DIR / "reports"

BASELINES_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# ====================== DEFAULT SETTINGS ======================
DEFAULT_EXCLUDE_PATTERNS = [
    "*.log", "*.tmp", "*.temp", "__pycache__", ".git", ".idea",
    ".vscode", "node_modules", "*.pyc", "*.pyo", "*.DS_Store", "Thumbs.db"
]

HASH_ALGORITHM = "sha256"

# ====================== HELPER FUNCTIONS ======================
def get_baseline_path(name: str) -> Path:
    """Return path for a named baseline"""
    clean_name = name.lower().strip().replace(" ", "_")
    return BASELINES_DIR / f"{clean_name}.json"


def list_baselines() -> list:
    """Return list of all existing baseline names"""
    return [f.stem for f in BASELINES_DIR.glob("*.json") if f.is_file()]


print("✅ Configuration loaded successfully")

