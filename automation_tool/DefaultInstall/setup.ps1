Set-ExecutionPolicy Bypass -Scope Process -Force

$apps = @(
    "Google.Chrome",
    "7zip.7zip",
    "VideoLAN.VLC",
    "Telegram.TelegramDesktop",
    "Discord.Discord",
    "Valve.Steam",
    "Microsoft.VCRedist.2015+.x64",
    "Nvidia.GeForceExperience",
    "Microsoft.DirectX",
    "Microsoft.DotNet.Runtime.8",
    "qBittorrent.qBittorrent"
)

foreach ($app in $apps) {
    winget install --id $app -e --silent --accept-package-agreements --accept-source-agreements
}

Write-Host "Completed successfully!" -ForegroundColor Green