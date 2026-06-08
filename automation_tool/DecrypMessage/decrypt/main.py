import argparse
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import subprocess

#parser
parser = argparse.ArgumentParser(
    description=(
        "AI-powered CLI tool\n" 
        "• Conventional Commits\n"
        "• Shell Commands\n"
        "• Slang Decoder"
    ),
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument(
    "text", nargs="?", type=str,     help="Optional text input. Commit mode (default): if empty, uses git diff; if provided, generates commit from this description."
)
parser.add_argument(
    "--lang",
    type=str,
    default=None,
    help="Transcription language (default from .env)",
)
parser.add_argument(
    "--config",
    action="store_true",
    help="Force re-configure API key and language"
)
parser.add_argument(
    "-sl", "--slang",
    action="store_true",
    help="Mode: Accurately expand and decipher internet abbreviations and slang",
)
parser.add_argument(
    "-s", "--shell",
    action="store_true",
    help="Mode: Generate an executable shell command from natural language"
)
parser.add_argument(
    "-c", "--commit",
    action="store_true",
    help="Mode: Generate Git commit message from text or staged diffs (default)"
)
args = parser.parse_args()


HOME_DIR = Path.home()
CONFIG_DIR = HOME_DIR / ".config" / "decrypt"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
class Settings(BaseSettings):
    API_KEY: str | None = None
    USER_LANGUAGE: str | None = "English"
    model_config = SettingsConfigDict(env_file=CONFIG_DIR / ".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

def is_retryable_error(exception):
        #check HTTP status code
    if getattr(exception, "http_status_code", None) in [429, 503]:
        return True

        #check string code gRPC (RESOURCE_EXHAUSTED — 429)
    if getattr(exception, "code", None) in [429, 503, "RESOURCE_EXHAUSTED", "UNAVAILABLE"]:
        return True

    err_msg = str(exception).lower()
    if "quota" in err_msg or "limit" in err_msg or "429" in err_msg:
        return True

    return False

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
    retry=retry_if_exception(is_retryable_error),
    reraise=True,
)
def _retry_request(client, model, contents, config):
    return client.models.generate_content(
        model=model, contents=contents, config=config
    )
PROMPTS = {
    "commit": (
        "You are an expert Git assistant. Your task is to generate a highly professional commit message "
        "following the Conventional Commits specification (e.g., feat(scope): message, fix(scope): message). "
        "Analyze the provided code diff or raw user description. Use clear, concise English. "
        "Return ONLY the raw text of the commit message. No markdown blocks, no quotation marks, no explanations."
    ),
    "shell": (
        "You are a DevOps and Linux Terminal expert. Convert the user's natural language request into a valid, "
        "safe, and optimized shell command. Detect whether it looks like Windows PowerShell or Bash context if possible, "
        "but default to cross-platform or standard syntax. "
        "Return ONLY the executable command text. Do not wrap it in markdown code blocks, do not add comments."
    ),
    "slang": (
        "You are a linguistic assistant. Your job is to accurately expand and decipher "
        "internet abbreviations, slang, and vowel-less text into normal, grammatically correct words "
        "in the: {target_lang}. Maintain the original meaning. Do not invent unnecessary context. "
        "Example: 'пр кд чд' should be translated as 'Привет, как дела, что делаешь?'. "
        "Return ONLY the corrected text, without comments or formatting."
    )
}
def decode_response(client: genai.Client, short_text:str, mode:str, target_lang: str):
    models_pool = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
    system_instruction = PROMPTS[mode]
    if mode == "slang":
        system_instruction = system_instruction.format(target_lang=target_lang)

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.2 if mode != "slang" else 0.4,
        max_output_tokens=350,
    )
    for current_model in models_pool:
        try:
            response = _retry_request(
                client=client,
                model=current_model,
                contents=short_text,
                config=config,
            )
            if response and response.text:
                return response.text.strip()
            return short_text
        except APIError as e:
            is_critical = getattr(e, "code", None) in [429, 503] or "429" in str(e) or "503" in str(e)

            if current_model == models_pool[-1] or not is_critical:
                if getattr(e, "code", None) == 429 or "429" in str(e):
                    return "\n\033[31m[Exhaustion Limit] Google has limited requests. Please wait 30-60 seconds.\033[0m"
                return f"\033[31mGemini API Error (Status {e.code}): {e.message}\033[0m"

            print(f"\033[33m[Fallback] {current_model} failed (Status {e.code}). Switching to backup model...\033[0m")
            continue

        except Exception as e:
            if current_model == models_pool[-1]:
                return f"Unexpected error: {e}"
            continue


def get_git_diff():
    try:
        result = subprocess.run(
            ["git", "diff", "--staged"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

GREEN = "\033[92m"
BOLD = "\033[1m"
DIM = "\033[2m"
RST = "\033[0m"
BANNER = f"""{GREEN}{BOLD}
 ██████╗ ███████╗ ██████╗██████╗ ██╗   ██╗██████╗ ████████╗
 ██╔══██╗██╔════╝██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝
 ██║  ██║█████╗  ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   
 ██║  ██║██╔══╝  ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   
 ██████╔╝███████╗╚██████╗██║  ██║   ██║   ██║        ██║   
 ╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝   {RST}
  {DIM}AI-powered CLI tool: Conventional Commits · Shell Commands · Slang Decoder{RST}
  {DIM}v1.1 Author: github.com/REvDl{RST}
"""


def main():
    env_file = CONFIG_DIR / ".env"
    if not env_file.exists() or args.config:
        print(f"Creating config file at {env_file}")
        api_key = input("Enter your Gemini API Key: ").strip()
        lang = input("Enter default language: ").strip() or "English"
        env_file.write_text(f"API_KEY={api_key}\nUSER_LANGUAGE={lang}\n", encoding="utf-8")
        if args.config and not args.text:
            print("Configuration updated successfully!")
            return
    global settings
    settings = Settings()
    if not settings.API_KEY:
        print("Error. API KEY is missing")
        return
    target_language = args.lang if args.lang is not None else settings.USER_LANGUAGE

    client = genai.Client(api_key=settings.API_KEY)
    if args.slang:
        mode = "slang"
    elif args.shell:
        mode = "shell"
    elif args.commit:
        mode = "commit"
    else:
        mode = "commit"
    diff = None
    if mode == "commit" and not args.text:
        diff = get_git_diff()

    if args.text or diff:
        input_data = args.text
        if mode == "commit" and not input_data:
            input_data = f"Generate commit message for this diff:\n{diff}"

        result = decode_response(client, input_data, mode, target_language)
        print(result)
        return

    else:
        print(BANNER)
        if mode == "commit":
            print("\033[33m[Git Notice] No staged changes found. Starting interactive mode...\033[0m")
        try:
            import readline
        except ImportError:
            pass
        print(f"Interactive mode ({mode.upper()}). Language: {target_language}. Type 'exit' to quit.")
        while True:
            try:
                user_text = input("> ")
                if user_text.lower() in ["exit", "break"]:
                    break
                if not user_text.strip():
                    continue
                result = decode_response(client, user_text, mode, target_language)
                print(f"\033[92m{result}\033[0m")
            except (KeyboardInterrupt, EOFError):
                print()
                break

if __name__ == "__main__":
    main()