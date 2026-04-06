"""Launcher for the main game file.

Keeps the documented run command working:
    python stellar_vagabond.py
"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    game_file = Path(__file__).with_name("Stellar vagabond.py")
    runpy.run_path(game_file, run_name="__main__")
