```text
 ██████╗ ███████╗ ██████╗██████╗ ██╗   ██╗██████╗ ████████╗
 ██╔══██╗██╔════╝██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝
 ██║  ██║█████╗  ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   
 ██║  ██║██╔══╝  ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   
 ██████╔╝███████╗╚██████╗██║  ██║   ██║   ██║        ██║   
 ╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝   
```

AI-powered CLI utility providing an operational bridge between natural language instructions, automatic Git commit generation, and contextual slang decoding using the Google Gemini API. Built for high performance and strict output isolation.

## Features

- **Automated Commit Generation (Default Mode):** Automatically extracts and staging-analyses active local diffs via `git diff --staged` to generate professional, clean Conventional Commits messages.
- **Natural Language Shell Commands (`-s` / `--shell`):** Converts loose technical intents into valid, optimized, executable Bash or cross-platform terminal commands.
- **Accurate Slang & Internet Abbreviation Decoder (`-sl` / `--slang`):** Recovers structure, expands short forms, and normalizes text lacking vowels or proper grammar into standard text for specified target languages.
- **Fault-Tolerant Fallback System:** Uses a multi-model architecture pool (`gemini-2.5-flash` -> `gemini-2.5-flash-lite`) combined with exponential backoff retries via `tenacity` to stay operational during 429 quota limits or 503 errors.

## Installation

```bash
git clone [https://github.com/REvDl/Scripts.git](https://github.com/REvDl/Scripts.git)
cd Scripts/automation_tool/DecrypMessage
pip install .
```

## Configuration

On the initial execution, the application will automatically prompt you to enter your **Gemini API Key** and preferred **default language**. These credentials are saved to a local configuration file.

- **Storage Location:** `~/.config/decrypt/.env`
- **Manual Reset Command:** `decrypt --config`

## Technical Reference & CLI Arguments

```text
usage: decrypt [-h] [--lang LANG] [--config] [-sl] [-s] [-c] [text]

AI-powered CLI tool
• Conventional Commits
• Shell Commands
• Slang Decoder

positional arguments:
  text           Optional text input. Commit mode (default): if empty, uses git diff; 
                 if provided, generates commit from this description.

options:
  -h, --help     show this help message and exit
  --lang LANG    Transcription language (default from .env)
  --config       Force re-configure API key and language
  -sl, --slang   Mode: Accurately expand and decipher internet abbreviations and slang
  -s, --shell    Mode: Generate an executable shell command from natural language
  -c, --commit   Mode: Generate Git commit message from text or staged diffs (default)
```

## Usage Examples

### 1. Generating Conventional Commits

Stage your local changes and execute the default command pipeline:

```bash
git add src/core.py
decrypt
```

Alternatively, pass raw text input directly through standard arguments to format a manual draft:

```bash
decrypt "fixed a broken connections pooling bug inside the database wrapper"
```

### 2. Translating Natural Language to Terminal Syntax

```bash
decrypt -s "find all json files in the current folder larger than 50 megabytes and delete them"
```

### 3. Expanding Slang / Chat History

```bash
decrypt -sl "hru btw" --lang "English"
```

### 4. Interactive Mode (REPL)

Executing the engine without positional string parameters drops down into a low-overhead, persistent shell environment running standard loops:

```bash
decrypt -s
```

```text
Interactive mode (SHELL). Language: English. Type 'exit' to quit.
> list all docker containers running on port 80
docker ps --filter "publish=80"
> 
```