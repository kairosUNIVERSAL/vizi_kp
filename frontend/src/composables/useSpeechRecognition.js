import { ref, onMounted, onUnmounted } from 'vue'

export function useSpeechRecognition() {
    const isSupported = ref(false)
    const isListening = ref(false)
    const transcript = ref('')
    const error = ref(null)

    let recognition = null

    onMounted(() => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

        if (SpeechRecognition) {
            isSupported.value = true
            recognition = new SpeechRecognition()
            recognition.lang = 'ru-RU'
            recognition.continuous = false
            recognition.interimResults = false

            recognition.onresult = (event) => {
                const result = event.results[event.results.length - 1]
                if (result.isFinal) {
                    const text = result[0].transcript
                    transcript.value = transcript.value
                        ? transcript.value + ' ' + text
                        : text
                }
            }

            recognition.onerror = (event) => {
                console.error("Speech recognition error", event.error)
                error.value = event.error
                isListening.value = false
            }

            recognition.onend = () => {
                isListening.value = false
            }
        }
    })

    onUnmounted(() => {
        if (recognition) {
            recognition.abort()
        }
    })

    const startListening = () => {
        if (recognition && !isListening.value) {
            error.value = null
            try {
                recognition.start()
                isListening.value = true
            } catch (e) {
                console.error("Failed to start", e)
            }
        }
    }

    const stopListening = () => {
        if (recognition && isListening.value) {
            recognition.stop()
            isListening.value = false
        }
    }

    const clearTranscript = () => {
        transcript.value = ''
    }

    return {
        isSupported,
        isListening,
        transcript,
        error,
        startListening,
        stopListening,
        clearTranscript
    }
}
