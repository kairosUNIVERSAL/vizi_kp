import api from './api'

/**
 * Service for server-side audio transcription using Gemini Flash
 */
export const transcribeService = {
    /**
     * Transcribe audio blob using server-side AI (Gemini Flash via OpenRouter)
     * @param {Blob} audioBlob - Audio blob from MediaRecorder
     * @returns {Promise<string>} Transcribed text
     */
    async transcribe(audioBlob) {
        const formData = new FormData()
        formData.append('audio', audioBlob, 'recording.webm')

        const response = await api.post('/transcribe', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            },
            timeout: 120000 // 2 minutes for long recordings
        })

        return response.data.transcript
    }
}

export default transcribeService
