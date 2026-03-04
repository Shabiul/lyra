"""
shared/utils/config_loader.py
Loads lyra.config.json from shared/config.
All services import this to get consistent config.
"""

import json
import os
from pathlib import Path


def load_config() -> dict:
    """
    Walks up from the calling file's location to find
    shared/config/lyra.config.json in the monorepo root.
    """
    # Try to find config relative to this file
    base = Path(__file__).resolve().parent.parent.parent
    config_path = base / "shared" / "config" / "lyra.config.json"

    if not config_path.exists():
        # Fallback: look in current working directory tree
        cwd = Path(os.getcwd())
        for parent in [cwd, *cwd.parents]:
            candidate = parent / "shared" / "config" / "lyra.config.json"
            if candidate.exists():
                config_path = candidate
                break

    if not config_path.exists():
        raise FileNotFoundError(
            f"lyra.config.json not found. Expected at: {config_path}"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Singleton config — import this in services
CONFIG = load_config()
