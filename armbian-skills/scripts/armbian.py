#!/usr/bin/env python3
"""Portable offline Armbian knowledge entry point."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/lib' if (ROOT / 'manifest.json').exists() else ROOT / 'src'))
from armbian_skills.cli import main
if __name__ == '__main__':
    sys.exit(main(ROOT))
