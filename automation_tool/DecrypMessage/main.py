from pydantic_settings import BaseSettings, SettingsConfigDict
import os
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
    while True:
        user_text = input("Your request (or 'exit'): ")
        if user_text.lower() in ["exit", "break"]:
            break
        if not user_text.strip():
            continue
        print(decode_slang(user_text, settings.API_KEY))
    return ""

if __name__ == "__main__":
    main()
