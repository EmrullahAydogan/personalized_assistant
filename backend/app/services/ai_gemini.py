from typing import List, Dict, AsyncGenerator
import google.generativeai as genai
from app.services.ai_base import AIServiceBase
from app.core.config import settings


class GeminiService(AIServiceBase):
    """Google Gemini service implementation"""

    def __init__(self, model: str = "gemini-pro"):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(model)
        self.chat_session = None

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
    ) -> str | AsyncGenerator[str, None]:
        """Send a chat request to Google Gemini"""

        # Convert messages to Gemini format
        gemini_messages = []
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            gemini_messages.append({"role": role, "parts": [msg["content"]]})

        # Create or update chat session
        if not self.chat_session:
            self.chat_session = self.model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])

        # Get the last message
        last_message = gemini_messages[-1]["parts"][0] if gemini_messages else ""

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        if stream:
            return self._stream_chat(last_message, generation_config)

        response = await self.chat_session.send_message_async(
            last_message,
            generation_config=generation_config,
        )

        return response.text

    async def _stream_chat(
        self,
        message: str,
        generation_config: dict,
    ) -> AsyncGenerator[str, None]:
        """Stream chat responses"""
        response = await self.chat_session.send_message_async(
            message,
            generation_config=generation_config,
            stream=True,
        )

        async for chunk in response:
            if chunk.text:
                yield chunk.text

    async def analyze_document(self, text: str, prompt: str = None) -> str:
        """Analyze a document"""
        analysis_prompt = prompt or "Analyze the following document and provide key insights:"

        messages = [
            {"role": "user", "content": f"{analysis_prompt}\n\n{text}"},
        ]

        # Reset chat session for document analysis
        self.chat_session = None
        return await self.chat(messages, temperature=0.3)

    async def summarize(self, text: str, max_length: int = 200) -> str:
        """Summarize text"""
        messages = [
            {
                "role": "user",
                "content": f"Summarize the following text in approximately {max_length} words:\n\n{text}",
            },
        ]

        # Reset chat session for summarization
        self.chat_session = None
        return await self.chat(messages, temperature=0.3, max_tokens=max_length * 2)

    def get_provider_name(self) -> str:
        return "gemini"
