"""Finding a game in the config and launching it through Steam."""

from __future__ import annotations

import subprocess
import webbrowser
from typing import Any

from . import ui
from .config import get_os_name


class GameNotFoundError(Exception):
    """No game matching the given name or AppID was found in the config."""


class LaunchConfigError(Exception):
    """Invalid launch configuration (missing app_id / missing steam path)."""


def find_game(query: str, config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """
    Looks up a game by name (case-insensitive) or by numeric AppID.
    Returns (display_name, game_data) or raises GameNotFoundError.
    """
    games = config.get("games", {}) or {}
    query = query.strip()

    if query.isdigit():
        target_id = int(query)
        for name, data in games.items():
            if data.get("app_id") == target_id:
                return name, data
        raise GameNotFoundError(query)

    for name, data in games.items():
        if name.lower() == query.lower():
            return name, data
    raise GameNotFoundError(query)


def launch_game(query: str, config: dict[str, Any]) -> None:
    """Launches a game by name or AppID, using the configured launch method."""
    name, data = find_game(query, config)

    app_id = data.get("app_id")
    if not app_id:
        raise LaunchConfigError(f'Game "{name}" has no app_id set in the config.')

    method = config.get("launch_method", "protocol")

    if method == "executable":
        os_name = get_os_name()
        steam_path = (config.get("steam_path") or {}).get(os_name)
        if not steam_path:
            raise LaunchConfigError(f'No steam_path set for OS "{os_name}" in the config.')
        subprocess.Popen([steam_path, "-applaunch", str(app_id)])
    else:
        webbrowser.open(f"steam://rungameid/{app_id}")

    ui.success(f'Launching "{name}" (AppID: {app_id})...')


def list_games(config: dict[str, Any]) -> None:
    games = config.get("games", {}) or {}
    if not games:
        ui.warning("No games in the config yet.")
        ui.dim("Run 'steamcli --scan' to auto-detect installed games,")
        ui.dim('or add one manually: steamcli --add "Game Name" APP_ID')
        return

    ui.heading("Available games:")
    width = max(len(n) for n in games) + 2
    for name, data in sorted(games.items()):
        app_id = data.get("app_id", "?")
        source = data.get("source")
        tag = f"{ui.DIM} (manual){ui.RST}" if source == "manual" else ""
        print(f"  {name:<{width}} {ui.DIM}AppID:{ui.RST} {app_id}{tag}")