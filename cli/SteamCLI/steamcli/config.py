"""
steamcli configuration handling.

The config lives in the user's per-OS config directory (detected via
sys.platform) and can be either JSON or YAML.

JSON (config.json) is used by default and needs no extra dependency.
If a config.yaml sits next to it, it is used instead (requires pyyaml).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from . import ui

APP_NAME = "steamcli"

try:
    import yaml  # type: ignore

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


def get_os_name() -> str:
    """Detects the current OS via sys.platform."""
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("linux"):
        return "linux"
    return "unknown"


def get_config_dir() -> Path:
    """Returns the standard config directory for the current OS."""
    os_name = get_os_name()
    if os_name == "windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif os_name == "macos":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / APP_NAME


def get_config_path() -> Path:
    """
    Returns the path to the active config file.

    If config.yaml/.yml exists (and pyyaml is available), it is used.
    Otherwise config.json is used (and created if missing).
    """
    config_dir = get_config_dir()
    yaml_path = config_dir / "config.yaml"
    yml_path = config_dir / "config.yml"
    json_path = config_dir / "config.json"

    if yaml_path.exists() and _HAS_YAML:
        return yaml_path
    if yml_path.exists() and _HAS_YAML:
        return yml_path
    return json_path


def default_config() -> dict[str, Any]:
    """Base config created on first run."""
    return {
        "steam_path": {
            "windows": r"C:\Program Files (x86)\Steam\steam.exe",
            "linux": "steam",
            "macos": "/Applications/Steam.app/Contents/MacOS/steam_osx",
        },
        "launch_method": "protocol",
        "games": {},
    }


def create_default_config(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = default_config()
    if path.suffix in (".yaml", ".yml"):
        if not _HAS_YAML:
            raise RuntimeError(
                "pyyaml is required to use a YAML config: pip install pyyaml"
            )
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    else:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def load_config() -> dict[str, Any]:
    """Loads the config, creating it with default values if missing."""
    path = get_config_path()
    if not path.exists():
        create_default_config(path)
        ui.success(f"Created default config: {path}")
        ui.dim("Run 'steamcli --scan' to detect your installed games, or edit it manually.\n")

    if path.suffix in (".yaml", ".yml"):
        if not _HAS_YAML:
            raise RuntimeError(
                f"Found a YAML config ({path}) but pyyaml is not installed. "
                "Install it with: pip install pyyaml"
            )
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    else:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)


def save_config(data: dict[str, Any], path: Path | None = None) -> None:
    path = path or get_config_path()
    if path.suffix in (".yaml", ".yml"):
        if not _HAS_YAML:
            raise RuntimeError("pyyaml is required to use a YAML config: pip install pyyaml")
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    else:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)