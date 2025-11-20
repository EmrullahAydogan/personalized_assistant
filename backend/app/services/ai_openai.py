from typing import List, Dict, AsyncGenerator
from openai import AsyncOpenAI
from app.services.ai_base import AIServiceBase
from app.core.config import settings


class OpenAIService(AIServiceBase):
    """OpenAI GPT service implementation"""

    def __init__(self, model: str = "gpt-4-turbo-preview"):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
    ) -> str | AsyncGenerator[str, None]:
        """Send a chat request to OpenAI"""

        if stream:
            return self._stream_chat(messages, temperature, max_tokens)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    async def _stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> AsyncGenerator[str, None]:
        """Stream chat responses"""
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def analyze_document(self, text: str, prompt: str = None) -> str:
        """Analyze a document"""
        analysis_prompt = prompt or "Analyze the following document and provide key insights:"

        messages = [
            {"role": "system", "content": "You are a helpful document analysis assistant."},
            {"role": "user", "content": f"{analysis_prompt}\n\n{text}"},
        ]

        return await self.chat(messages, temperature=0.3)

    async def summarize(self, text: str, max_length: int = 200) -> str:
        """Summarize text"""
        messages = [
            {"role": "system", "content": "You are a helpful summarization assistant."},
            {
                "role": "user",
                "content": f"Summarize the following text in approximately {max_length} words:\n\n{text}",
            },
        ]

        return await self.chat(messages, temperature=0.3, max_tokens=max_length * 2)

    def get_provider_name(self) -> str:
        return "openai"
