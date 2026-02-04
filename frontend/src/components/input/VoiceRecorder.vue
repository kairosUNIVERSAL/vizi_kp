<template>
  <div class="voice-recorder space-y-4">
    <!-- Instructions (Collapsible on Mobile) -->
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
    
    <!-- Recording Button (Large Touch Target) -->
    <div class="flex justify-center py-4">
      <button
        @click="toggleRecording"
        :disabled="!isSupported"
        :class="[
          'voice-btn touch-target',
          isListening ? 'recording' : 'idle'
        ]"
      >
        <span v-if="isListening">⏹️</span>
        <span v-else>🎤</span>
      </button>
    </div>
    
    <!-- Recording Status -->
    <p class="text-center text-sm font-medium" :class="isListening ? 'text-red-500' : 'text-gray-500'">
      <span v-if="isListening" class="inline-flex items-center gap-2">
        <span class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
        Запись...
      </span>
      <span v-else-if="!isSupported" class="text-yellow-600">
        Браузер не поддерживает голосовой ввод
      </span>
      <span v-else>
        Нажмите для записи
      </span>
    </p>
    
    <!-- Error Message -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl p-3">
      <p class="text-red-700 text-sm text-center">{{ getErrorMessage(error) }}</p>
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
import { watch } from 'vue'
import { useSpeechRecognition } from '@/composables/useSpeechRecognition'

const props = defineProps({
  modelValue: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

const { 
  isSupported, 
  isListening, 
  transcript: internalTranscript, 
  error, 
  startListening, 
  stopListening, 
  clearTranscript 
} = useSpeechRecognition()

// Sync internal transcript to parent
watch(internalTranscript, (val) => {
  if (val) {
    const current = props.modelValue || ''
    const newValue = current ? current + ' ' + val : val
    emit('update:modelValue', newValue)
    clearTranscript()
  }
})

const toggleRecording = () => {
  if (isListening.value) {
    stopListening()
  } else {
    startListening()
  }
}

const clearAll = () => {
  emit('update:modelValue', '')
  clearTranscript()
}

const getErrorMessage = (err) => {
  const messages = {
    'not-allowed': 'Доступ к микрофону запрещён',
    'no-speech': 'Речь не обнаружена',
    'network': 'Ошибка сети',
    'aborted': 'Запись отменена'
  }
  return messages[err] || `Ошибка: ${err}`
}
</script>
