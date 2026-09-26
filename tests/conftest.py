import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

for app_dir in ("services/api/app", "services/camera/app"):
  path = str(ROOT / app_dir)
  if path not in sys.path:
    sys.path.insert(0, path)