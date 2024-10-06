from enum import Enum

class LLMEnum(Enum):
    OLLAMA = "ollama"
    GROQ = "groq"
    MISTRAL = "mistral"
    QWEN2 = "qwen2:0.5b"
    MIXTURE = "mixtral-8x7b-32768"
    