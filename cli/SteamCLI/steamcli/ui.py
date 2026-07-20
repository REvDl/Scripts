"""Shared terminal styling: ANSI colors, banner and print helpers.

Mirrors the visual language used across REvDl's CLI tools (decrypt),
so both tools feel consistent to use: green for success/headings,
yellow for warnings, red for errors, dim for secondary/hint text.
"""

from __future__ import annotations
from . import __version__
GREEN = "\033[92m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
DIM = "\033[2m"
RST = "\033[0m"
BLUE = "\033[34m"


BANNER = f"""{BLUE}{BOLD}
 ███████╗████████╗███████╗ █████╗ ███╗   ███╗ ██████╗██╗     ██╗
 ██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██╔════╝██║     ██║
 ███████╗   ██║   █████╗  ███████║██╔████╔██║██║     ██║     ██║
 ╚════██║   ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║██║     ██║     ██║
 ███████║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║╚██████╗███████╗██║
 ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝╚══════╝╚═╝{RST}
{DIM}Launch your Steam games from the command line{RST}
{DIM}v{__version__} Author: github.com/REvDl{RST}
"""


def banner() -> None:
    print(BANNER)


def error(message: str) -> None:
    print(f"{RED}{message}{RST}")


def warning(message: str) -> None:
    print(f"{YELLOW}{message}{RST}")


def success(message: str) -> None:
    print(f"{GREEN}{message}{RST}")


def heading(message: str) -> None:
    print(f"{GREEN}{BOLD}{message}{RST}")


def dim(message: str) -> None:
    print(f"{DIM}{message}{RST}")


def info(message: str) -> None:
    """Neutral/blue informational line (paths, config locations, etc.)."""
    print(f"{BLUE}{message}{RST}")


def kv(key: str, value: str, *, width: int = 0) -> None:
    """Aligned 'key: value' row, key padded to `width`, key dimmed."""
    print(f"  {key:<{width}} {DIM}{value}{RST}" if width else f"  {DIM}{key}{RST} {value}")