# Github themes

Small Python utility for generating previews of GitHub Readme Stats themes and Top Languages card themes.

It automatically creates Markdown files with all theme variations so you can visually compare them and choose the best one for your GitHub profile.

---

## Features

- Generates preview links for all GitHub Readme Stats themes
- Generates preview links for Top Languages card themes
- Exports ready-to-use Markdown files
- Automatically names output files based on content
- Optional browser auto-preview mode
- Easy to extend with custom themes or users

---

## Requirements

- Python 3.12+
- No external libraries required (only standard library)

---

## Setup

Clone or download the script:

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

---

## Configuration (IMPORTANT)

Before running, replace the username in the URLs:

```python
BASE_URL_STATS = "https://github-readme-stats.shion.dev/api?username=YOUR_USERNAME&show_icons=true&theme={}&rank_icon=github"

BASE_LANGS_URL = "https://github-readme-stats.shion.dev/api/top-langs/?username=YOUR_USERNAME&layout=compact&theme={}"
```

Replace:
YOUR_USERNAME → your actual GitHub username

Example:
username=REvDl

---

## Usage

Run script:

```bash
python github_theme.py
```

This will generate Markdown files automatically:

- stats.md → preview of GitHub stats card themes
- langs.md → preview of top languages themes

File names are generated dynamically depending on the function call:
- Each function call defines its own output filename
- You can change filenames in the function parameters
- This allows flexible generation for different card types or users

---

## Optional: Open in browser

If you want to automatically open all theme previews in browser:

```python
get_url_theme(BASE_URL_STATS, open_browser=True)
```

Warning: this will open many tabs (one per theme).

---

## Output Example

Each generated file contains Markdown like:

```markdown
![tokyonight](https://github-readme-stats.shion.dev/api?...theme=tokyonight)
![dracula](https://github-readme-stats.shion.dev/api?...theme=dracula)
```

These will render as images in GitHub README.

---

## How it works

- Takes a list of theme names
- Injects them into URL templates
- Generates Markdown preview files
- Automatically names output files based on function parameters
- (optional) opens URLs in browser

---

## Notes

- STATS_THEME → themes for main stats card
- REPO_CARD_THEME → reserved for repo card support (not used yet)
- File names are configurable via function arguments
- You can easily extend or split outputs per theme group