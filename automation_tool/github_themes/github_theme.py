import webbrowser
STATS_THEME = [
    "default", "transparent", "shadow_red", "shadow_green", "shadow_blue",
    "dark", "radical", "merko", "gruvbox", "gruvbox_light",
    "tokyonight", "onedark", "cobalt", "synthwave", "highcontrast",
    "dracula", "prussian", "monokai", "vue", "vue-dark",
    "shades-of-purple", "nightowl", "buefy", "blue-green", "algolia",
    "great-gatsby", "darcula", "bear", "solarized-dark", "solarized-light",
    "chartreuse-dark", "nord", "gotham", "material-palenight", "graywhite",
    "vision-friendly-dark", "ayu-mirage", "midnight-purple", "calm", "flag-india",
    "omni", "react", "jolly", "maroongold", "yeblu",
    "blueberry", "slateorange", "kacho_ga", "outrun", "ocean_dark",
    "city_lights", "github_dark", "github_dark_dimmed", "discord_old_blurple", "aura_dark",
    "panda", "noctis_minimus", "cobalt2", "swift", "aura",
    "apprentice", "moltack", "codeSTACKr", "rose_pine", "catppuccin_latte",
    "catppuccin_mocha", "date_night", "one_dark_pro", "rose", "holi",
    "neon", "blue_navy", "calm_pink", "ambient_gradient"
]
REPO_CARD_THEME = [
    "default_repocard", "transparent", "shadow_red", "shadow_green", "shadow_blue",
    "dark", "radical", "merko", "gruvbox", "gruvbox_light",
    "tokyonight", "onedark", "cobalt", "synthwave", "highcontrast",
    "dracula", "prussian", "monokai", "vue", "vue-dark",
    "shades-of-purple", "nightowl", "buefy", "blue-green", "algolia",
    "great-gatsby", "darcula", "bear", "solarized-dark", "solarized-light",
    "chartreuse-dark", "nord", "gotham", "material-palenight", "graywhite",
    "vision-friendly-dark", "ayu-mirage", "midnight-purple", "calm", "flag-india",
    "omni", "react", "jolly", "maroongold", "yeblu",
    "blueberry", "slateorange", "kacho_ga", "outrun", "ocean_dark",
    "city_lights", "github_dark", "github_dark_dimmed", "discord_old_blurple", "aura_dark",
    "panda", "noctis_minimus", "cobalt2", "swift", "aura",
    "apprentice", "moltack", "codeSTACKr", "rose_pine", "catppuccin_latte",
    "catppuccin_mocha", "date_night", "one_dark_pro", "rose", "holi",
    "neon", "blue_navy", "calm_pink", "ambient_gradient"
]
BASE_URL_STATS = "https://github-readme-stats.shion.dev/api?username=REvDl&show_icons=true&theme={}&rank_icon=github"
BASE_LANGS_URL = "https://github-readme-stats.shion.dev/api/top-langs/?username=REvDl&layout=compact&theme={}"

def get_url_theme(main_url: str, open_browser: bool = False) -> list[str]:
	urls = [main_url.format(theme) for theme in STATS_THEME]
	if open_browser:
		for url in urls:
			webbrowser.open(url)
	return urls


def get_url_theme_file(main_url: str, filename: str = "stats.md"):
	with open(filename, "w", encoding="utf-8") as f:
		for t in STATS_THEME:
			f.write(f"![{t}]({main_url.format(t)})\n")


get_url_theme_file(BASE_URL_STATS)
get_url_theme_file(BASE_LANGS_URL, "langs.md")



