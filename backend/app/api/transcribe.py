from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.transcribe_service import transcribe_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file to transcribe (webm, mp3, wav)")
):
    """
    Transcribe audio file to text using Gemini Flash via OpenRouter.
    
    Accepts audio files in common formats (webm, mp3, wav, ogg).
    Returns the transcribed text.
    """
    # Validate file type (flexible check for audio/*)
    content_type = audio.content_type or "audio/webm"
    
    if not content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: {content_type}. Please upload an audio file."
        )
    
    try:
        # Read audio data
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty audio file"
            )
        
        # Limit file size (10MB)
        max_size = 10 * 1024 * 1024
        if len(audio_data) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Audio file too large. Max size: {max_size // (1024*1024)}MB"
            )
        
        # Transcribe
        transcript = await transcribe_service.transcribe_audio(audio_data, content_type)
        
        return {
            "success": True,
            "transcript": transcript
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )
