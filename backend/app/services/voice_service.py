import os
import tempfile
import asyncio
from typing import Optional
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from app.core.config import settings


class VoiceService:
    """Service for speech recognition and text-to-speech"""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.language = settings.VOICE_LANGUAGE

    async def speech_to_text(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
    ) -> str:
        """
        Convert speech audio file to text

        Args:
            audio_file_path: Path to audio file
            language: Language code (e.g., 'tr-TR', 'en-US')

        Returns:
            Transcribed text

        Raises:
            sr.UnknownValueError: Could not understand audio
            sr.RequestError: API error
        """
        lang = language or self.language

        def _recognize():
            # Convert audio to WAV if needed
            path = audio_file_path
            if not path.endswith('.wav'):
                audio = AudioSegment.from_file(path)
                temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                audio.export(temp_wav.name, format='wav')
                path = temp_wav.name

            # Recognize speech
            with sr.AudioFile(path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language=lang)

            return text

        # Run in thread pool to avoid blocking
        return await asyncio.to_thread(_recognize)

    async def text_to_speech(
        self,
        text: str,
        language: Optional[str] = None,
        slow: bool = False,
    ) -> str:
        """
        Convert text to speech audio file

        Args:
            text: Text to convert to speech
            language: Language code (e.g., 'tr', 'en')
            slow: Speak slowly

        Returns:
            Path to generated audio file
        """
        lang = language or self.language.split('-')[0]  # Get language without region

        def _generate_speech():
            # Generate speech
            tts = gTTS(text=text, lang=lang, slow=slow)

            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            tts.save(temp_file.name)

            return temp_file.name

        # Run in thread pool to avoid blocking
        return await asyncio.to_thread(_generate_speech)

    async def record_audio(
        self,
        duration: int = 5,
        sample_rate: int = 16000,
    ) -> str:
        """
        Record audio from microphone

        Args:
            duration: Recording duration in seconds
            sample_rate: Sample rate in Hz

        Returns:
            Path to recorded audio file
        """
        def _record():
            with sr.Microphone(sample_rate=sample_rate) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Record audio
                audio_data = self.recognizer.record(source, duration=duration)

            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)

            with open(temp_file.name, 'wb') as f:
                f.write(audio_data.get_wav_data())

            return temp_file.name

        # Run in thread pool to avoid blocking
        return await asyncio.to_thread(_record)

    def cleanup_temp_file(self, file_path: str):
        """Delete temporary audio file"""
        if os.path.exists(file_path):
            os.unlink(file_path)
