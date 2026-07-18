# steamcli

CLI utility for launching Steam games from the terminal. Python >= 3.12, no required external dependencies.

## Features

- OS detection via `sys.platform` (Windows / Linux / macOS).
- **Automatic game discovery** — `steamcli --scan` locates your Steam install, walks every library (including extra ones on other drives, via `libraryfolders.vdf`) and parses `appmanifest_*.acf` for each installed game. Uses a small built-in VDF parser, no third-party dependency.
- **Sync mode** — `steamcli --sync` does the same, but also removes auto-detected games from the config that are no longer installed. Games you added yourself with `--add` are never touched by sync.
- Config is created automatically on first run (`config.json` in the OS-standard settings folder); `config.yaml` is also supported (requires `pyyaml` and a `config.yaml` file in the same folder).
- List games — `steamcli --list`, or just run with no arguments.
- Launch by **name** or by **AppID** — `steamcli "Dota 2"` or `steamcli 570` (name lookup is case-insensitive).
- Launching a game that isn't in the config prints a clear error and exits with code 1.
- Manually add/override games — `steamcli --add "Game Name" APP_ID` — or remove them with `steamcli --remove "Game Name"` / `steamcli --remove APP_ID` (works by name or AppID, for both manual and auto-detected entries).
- Two launch methods: via the `steam://rungameid/<id>` protocol (default, most reliable) or directly through the Steam executable with `-applaunch` (`launch_method: "executable"` in the config).

## Installation

```bash
cd steamcli
pip install .
# for YAML config support:
pip install .[yaml]
```

This installs the `steamcli` command. You can also run it without installing: `python -m steamcli ...` from the project root.

## Usage

```bash
steamcli --scan                     # auto-detect installed games (add/update only)
steamcli --sync                     # same, but also removes uninstalled games (manual entries kept)
steamcli --list                     # show the list of games
steamcli "Dota 2"                   # launch by name
steamcli 570                        # launch by AppID
steamcli --add "Portal 2" 620       # add a game manually (e.g. one that isn't installed)
steamcli --remove "Portal 2"        # remove a game by name
steamcli --remove 620               # remove a game by AppID
steamcli --config-path              # print the config file path
```

If Steam's install folder can't be auto-detected:

```bash
steamcli --scan --steam-path "D:\SteamLibrary\Steam"
```

`--scan` / `--sync` can be re-run any time, e.g. after installing or uninstalling a game, to refresh the list.

If a game isn't found:

```
$ steamcli "Half-Life 3"
Error: game "Half-Life 3" was not found in the list of available games.
Check the list with: steamcli --list
```

## Config location

- Windows: `%APPDATA%\steamcli\config.json`
- macOS: `~/Library/Application Support/steamcli/config.json`
- Linux: `~/.config/steamcli/config.json`

Example content after `steamcli --scan`:

```json
{
  "steam_path": {
    "windows": "C:\\Program Files (x86)\\Steam\\steam.exe",
    "linux": "steam",
    "macos": "/Applications/Steam.app/Contents/MacOS/steam_osx"
  },
  "launch_method": "protocol",
  "games": {
    "Counter-Strike 2": { "app_id": 730, "source": "scan" },
    "Dota 2": { "app_id": 570, "source": "scan" }
  }
}
```

`"source"` marks where an entry came from: `"scan"` for auto-detected games (safe to remove via `--sync` if uninstalled) or `"manual"` for ones added with `--add` (never removed automatically).

`steam_path` is only used by the `"executable"` launch method (direct `-applaunch`) — game *discovery* via `--scan`/`--sync` uses a separately auto-detected Steam folder (Windows registry, or standard paths on Linux/macOS).

You can find a game's AppID on its Steam Store page URL, or on [SteamDB](https://steamdb.info).

## Project structure

```
steamcli/
├── steamcli/
│   ├── __init__.py
│   ├── __main__.py       # python -m steamcli
│   ├── cli.py             # argparse, entry point
│   ├── config.py          # read/write config.json|yaml
│   ├── launcher.py        # find a game by name/AppID and launch Steam
│   └── steam_scanner.py   # Steam folder detection + VDF parser + .acf scanning
├── pyproject.toml
└── README.md
```