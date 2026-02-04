import base64
import httpx
import tempfile
import os
import subprocess
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
        Automatically converts input audio to MP3 using ffmpeg for compatibility.
        """
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured")
        
        # Convert to MP3 using ffmpeg
        try:
            mp3_data = self._convert_to_mp3(audio_data)
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            raise ValueError(f"Failed to process audio file: {e}")

        # Encode MP3 to Base64
        audio_base64 = base64.b64encode(mp3_data).decode('utf-8')
        
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
                            "text": "Транскрибируй это аудио на русском языке. Верни ТОЛЬКО текст транскрипции, ничего больше. Не добавляй никаких комментариев или пояснений."
                        },
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": audio_base64,
                                "format": "mp3"
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
            
            if response.status_code != 200:
                error_body = response.text
                logger.error(f"OpenRouter API Error ({response.status_code}): {error_body}")
                raise ValueError(f"Transcription failed: Provider returned {response.status_code}")

            data = response.json()
            
            # Check for generic error structure
            if "error" in data:
                 raise ValueError(f"API Error: {data['error'].get('message', 'Unknown error')}")

            try:
                transcript = data["choices"][0]["message"]["content"]
                logger.info(f"Transcribed audio: {transcript[:100]}...")
                return transcript.strip()
            except (KeyError, IndexError) as e:
                 logger.error(f"Unexpected API response format: {data}")
                 raise ValueError("Invalid response from transcription service")

    def _convert_to_mp3(self, input_data: bytes) -> bytes:
        """Convert input audio bytes to MP3 using ffmpeg"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".input") as tmp_in:
            tmp_in.write(input_data)
            tmp_in_path = tmp_in.name
            
        tmp_out_path = tmp_in_path + ".mp3"
        
        try:
            # ffmpeg command: input -> convert to mp3 -> output
            # -y: overwrite output
            # -vn: disable video
            # -ac: 1 (mono)
            # -ar: 16000 (sample rate)
            process = subprocess.run(
                [
                    "ffmpeg", "-y", 
                    "-i", tmp_in_path,
                    "-vn", "-ac", "1", "-ar", "16000",
                    "-f", "mp3", 
                    tmp_out_path
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            
            with open(tmp_out_path, "rb") as f:
                return f.read()
                
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg error: {e.stderr.decode()}")
            raise Exception("FFmpeg conversion failed")
        finally:
            # Cleanup temp files
            if os.path.exists(tmp_in_path):
                os.unlink(tmp_in_path)
            if os.path.exists(tmp_out_path):
                os.unlink(tmp_out_path)
