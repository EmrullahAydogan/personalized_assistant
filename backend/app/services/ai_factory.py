from typing import Optional
from app.services.ai_base import AIServiceBase
from app.services.ai_openai import OpenAIService
from app.services.ai_anthropic import AnthropicService
from app.services.ai_gemini import GeminiService
from app.services.ai_ollama import OllamaService
from app.core.config import settings


class AIServiceFactory:
    """Factory for creating AI service instances"""

    _instances = {}

    @classmethod
    def get_service(cls, provider: Optional[str] = None) -> AIServiceBase:
        """
        Get an AI service instance

        Args:
            provider: AI provider name (openai, anthropic, gemini, ollama)
                     If None, uses DEFAULT_AI_PROVIDER from settings

        Returns:
            AIServiceBase instance

        Raises:
            ValueError: If provider is not supported
        """
        provider = provider or settings.DEFAULT_AI_PROVIDER

        # Return cached instance if available
        if provider in cls._instances:
            return cls._instances[provider]

        # Create new instance based on provider
        if provider == "openai":
            service = OpenAIService()
        elif provider == "anthropic":
            service = AnthropicService()
        elif provider == "gemini":
            service = GeminiService()
        elif provider == "ollama":
            service = OllamaService()
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

        # Cache the instance
        cls._instances[provider] = service
        return service

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available AI providers"""
        providers = []

        if settings.OPENAI_API_KEY:
            providers.append("openai")
        if settings.ANTHROPIC_API_KEY:
            providers.append("anthropic")
        if settings.GOOGLE_API_KEY:
            providers.append("gemini")
        # Ollama is always available if host is accessible
        providers.append("ollama")

        return providers

    @classmethod
    def clear_cache(cls):
        """Clear cached service instances"""
        cls._instances = {}
