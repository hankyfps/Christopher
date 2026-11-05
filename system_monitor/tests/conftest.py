import sys
from pathlib import Path

# Projektordner in den Suchpfad, damit "import monitor" funktioniert
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
