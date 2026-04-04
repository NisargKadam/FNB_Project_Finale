from openai import OpenAI

MODEL = "gpt-4o-mini"

def get_client() -> OpenAI:
    return OpenAI()
