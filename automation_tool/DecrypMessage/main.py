import argparse
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

#parser
parser = argparse.ArgumentParser(
    description="CLI utility for deciphering internet abbreviations using the Gemini API."
)
parser.add_argument(
    "text", nargs="?", type=str, help="Abbreviated text to be deciphered"
)
parser.add_argument(
    "--lang",
    type=str,
    default=None,
    help="Transcription language (default from .env)",
)
args = parser.parse_args()


HOME_DIR = Path.home()
CONFIG_DIR = HOME_DIR / ".config" / "decryp"
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
    stop=stop_after_attempt(6),
    wait=wait_exponential(multiplier=2, min=2, max=60),
    retry=retry_if_exception(is_retryable_error),
    reraise=True,
)
def _retry_request(client, model, contents, config):
    return client.models.generate_content(
        model=model, contents=contents, config=config
    )

def decode_slang(client: genai.Client, short_text:str, target_lang: str):
    try:
        config = types.GenerateContentConfig(
            system_instruction=(
                "You are a linguistic assistant. Your job is to accurately expand and decipher "
                "internet abbreviations, slang, and vowel-less text into normal, grammatically correct words "
                f"in the {target_lang} language. Maintain the original meaning and structure of the words. "
                "Do not invent context or add unnecessary words if they weren't implied. "
                "Example: 'пр кд чд' should be translated as 'Привет, как дела, что делаешь?'. "
                "Return ONLY the corrected text, without comments or formatting."
            ),
            temperature=0.2,
            max_output_tokens=300,
        )
        response = _retry_request(
            client=client,
            model="gemini-2.5-flash",
            contents=short_text,
            config=config,
        )
        if response and response.text:
            return response.text.strip()
        return short_text
    except APIError as e:
        return f"Gemini API Error (Status {e.code}): {e.message}"
    except Exception as e:
        return f"Unexpected error: {e}"


def main():
    env_file = CONFIG_DIR / ".env"
    if not env_file.exists():
        print(f"Config file not found. Creating one at {env_file}")
        api_key = input("Enter your Gemini API Key: ").strip()
        lang = input("Enter default language: ").strip() or "English"
        env_file.write_text(f"API_KEY={api_key}\nUSER_LANGUAGE={lang}\n", encoding="utf-8")
    global settings
    settings = Settings()
    if not settings.API_KEY:
        print("Error. API KEY is missing")
        return
    target_language = args.lang if args.lang is not None else settings.USER_LANGUAGE

    client = genai.Client(api_key=settings.API_KEY)
    if args.text:
        print(decode_slang(client, args.text, target_language))
    else:
        try:
            import readline
        except ImportError:
            pass
        print(f"Interactive mode. Language: {target_language}. Type 'exit' to quit.")
        while True:
            try:
                user_text = input("> ")
                if user_text.lower() in ["exit", "break"]:
                    break
                if not user_text.strip():
                    continue
                result = decode_slang(client, user_text, target_language)
                print(f"\033[92m{result}\033[0m")
            except (KeyboardInterrupt, EOFError):
                print()
                break

if __name__ == "__main__":
    main()
