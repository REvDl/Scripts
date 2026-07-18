"""CLI entry point: steamcli "Game Name" / steamcli 730 / steamcli --list ..."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .config import get_config_path, get_os_name, load_config, save_config
from .launcher import GameNotFoundError, LaunchConfigError, launch_game, list_games
from .steam_scanner import get_steam_install_path, scan_installed_games


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="steamcli",
        description="Launch Steam games from the command line.",
    )
    parser.add_argument(
        "game",
        nargs="?",
        help='Game name or AppID to launch, e.g. steamcli "Dota 2" or steamcli 570',
    )
    parser.add_argument(
        "-l", "--list", action="store_true", help="show the list of available games"
    )
    parser.add_argument(
        "--config-path", action="store_true", help="print the path to the config file"
    )
    parser.add_argument(
        "--add",
        nargs=2,
        metavar=("NAME", "APP_ID"),
        help='manually add a game to the config: --add "Half-Life 2" 220',
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="auto-detect installed Steam games (via .acf files) and add/update "
        "them in the config; existing entries not found on disk are kept as-is",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="like --scan, but also removes auto-detected games that are no "
        "longer installed. Games added manually with --add are never removed",
    )
    parser.add_argument(
        "--steam-path",
        metavar="PATH",
        help="manually specify the Steam install folder, used with --scan/--sync "
        "if auto-detection fails",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"steamcli {__version__}"
    )
    return parser


def _resolve_steam_path(args: argparse.Namespace) -> Path | None:
    if args.steam_path:
        return Path(args.steam_path)
    return get_steam_install_path(get_os_name())


def _run_scan(config: dict, args: argparse.Namespace, *, remove_missing: bool) -> int:
    steam_path = _resolve_steam_path(args)
    if not steam_path or not steam_path.exists():
        print("Error: could not find a Steam installation folder.")
        print("Specify it manually: steamcli --scan --steam-path <path>")
        return 1

    found = scan_installed_games(steam_path)
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
        print(f"No installed games found in {steam_path}.")
        return 0

    print(f"Found installed games: {len(found)}")
    print(f"  added:   {added}")
    print(f"  updated: {updated}")
    if remove_missing:
        print(f"  removed: {len(removed)}" + (f" ({', '.join(removed)})" if removed else ""))
    print(f"Config saved: {get_config_path()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.config_path:
        print(get_config_path())
        return 0

    config = load_config()

    if args.sync:
        return _run_scan(config, args, remove_missing=True)

    if args.scan:
        return _run_scan(config, args, remove_missing=False)

    if args.add:
        name, app_id_raw = args.add
        try:
            app_id = int(app_id_raw)
        except ValueError:
            print(f'Error: APP_ID must be a number, got "{app_id_raw}".')
            return 1
        config.setdefault("games", {})[name] = {"app_id": app_id, "source": "manual"}
        save_config(config)
        print(f'Added "{name}" (AppID: {app_id}) to the config.')
        return 0

    if args.list or not args.game:
        list_games(config)
        if not args.game:
            print('\nTip: launch a game with steamcli "Game Name" or steamcli <AppID>')
        return 0

    try:
        launch_game(args.game, config)
    except GameNotFoundError:
        print(f'Error: game "{args.game}" was not found in the list of available games.')
        print("Check the list with: steamcli --list")
        return 1
    except LaunchConfigError as exc:
        print(f"Configuration error: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())