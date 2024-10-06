import os
from llms.LLMEnum import LLMEnum
from langchain_ollama import OllamaLLM
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

class LLMFactory:
    def __init__(self, provider:str, model:str):
        self.provider = provider
        self.model = model

    def create(self):
        if self.provider == LLMEnum.OLLAMA.value:
            return OllamaLLM(model=self.model)
        elif self.provider == LLMEnum.GROQ.value:
            return ChatGroq(api_key=groq_api_key, model=self.model, temperature=0.5)
        else:
            raise Exception("Invalid provider")