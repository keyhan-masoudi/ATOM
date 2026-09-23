"""Repository locations shared by the simulator and command-line tools."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data"
CACHE_ROOT = DATA_ROOT / "caches"
DATASET_ROOT = DATA_ROOT / "datasets"
REPORT_ROOT = DATA_ROOT / "reports"
