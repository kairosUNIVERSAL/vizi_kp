<template>
  <div class="voice-recorder space-y-4">
    <!-- Instructions -->
    <div class="bg-blue-50 border border-blue-200 rounded-xl p-3 md:p-4">
      <div class="flex items-start gap-2">
        <span class="text-lg">💡</span>
        <div class="text-sm">
          <p class="font-medium text-blue-800">Как диктовать:</p>
          <p class="text-blue-700 mt-1">
            Короткими фразами (1-2 предложения)
          </p>
          <p class="text-blue-600 italic mt-1 text-xs">
            "Гостиная 24 квадрата, еврокраб 22 метра..."
          </p>
        </div>
      </div>
    </div>
    
    <!-- Recording Button -->
    <div class="flex justify-center py-4">
      <button
        @click="toggleRecording"
        :disabled="isTranscribing"
        :class="[
          'voice-btn touch-target',
          isRecording ? 'recording' : 'idle'
        ]"
      >
        <span v-if="isTranscribing" class="animate-spin">⏳</span>
        <span v-else-if="isRecording">⏹️</span>
        <span v-else>🎤</span>
      </button>
    </div>
    
    <!-- Recording Status -->
    <p class="text-center text-sm font-medium" :class="statusClass">
      <span v-if="isTranscribing" class="inline-flex items-center gap-2">
        <span class="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
        Распознавание... (Gemini AI)
      </span>
      <span v-else-if="isRecording" class="inline-flex items-center gap-2">
        <span class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
        Запись... {{ recordingTime }}с
      </span>
      <span v-else>
        Нажмите для записи
      </span>
    </p>
    
    <!-- Error Message -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl p-3">
      <p class="text-red-700 text-sm text-center">{{ error }}</p>
    </div>
    
    <!-- Transcript Area -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Распознанный текст:
      </label>
      <textarea
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        rows="4"
        class="input"
        placeholder="Текст появится здесь после записи..."
      ></textarea>
    </div>
    
    <!-- Clear Button -->
    <div class="flex justify-start">
      <button
        @click="clearAll"
        :disabled="!modelValue"
        class="btn btn-secondary text-sm"
      >
        🗑️ Очистить
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import transcribeService from '@/services/transcribeService'

const props = defineProps({
  modelValue: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

// State
const isRecording = ref(false)
const isTranscribing = ref(false)
const error = ref(null)
const recordingTime = ref(0)

// MediaRecorder
let mediaRecorder = null
let audioChunks = []
let recordingTimer = null

const statusClass = computed(() => {
  if (isTranscribing.value) return 'text-blue-500'
  if (isRecording.value) return 'text-red-500'
  return 'text-gray-500'
})

const startRecording = async () => {
  error.value = null
  audioChunks = []
  recordingTime.value = 0
  
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    
    mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'
    })
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }
    
    mediaRecorder.onstop = async () => {
      // Stop all tracks
      stream.getTracks().forEach(track => track.stop())
      
      // Create blob and transcribe
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
      await transcribeAudio(audioBlob)
    }
    
    mediaRecorder.start()
    isRecording.value = true
    
    // Recording timer
    recordingTimer = setInterval(() => {
      recordingTime.value++
      // Auto-stop after 60 seconds
      if (recordingTime.value >= 60) {
        stopRecording()
      }
    }, 1000)
    
  } catch (err) {
    error.value = getErrorMessage(err)
  }
}

const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
  isRecording.value = false
  
  if (recordingTimer) {
    clearInterval(recordingTimer)
    recordingTimer = null
  }
}

const transcribeAudio = async (audioBlob) => {
  isTranscribing.value = true
  error.value = null
  
  try {
    const transcript = await transcribeService.transcribe(audioBlob)
    
    if (transcript) {
      const current = props.modelValue || ''
      const newValue = current ? current + ' ' + transcript : transcript
      emit('update:modelValue', newValue)
    }
  } catch (err) {
    error.value = `Ошибка распознавания: ${err.response?.data?.detail || err.message}`
  } finally {
    isTranscribing.value = false
  }
}

const toggleRecording = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const clearAll = () => {
  emit('update:modelValue', '')
  error.value = null
}

const getErrorMessage = (err) => {
  if (err.name === 'NotAllowedError') {
    return 'Доступ к микрофону запрещён'
  }
  if (err.name === 'NotFoundError') {
    return 'Микрофон не найден'
  }
  return `Ошибка: ${err.message}`
}

onUnmounted(() => {
  if (recordingTimer) {
    clearInterval(recordingTimer)
  }
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
})
</script>

