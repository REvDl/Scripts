"""
Automatic discovery of installed Steam games.

Steam stores game data in its own text format called VDF (aka KeyValues).
Each installed game has an appmanifest_<appid>.acf file (VDF syntax) inside
the steamapps folder of its library. If there is more than one library
(e.g. games installed on different drives), the list of library folders
is stored in steamapps/libraryfolders.vdf (also VDF).

On Linux in particular, a single machine can have *more than one* Steam
installation at once (e.g. the native/deb package plus a Flatpak
sandboxed install, which lives under
~/.var/app/com.valvesoftware.Steam/ because of Flatpak's virtual
filesystem). get_steam_install_paths() therefore returns every install
it can find that actually looks real, instead of stopping at the first
folder that merely exists.

This module has no third-party dependencies: it implements a minimal VDF
parser, sufficient to read these two file types.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

_TOKEN_RE = re.compile(r'"((?:[^"\\]|\\.)*)"|([{}])')


def parse_vdf(text: str) -> dict[str, Any]:
    """Minimal parser for the VDF/KeyValues format used by Steam."""
    tokens: list[str] = []
    for m in _TOKEN_RE.finditer(text):
        if m.group(2):
            tokens.append(m.group(2))
        else:
            tokens.append(m.group(1).replace('\\"', '"').replace("\\\\", "\\"))

    pos = 0

    def parse_object() -> dict[str, Any]:
        nonlocal pos
        obj: dict[str, Any] = {}
        while pos < len(tokens):
            tok = tokens[pos]
            if tok == "}":
                pos += 1
                return obj
            key = tok
            pos += 1
            if pos < len(tokens) and tokens[pos] == "{":
                pos += 1
                obj[key] = parse_object()
            elif pos < len(tokens):
                obj[key] = tokens[pos]
                pos += 1
        return obj

    result: dict[str, Any] = {}
    while pos < len(tokens):
        key = tokens[pos]
        pos += 1
        if pos < len(tokens) and tokens[pos] == "{":
            pos += 1
            result[key] = parse_object()
        elif pos < len(tokens):
            result[key] = tokens[pos]
            pos += 1
    return result


def _looks_like_steam_install(path: Path) -> bool:
    """Only count a folder as a *real* Steam install if its steamapps
    directory actually contains library data (libraryfolders.vdf, or at
    least one appmanifest_*.acf).

    Just the base folder existing is not enough: a stray ~/.steam/steam
    can be left behind with no real games in it at all (e.g. only SDK
    redistributable files dropped there by a pirated-game emulator), and
    picking that folder as "the" Steam install used to make the scanner
    stop looking any further, silently ignoring an actual Flatpak
    install sitting right next to it.
    """
    steamapps = path / "steamapps"
    if not steamapps.is_dir():
        return False
    if (steamapps / "libraryfolders.vdf").exists():
        return True
    return any(steamapps.glob("appmanifest_*.acf"))


def get_steam_install_paths(os_name: str) -> list[Path]:
    """Finds every Steam installation folder for the current OS.

    Returns a list because more than one can legitimately coexist
    (typical case: native package + Flatpak). Callers should scan all
    of them and merge the results, rather than only using the first.
    """
    if os_name == "windows":
        try:
            import winreg

            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            value, _ = winreg.QueryValueEx(key, "SteamPath")
            path = Path(value)
            if path.exists():
                return [path]
        except OSError:
            pass
        for env_var in ("ProgramFiles(x86)", "ProgramFiles"):
            base = os.environ.get(env_var)
            if base:
                candidate = Path(base) / "Steam"
                if candidate.exists():
                    return [candidate]
        return []

    if os_name == "macos":
        candidate = Path.home() / "Library" / "Application Support" / "Steam"
        return [candidate] if candidate.exists() else []

    # linux
    candidates = (
        Path.home() / ".steam" / "steam",
        Path.home() / ".steam" / "root",
        Path.home() / ".local" / "share" / "Steam",
        Path.home() / ".var" / "app" / "com.valvesoftware.Steam" / ".local" / "share" / "Steam",
    )

    found = [c for c in candidates if _looks_like_steam_install(c)]
    if found:
        return found

    # Nothing looked like a *genuine* install (steamapps with real
    # library data) - fall back to whatever plain folders exist, so
    # unusual-but-valid setups still get a chance instead of a hard
    # "not found" with no candidates at all.
    return [c for c in candidates if c.exists()]


def get_library_folders(steam_path: Path) -> list[Path]:
    """
    Returns all Steam library folders (the main one plus any extra
    libraries mounted on other drives), read from libraryfolders.vdf.
    """
    libraries = [steam_path]
    vdf_path = steam_path / "steamapps" / "libraryfolders.vdf"
    if not vdf_path.exists():
        return libraries

    try:
        data = parse_vdf(vdf_path.read_text(encoding="utf-8", errors="ignore"))
    except OSError:
        return libraries

    root = data.get("libraryfolders", data)
    for value in root.values():
        if isinstance(value, dict) and "path" in value:
            path = Path(value["path"])
            if path not in libraries:
                libraries.append(path)
    return libraries


def scan_installed_games(steam_path: Path) -> dict[str, dict[str, Any]]:
    """
    Walks every Steam library and parses appmanifest_*.acf files,
    returning {game_name: {"app_id": id, "source": "scan"}}.

    The "source": "scan" tag marks entries as auto-discovered, so that
    `steamcli --sync` knows it is safe to remove them later if the game
    gets uninstalled, without touching games added manually.
    """
    games: dict[str, dict[str, Any]] = {}
    for library in get_library_folders(steam_path):
        steamapps = library / "steamapps"
        if not steamapps.is_dir():
            continue
        for acf_file in steamapps.glob("appmanifest_*.acf"):
            try:
                data = parse_vdf(acf_file.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                continue
            state = data.get("AppState", {})
            name = state.get("name")
            app_id = state.get("appid")
            if not name or not app_id:
                continue
            try:
                games[name] = {"app_id": int(app_id), "source": "scan"}
            except ValueError:
                continue
    return games