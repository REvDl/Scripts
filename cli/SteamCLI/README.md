```
 ███████╗████████╗███████╗ █████╗ ███╗   ███╗ ██████╗██╗     ██╗
 ██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██╔════╝██║     ██║
 ███████╗   ██║   █████╗  ███████║██╔████╔██║██║     ██║     ██║
 ╚════██║   ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║██║     ██║     ██║
 ███████║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║╚██████╗███████╗██║
 ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝╚══════╝╚═╝
  Launch your Steam games from the command line
```
CLI utility that launches Steam games straight from the terminal:

- Automatic game discovery across **every** Steam install on the machine (native package, Flatpak, extra library drives)
- Sync mode that keeps the config in line with what's actually installed
- Launch by name or AppID, via the Steam protocol or directly through the Steam executable
- Manual add/remove for games Steam itself doesn't know about (e.g. not installed yet)

No required third-party dependencies. Python >= 3.10.

---

## Why

Steam has its own launcher, but if you live in a terminal, alt-tabbing to a GUI just to start a game breaks flow. `steamcli` skips that — one command, no window switching, no hunting through a library list.

The other reason it's worth having installed: `--scan`/`--sync` keep the config in sync with what's actually on disk, across every Steam install and library it can find. Set it up once, re-run it after installing something new, and it just stays current.

---

## Features

### 1. Automatic Discovery (`--scan` / `--sync`)
Locates every Steam installation it can find — including side-by-side setups like a native package plus a Flatpak sandbox — and walks every library of each one (main library + any extra ones on other drives, via `libraryfolders.vdf`), parsing `appmanifest_*.acf` for each installed game. Uses a small built-in VDF parser, no third-party dependency.

```bash
steamcli --scan                     # auto-detect installed games (add/update only)
steamcli --sync                     # same, but also removes uninstalled games
```

`--sync` also removes auto-detected games from the config that are no longer installed. Games you added yourself with `--add` are never touched by sync. Both can be re-run any time, e.g. after installing or uninstalling something, to refresh the list.

If auto-detection can't find your install (uncommon setup, unusual path):

```bash
steamcli --scan --steam-path "D:\SteamLibrary\Steam"
```

### 2. Launching
Launch by **name** or by **AppID** (name lookup is case-insensitive):

```bash
steamcli "Dota 2"
steamcli 570
```

Two launch methods are supported: via the `steam://rungameid/<id>` protocol (default, most reliable) or directly through the Steam executable with `-applaunch` (set `launch_method: "executable"` in the config). Launching a game that isn't in the config prints a clear error and exits with code 1:

```
$ steamcli "Half-Life 3"
Error: game "Half-Life 3" was not found in the list of available games.
Check the list with: steamcli --list
```

### 3. Manual management (`--add` / `--remove`)
For games you want listed before they're installed, or entries you'd rather manage by hand:

```bash
steamcli --add "Portal 2" 620       # add a game manually
steamcli --remove "Portal 2"        # remove by name
steamcli --remove 620               # remove by AppID
```

### 4. Listing & config
```bash
steamcli --list                     # show the list of games, or just run with no arguments
steamcli --config-path              # print the config file path
```
Config is created automatically on first run (`config.json` in the OS-standard settings folder); `config.yaml` is also supported (requires `pyyaml` and a `config.yaml` file in the same folder).

---

## Installation

### From PyPI
```bash
pip install steamcli
```

### Using pipx
```bash
pipx install steamcli
```

### Local development install
```bash
git clone https://github.com/REvDl/Scripts.git
cd Scripts/cli/SteamCLI
pip install .
# for YAML config support:
pip install .[yaml]
```

This installs the `steamcli` command. You can also run it without installing: `python -m steamcli ...` from the project root.

---

## Configuration

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

`steam_path` is only used by the `"executable"` launch method (direct `-applaunch`) — game *discovery* via `--scan`/`--sync` uses separately auto-detected Steam folders (Windows registry, or standard paths on Linux/macOS, including Flatpak).

You can find a game's AppID on its Steam Store page URL, or on [SteamDB](https://steamdb.info).

---

## CLI Usage

```
usage: steamcli [-h] [-l] [-c] [-s] [-S] [-v] [--add NAME APP_ID] [--remove NAME_OR_APPID] [--steam-path PATH] [game]

Launch Steam games from the command line.

positional arguments:
  game                  Game name or AppID to launch, e.g. steamcli "Dota 2" or steamcli 570

options:
  -h, --help            show this help message and exit
  -l, --list            show the list of available games
  -c, --config-path     print the path to the config file
  -s, --scan            auto-detect installed Steam games (via .acf files) and add/update them in the config; existing entries not found on disk are kept as-is
  -S, --sync            like --scan, but also removes auto-detected games that are no longer installed. Games added manually with --add are never removed
  -v, --version         show program's version number and exit

  --add NAME APP_ID     manually add a game to the config: --add "Half-Life 2" 220
  --remove NAME_OR_APPID
                        remove a game from the config, by name or AppID: --remove "Half-Life 2" or --remove 220
  --steam-path PATH     manually specify a Steam install folder, used with --scan/--sync if auto-detection fails
```

---

## Tech Stack

- Python 3.10+
- `argparse`
- built-in VDF/KeyValues parser (no dependency)
- `pyyaml` (optional, only for `config.yaml`)

## Project structure

```
steamcli/
├── steamcli/
│   ├── __init__.py
│   ├── __main__.py       # python -m steamcli
│   ├── cli.py             # argparse, entry point
│   ├── config.py          # read/write config.json|yaml
│   ├── launcher.py        # find a game by name/AppID and launch Steam
│   ├── steam_scanner.py   # Steam folder detection + VDF parser + .acf scanning
│   └── ui.py               # shared terminal styling (colors, banner)
├── pyproject.toml
├── LICENSE
└── README.md
```