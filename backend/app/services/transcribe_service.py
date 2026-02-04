import base64
import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class TranscribeService:
    """Service for transcribing audio using Gemini Flash via OpenRouter"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_TRANSCRIBE_MODEL
    
    async def transcribe_audio(self, audio_data: bytes, mime_type: str = "audio/webm") -> str:
        """
        Transcribe audio using Gemini Flash model via OpenRouter.
        
        Args:
            audio_data: Raw audio bytes
            mime_type: MIME type of the audio (e.g., "audio/webm", "audio/mp3")
        
        Returns:
            Transcribed text
        """
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured")
        
        # Encode audio to Base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Determine format from mime_type
        # Note: webm is not directly supported, try as ogg (both use opus codec)
        format_map = {
            "audio/mp4": "m4a",
            "audio/ogg": "ogg",
            "audio/webm": "ogg",  # WebM with Opus -> try as OGG
            "audio/mp3": "mp3",
            "audio/mpeg": "mp3",
            "audio/wav": "wav",
            "audio/m4a": "m4a",
            "audio/flac": "flac",
            "audio/aac": "aac"
        }
        audio_format = format_map.get(mime_type, "ogg")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ceiling-kp.app",
            "X-Title": "Ceiling KP Generator"
        }
        
        # Correct OpenRouter multimodal format for audio
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Пожалуйста, транскрибируй это аудио на русском языке. Верни только текст транскрипции, без комментариев."
                        },
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": audio_base64,
                                "format": audio_format
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4096,
            "temperature": 0.1
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            transcript = data["choices"][0]["message"]["content"]
            logger.info(f"Transcribed audio: {transcript[:100]}...")
            return transcript.strip()


transcribe_service = TranscribeService()
