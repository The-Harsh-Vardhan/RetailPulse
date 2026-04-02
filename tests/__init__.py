from pathlib import Path
import sys


SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
scripts_path = str(SCRIPTS_DIR)

if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)
