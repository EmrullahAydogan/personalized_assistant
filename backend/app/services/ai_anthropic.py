from typing import List, Dict, AsyncGenerator
from anthropic import AsyncAnthropic
from app.services.ai_base import AIServiceBase
from app.core.config import settings


class AnthropicService(AIServiceBase):
    """Anthropic Claude service implementation"""

    def __init__(self, model: str = "claude-3-sonnet-20240229"):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = model

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
    ) -> str | AsyncGenerator[str, None]:
        """Send a chat request to Anthropic Claude"""

        # Extract system message if present
        system_message = ""
        claude_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append(msg)

        if stream:
            return self._stream_chat(claude_messages, system_message, temperature, max_tokens)

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message if system_message else None,
            messages=claude_messages,
        )

        return response.content[0].text

    async def _stream_chat(
        self,
        messages: List[Dict[str, str]],
        system_message: str,
        temperature: float,
        max_tokens: int,
    ) -> AsyncGenerator[str, None]:
        """Stream chat responses"""
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message if system_message else None,
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def analyze_document(self, text: str, prompt: str = None) -> str:
        """Analyze a document"""
        analysis_prompt = prompt or "Analyze the following document and provide key insights:"

        messages = [
            {"role": "user", "content": f"{analysis_prompt}\n\n{text}"},
        ]

        return await self.chat(
            messages,
            temperature=0.3,
        )

    async def summarize(self, text: str, max_length: int = 200) -> str:
        """Summarize text"""
        messages = [
            {
                "role": "user",
                "content": f"Summarize the following text in approximately {max_length} words:\n\n{text}",
            },
        ]

        return await self.chat(messages, temperature=0.3, max_tokens=max_length * 2)

    def get_provider_name(self) -> str:
        return "anthropic"
