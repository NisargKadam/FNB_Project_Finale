import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
# Read model from env so it can be changed without touching code.
# Falls back to gpt-3.5-turbo which is universally available.
MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

def get_client() -> OpenAI:
    return OpenAI()
