```
 ██████╗ ███████╗ ██████╗██████╗ ██╗   ██╗██████╗ ████████╗
 ██╔══██╗██╔════╝██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝
 ██║  ██║█████╗  ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║
 ██║  ██║██╔══╝  ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║
 ██████╔╝███████╗╚██████╗██║  ██║   ██║   ██║        ██║
 ╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝
```

AI-powered CLI tool that connects natural language with developer workflows:

- Git commit generation
- Shell command generation
- Slang / abbreviation decoding

Powered by Google Gemini API.

---

## Features

### Commit Generator (default mode)
Generates Conventional Commit messages from:
- staged git diff (`git diff --staged`)
- or manual input text

Example:
```bash
git add .
decrypt
```

or:
```bash
decrypt "fix auth bug in jwt middleware"
```

---

### Shell Command Generator
Convert natural language into executable terminal commands.

```bash
decrypt -s "find all png files larger than 10MB and delete them"
```

---

### Slang Decoder
Expands internet slang and shorthand into readable text.

```bash
decrypt -sl "hru btw idk"
```

---

### Interactive Mode
Run without arguments:

```bash
decrypt
```

---

## Installation

### From PyPI
```bash
pip install decrypt
```

### Recommended (CLI isolation)
```bash
pipx install decrypt
```

### Local install
```bash
git clone https://github.com/REvDl/Scripts.git
cd Scripts/automation_tool/DecrypMessage
pip install .
```

---

## Configuration

On first run:
- Gemini API key
- Default language

Stored at:
```
~/.config/decrypt/.env
```

Reset:
```bash
decrypt --config
```

---

## CLI Usage

```
usage: decrypt [-h] [--lang LANG] [--config] [-sl] [-s] [-c] [text]

positional arguments:
  text          input text or git diff

options:
  -h, --help    show help
  --lang LANG   output language
  --config      reconfigure API key and language
  -sl, --slang  decode slang
  -s, --shell   generate shell command
  -c, --commit  generate commit message
```

---

## Examples

Commit:
```bash
git add .
decrypt
```

Shell:
```bash
decrypt -s "kill all processes on port 3000"
```

Slang:
```bash
decrypt -sl "idk brb hru"
```

---

## Why

Developers constantly:
- write commit messages manually
- translate natural language into shell commands
- decode slang and shorthand text

This tool unifies all of that into a single CLI.

---

## Tech Stack

- Python 3.10+
- Google Gemini API
- Tenacity
- Pydantic Settings
- argparse

---