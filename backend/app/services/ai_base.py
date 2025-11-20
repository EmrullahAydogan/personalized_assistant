from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator


class AIServiceBase(ABC):
    """Base class for AI service providers"""

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
    ) -> str | AsyncGenerator[str, None]:
        """
        Send a chat request to the AI service

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Response text or async generator for streaming
        """
        pass

    @abstractmethod
    async def analyze_document(self, text: str, prompt: str = None) -> str:
        """
        Analyze a document text

        Args:
            text: Document text to analyze
            prompt: Optional custom prompt for analysis

        Returns:
            Analysis result
        """
        pass

    @abstractmethod
    async def summarize(self, text: str, max_length: int = 200) -> str:
        """
        Summarize text

        Args:
            text: Text to summarize
            max_length: Maximum length of summary

        Returns:
            Summary text
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name"""
        pass
