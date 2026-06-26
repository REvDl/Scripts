# DefaultInstall

PowerShell script that automatically installs essential applications on a fresh Windows system using `winget`.

## Requirements

- Windows 10 1809+ or Windows 11
- PowerShell 5.1+
- Internet connection
- Administrator privileges

## Applications installed

| App | Purpose |
|-----|---------|
| Google Chrome | Browser |
| 7-Zip | Archiver |
| VLC | Media player |
| Telegram | Messenger |
| Discord | Voice & chat |
| Steam | Game platform |
| VC++ Redist 2015+ | Runtime for apps/games |
| GeForce Experience | Nvidia drivers + game optimization |
| DirectX | Graphics runtime |
| .NET Runtime 8 | Runtime for apps |
| qBittorrent | Torrent client |

## Usage

1. Right-click `setup.ps1`
2. Select **"Run as Administrator"**
3. Wait for completion — each app installs silently
