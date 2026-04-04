from openai import OpenAI

MODEL = "gpt-4-mini"

def get_client() -> OpenAI:
    return OpenAI()
