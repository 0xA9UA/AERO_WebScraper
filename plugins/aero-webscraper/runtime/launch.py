# MMA FILE SUMMARY
# Purpose: Starts the packaged local MCP backend using its bundled canonical source copy.
# Public interface: python runtime/launch.py; AERO_LIBRARY_ROOT selects persistent storage.
# Invariants: Protocol stdout belongs to the backend; no dependency download or imported execution.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from aero_webscraper.adapters.cli import main
if __name__ == "__main__":
    raise SystemExit(main(["serve"]))