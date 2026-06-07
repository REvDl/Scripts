import argparse



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



from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from google.genai.errors import APIError

class Settings(BaseSettings):
    API_KEY: str
    USER_LANGUAGE: str
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

def is_retryable_error(exception):
    return isinstance(exception, APIError) and exception.code == 503

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
    retry=retry_if_exception(is_retryable_error),
    reraise=True
)
def _retry_request(client, model, contents, config):
    return client.models.generate_content(
        model=model, contents=contents, config=config
    )

def decode_slang(short_text:str, user_api_key):
    try:
        client = genai.Client(api_key=user_api_key)
        config = types.GenerateContentConfig(
            system_instruction=(
                "You are a linguistic assistant. Your job is to transcribe abbreviated "
                "texts, internet slang, and vowel-less messages into full, literate "
                f"sentences in the {settings.USER_LANGUAGE} language. Return ONLY the corrected text, "
                "without unnecessary comments, quotation marks, or formatting."
            ),
            temperature=0.2,
        )
        response = _retry_request(
            client=client,
            model="gemini-2.5-flash",
            contents=short_text,
            config=config,
        )
        return response.text.strip()
    except APIError as e:
        return f"Gemini API Error (Status {e.code}): {e.message}"
    except Exception as e:
        return f"Unexpected error: {e}"


def main():
    if not settings.API_KEY:
        print("Error. API KEY is missing")
        return
    client = genai.Client(api_key=settings.API_KEY)
    if args.text:
        print(decode_slang(client, args.text, target_language))
    else:
        print(f"Interactive mode. Language: {target_language}. Type 'exit' to quit.")
        while True:
            try:
                user_text = input("> ")
                if user_text.lower() in ["exit", "break"]:
                    break
                if not user_text.strip():
                    continue
                print(decode_slang(client, user_text, target_language))
            except (KeyboardInterrupt, EOFError):
                break

if __name__ == "__main__":
    main()
