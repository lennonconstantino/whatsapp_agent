from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
import os

_ = load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

_PROVIDER_MAP = {
    "openai": ChatOpenAI,
    "google": ChatGoogleGenerativeAI
}

MODEL_CONFIGS = [
    {
        "key_name": "g25flash",
        "provider" : "google",
        "model_name": "gemini-2.5-flash",
        "temprature": 0,
    },
    {
        "key_name":"3.5-turbo",
        "provider":"openai",
        "model_name":"gpt-3.5-turbo",
    },
    {
        "key_name": "o4",
        "provider": "openai",
        "model_name": "o4-mini-2025-04-16",
    },
    {
        "key_name": "gpt_4o",
        "provider": "openai",
        "model_name": "gpt-4o-2024-08-06",
    },
]

def _create_chat_model(model_name: str, provider: str, temperature: float | None = None):
    if provider not in _PROVIDER_MAP:
        raise ValueError(f"Provedor nao suportado: {provider}. Provedores suportados sao: {list(_PROVIDER_MAP.keys())}")

    model_class = _PROVIDER_MAP[provider]
    params = {"model": model_name}
    if temperature is not None:
        params["temperature"] = temperature

    if provider == "google":
        # Importar as classes necessárias para safety_settings
        from langchain_google_genai import HarmCategory, HarmBlockThreshold
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        }
        params["safety_settings"] = safety_settings

    return model_class(**params)

models = {}

for config in MODEL_CONFIGS:
    models[config["key_name"]] = _create_chat_model(
        model_name=config["model_name"],
        provider=config["provider"],
        temperature=config.get("temperature")
    )

LLM = "g25flash"

if __name__ == "__main__":
    print()