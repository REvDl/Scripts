"""CLI entry point: steamcli "Game Name" / steamcli 730 / steamcli --list ..."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from . import __version__, ui
from .config import get_config_path, get_os_name, load_config, save_config
from .launcher import GameNotFoundError, LaunchConfigError, find_game, launch_game, list_games
from .steam_scanner import get_steam_install_paths, scan_installed_games

try:
    import argcomplete
    HAS_ARGCOMPLETE = True
except ImportError:
    HAS_ARGCOMPLETE = False


def _complete_game(prefix: str, parsed_args, **kwargs) -> list[str]:
    """Hints for the game positional argument: game names + their AppIDs."""
    config = load_config()
    games = config.get("games", {})
    candidates = list(games.keys())
    candidates += [str(data["app_id"]) for data in games.values() if "app_id" in data]
    return [c for c in candidates if c.lower().startswith(prefix.lower())]


_COMPLETION_HOOK_LINE = 'eval "$(register-python-argcomplete steamcli)"'
_COMPLETION_MARKER = "# steamcli tab-completion"


_POSIX_SHELL_CONFIG: dict[str, dict[str, Any]] = {
    "bash": {
        "rc_path": lambda: Path.home() / ".bashrc",
        "lines": [_COMPLETION_HOOK_LINE],
    },
    "zsh": {
        "rc_path": lambda: Path.home() / ".zshrc",
        "lines": ["autoload -U bashcompinit", "bashcompinit", _COMPLETION_HOOK_LINE],
    },
}


def _detect_shell() -> str:
    """
    Cross-platform shell detection.

    NOTE: On Windows there is no $SHELL env var (that's Unix-only), so we
    branch on os.name first. cmd.exe vs PowerShell can't be told apart with
    100% certainty from inside a child process, but PowerShell (both
    Windows PowerShell and pwsh core) sets PSModulePath in its process
    environment and that variable propagates to child processes; cmd.exe
    does not set it unless it was itself launched from PowerShell. This is
    the same heuristic tools like nvm-windows and other cross-shell CLIs use.
    """
    if os.name == "nt":
        if os.environ.get("PSModulePath"):
            return "powershell"
        return "cmd"

    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "zsh"
    if "fish" in shell:
        return "fish"
    return "bash"


def _completion_marker_path() -> Path:
    return get_config_path().parent / ".completion_installed"


def _powershell_profile_path() -> Path | None:
    """
    Ask PowerShell itself for $PROFILE, since the correct path differs by
    host (Windows PowerShell vs pwsh, Console vs ISE vs VS Code terminal)
    """
    for exe in ("pwsh", "powershell"):
        try:
            result = subprocess.run(
                [exe, "-NoLogo", "-NoProfile", "-Command",
                 "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; $PROFILE"],
                capture_output=True, encoding="utf-8", timeout=10,
            )
        except FileNotFoundError:
            continue
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip())
    return None


def is_completion_installed() -> bool:
    shell = _detect_shell()

    if shell == "cmd":
        return True  # not supported at all - don't nag about something impossible

    if shell == "powershell":
        profile_path = _powershell_profile_path()
        if profile_path is None or not profile_path.exists():
            return False
        return "Register-ArgumentCompleter" in profile_path.read_text(encoding="utf-8", errors="ignore")

    if shell in _POSIX_SHELL_CONFIG:
        if _completion_marker_path().exists():
            return True
        rc_path = _POSIX_SHELL_CONFIG[shell]["rc_path"]()
        return rc_path.exists() and _COMPLETION_HOOK_LINE in rc_path.read_text()

    if shell == "fish":
        return (Path.home() / ".config" / "fish" / "completions" / "steamcli.fish").exists()

    return True


def install_completion() -> int:
    """steamcli --install-completion - one-time Tab-completion setup."""
    if not HAS_ARGCOMPLETE:
        ui.error("Error: argcomplete is not installed.")
        ui.dim("Install it with: pip install argcomplete")
        return 1

    shell = _detect_shell()

    if shell == "cmd":
        ui.error("Tab-completion is not supported in cmd.exe.")
        ui.dim("This is a Windows limitation, not a steamcli issue: cmd.exe has")
        ui.dim("no mechanism for programs to hook into Tab at all.")
        ui.dim("Use PowerShell, Git Bash, or WSL instead for autocompletion.")
        return 1

    if shell == "powershell":
        return _install_completion_powershell()

    if shell == "fish":
        return _install_completion_fish()

    if shell in _POSIX_SHELL_CONFIG:
        return _install_completion_posix(shell)

    ui.error(f'Shell "{shell}" is not supported for automatic setup.')
    return 1


def _install_completion_posix(shell: str) -> int:
    cfg = _POSIX_SHELL_CONFIG[shell]
    rc_path: Path = cfg["rc_path"]()
    lines_to_add: list[str] = cfg["lines"]

    existing = rc_path.read_text() if rc_path.exists() else ""

    if _COMPLETION_HOOK_LINE in existing:
        _completion_marker_path().touch()
        ui.success(f"Tab-completion is already set up in {rc_path}")
        return 0

    with rc_path.open("a") as f:
        f.write(f"\n{_COMPLETION_MARKER}\n")
        for line in lines_to_add:
            f.write(line + "\n")

    _completion_marker_path().touch()
    ui.success(f"Tab-completion added to {rc_path}")
    ui.dim(f"Restart your terminal or run: source {rc_path}")
    return 0


def _install_completion_fish() -> int:
    rc_path = Path.home() / ".config" / "fish" / "completions" / "steamcli.fish"
    rc_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["register-python-argcomplete", "--shell", "fish", "steamcli"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        ui.error("Error: could not generate fish completion script.")
        ui.dim(result.stderr)
        return 1
    rc_path.write_text(result.stdout, encoding="utf-8")
    _completion_marker_path().touch()
    ui.success(f"Tab-completion installed for fish: {rc_path}")
    return 0


def _install_completion_powershell() -> int:
    profile_path = _powershell_profile_path()
    if profile_path is None:
        ui.error("Could not find PowerShell (pwsh/powershell) to determine $PROFILE.")
        return 1
    try:
        result = subprocess.run(
            ["register-python-argcomplete", "--shell", "powershell", "steamcli"],
            capture_output=True, encoding="utf-8", timeout=10,
        )
    except FileNotFoundError:
        ui.error("Error: 'register-python-argcomplete' was not found in PATH.")
        ui.dim("It should be installed alongside argcomplete, in the same Scripts")
        ui.dim("folder as steamcli.exe. Check with:")
        ui.dim("  Get-Command steamcli, register-python-argcomplete")
        ui.dim("If only steamcli.exe is found, reinstall argcomplete:")
        ui.dim("  pip install --force-reinstall argcomplete")
        return 1
    except subprocess.TimeoutExpired:
        ui.error("Error: register-python-argcomplete timed out.")
        return 1

    if result.returncode != 0:
        ui.error("Error: could not generate PowerShell completion script.")
        ui.dim(result.stderr)
        return 1

    script = result.stdout
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    existing = profile_path.read_text(encoding="utf-8") if profile_path.exists() else ""

    if _COMPLETION_MARKER not in existing:
        with profile_path.open("a", encoding="utf-8") as f:
            f.write(f"\n{_COMPLETION_MARKER}\n")
            f.write(script)
    if not profile_path.exists() or _COMPLETION_MARKER not in profile_path.read_text(encoding="utf-8"):
        ui.error(f"Something went wrong: {profile_path} still doesn't contain the completion block.")
        return 1

    _completion_marker_path().touch()
    ui.success(f"Tab-completion added to {profile_path}")
    ui.dim(f"Restart PowerShell or run: . $PROFILE")
    ui.dim("If nothing happens on Tab, PowerShell's execution policy may be")
    ui.dim("blocking your profile script. Check with: Get-ExecutionPolicy")
    ui.dim('and if needed: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned')
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="steamcli",
        description="Launch Steam games from the command line.",
    )

    game_arg = parser.add_argument(
        "game",
        nargs="?",
        help='Game name or AppID to launch, e.g. steamcli "Dota 2" or steamcli 570',
    )
    if HAS_ARGCOMPLETE:
        game_arg.completer = _complete_game
    parser.add_argument(
        "-l", "--list", action="store_true", help="show the list of available games"
    )
    parser.add_argument(
        "-c", "--config-path", action="store_true", help="print the path to the config file"
    )
    parser.add_argument(
        "-s", "--scan",
        action="store_true",
        help="auto-detect installed Steam games (via .acf files) and add/update "
             "them in the config; existing entries not found on disk are kept as-is",
    )
    parser.add_argument(
        "-S", "--sync",
        action="store_true",
        help="like --scan, but also removes auto-detected games that are no "
             "longer installed. Games added manually with --add are never removed",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"steamcli {__version__}"
    )

    advanced_group = parser.add_argument_group("")

    advanced_group.add_argument(
        "--add",
        nargs=2,
        metavar=("NAME", "APP_ID"),
        help='manually add a game to the config: --add "Half-Life 2" 220',
    )
    advanced_group.add_argument(
        "--remove",
        metavar="NAME_OR_APPID",
        help='remove a game from the config, by name or AppID: --remove "Half-Life 2" '
             "or --remove 220",
    )
    advanced_group.add_argument(
        "--steam-path",
        metavar="PATH",
        help="manually specify a Steam install folder, used with --scan/--sync "
             "if auto-detection fails",
    )
    advanced_group.add_argument(
        "--install-completion",
        action="store_true",
        help="set up Tab-completion of game names in your shell (one-time setup)",
    )

    return parser


def _resolve_steam_paths(args: argparse.Namespace) -> list[Path]:
    """
    Returns every Steam install folder to scan.

    NOTE: get_steam_install_paths() can legitimately return more than one
    path (e.g. a native install *and* a Flatpak install side by side), so
    every caller here scans and merges all of them instead of picking just
    the first one - that's what used to make --scan silently miss games
    for Flatpak users who also had a leftover native ~/.steam/steam folder.
    """
    if args.steam_path:
        manual_path = Path(args.steam_path)
        return [manual_path] if manual_path.exists() else []
    return get_steam_install_paths(get_os_name())


def _run_scan(config: dict, args: argparse.Namespace, *, remove_missing: bool) -> int:
    steam_paths = _resolve_steam_paths(args)
    if not steam_paths:
        ui.error("Error: could not find a Steam installation folder.")
        ui.dim("Specify it manually: steamcli --scan --steam-path <path>")
        return 1

    found: dict[str, dict[str, Any]] = {}
    for steam_path in steam_paths:
        found.update(scan_installed_games(steam_path))

    games = config.setdefault("games", {})

    removed: list[str] = []
    if remove_missing:
        installed_ids = {data["app_id"] for data in found.values()}
        removed = [
            name
            for name, data in games.items()
            if data.get("source", "scan") == "scan" and data.get("app_id") not in installed_ids
        ]
        for name in removed:
            del games[name]

    added = sum(1 for name in found if name not in games)
    updated = sum(1 for name in found if name in games and games[name] != found[name])
    games.update(found)
    save_config(config)

    if not found and not removed:
        locations = ", ".join(str(p) for p in steam_paths)
        ui.warning(f"No installed games found in {locations}.")
        return 0

    ui.heading("Scan complete")
    if len(steam_paths) > 1:
        ui.dim(f"Checked {len(steam_paths)} Steam installs:")
        for p in steam_paths:
            ui.dim(f"  - {p}")
    print(f"  Found:   {len(found)}")
    ui.success(f"  Added:   {added}")
    if updated:
        ui.warning(f"  Updated: {updated}")
    else:
        print(f"  Updated: {updated}")
    if remove_missing:
        removed_suffix = f" ({', '.join(removed)})" if removed else ""
        if removed:
            ui.warning(f"  Removed: {len(removed)}{removed_suffix}")
        else:
            print(f"  Removed: {len(removed)}")
    ui.dim(f"Config saved: {get_config_path()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    if HAS_ARGCOMPLETE:
        argcomplete.autocomplete(parser)
    args = parser.parse_args(argv)

    if args.install_completion:
        return install_completion()

    if args.config_path:
        print(get_config_path())
        return 0

    config = load_config()

    if args.sync:
        return _run_scan(config, args, remove_missing=True)

    if args.scan:
        return _run_scan(config, args, remove_missing=False)

    if args.remove:
        try:
            name, _ = find_game(args.remove, config)
        except GameNotFoundError:
            ui.error(f'Error: game "{args.remove}" was not found in the config.')
            ui.dim("Check the list with: steamcli --list")
            return 1
        del config["games"][name]
        save_config(config)
        ui.success(f'Removed "{name}" from the config.')
        return 0

    if args.add:
        name, app_id_raw = args.add
        try:
            app_id = int(app_id_raw)
        except ValueError:
            ui.error(f'Error: APP_ID must be a number, got "{app_id_raw}".')
            return 1
        config.setdefault("games", {})[name] = {"app_id": app_id, "source": "manual"}
        save_config(config)
        ui.success(f'Added "{name}" (AppID: {app_id}) to the config.')
        return 0

    if args.list or not args.game:
        ui.banner()
        list_games(config)
        if not args.game:
            ui.dim('\nTip: launch a game with steamcli "Game Name" or steamcli <AppID>')
            if HAS_ARGCOMPLETE and not is_completion_installed():
                ui.dim('Tip: run "steamcli --install-completion" for Tab-completion of game names')
        return 0

    try:
        launch_game(args.game, config)
    except GameNotFoundError:
        ui.error(f'Error: game "{args.game}" was not found in the list of available games.')
        ui.dim("Check the list with: steamcli --list")
        return 1
    except LaunchConfigError as exc:
        ui.error(f"Configuration error: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())