<template>
  <div class="space-y-4 md:space-y-6">
    <!-- Success Header -->
    <div class="text-center py-4 md:py-6">
      <div class="text-5xl md:text-6xl mb-3">✅</div>
      <h2 class="text-xl md:text-2xl font-bold mb-1">Смета создана!</h2>
      <p class="text-gray-500 text-sm">Заказ #{{ estimateStore.estimate?.id }}</p>
    </div>
    
    <!-- PDF Preview Section -->
    <div class="bg-white rounded-xl shadow-lg overflow-hidden -mx-4 md:mx-0">
      <div class="bg-gray-100 px-4 py-3 border-b flex justify-between items-center">
        <h3 class="font-semibold text-gray-700 text-sm md:text-base">Предпросмотр</h3>
        <button 
          @click="loadPreview" 
          class="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-lg active:bg-blue-200"
          :disabled="previewLoading"
        >
          {{ previewLoading ? '⌛' : '🔄' }}
        </button>
      </div>
      
      <!-- Loading State -->
      <div v-if="previewLoading" class="h-80 md:h-[500px] flex items-center justify-center bg-gray-50">
        <div class="text-center">
          <div class="animate-spin text-3xl mb-2">⌛</div>
          <p class="text-gray-500 text-sm">Генерация...</p>
        </div>
      </div>
      
      <!-- Error State -->
      <div v-else-if="previewError" class="h-64 flex items-center justify-center bg-red-50 p-4">
        <div class="text-center">
          <div class="text-3xl mb-2">⚠️</div>
          <p class="text-red-600 text-sm">{{ previewError }}</p>
          <button 
            @click="loadPreview" 
            class="mt-3 btn btn-secondary text-sm"
          >
            Попробовать снова
          </button>
        </div>
      </div>
      
      <!-- PDF Preview -->
      <iframe 
        v-else-if="previewUrl"
        :src="previewUrl" 
        class="w-full h-80 md:h-[500px] border-0"
      ></iframe>
      
      <!-- Empty State -->
      <div v-else class="h-64 flex items-center justify-center bg-gray-50">
        <p class="text-gray-400 text-sm">Загрузка предпросмотра...</p>
      </div>
    </div>
    
    <!-- Edit Hint -->
    <div class="bg-yellow-50 border border-yellow-200 rounded-xl p-3">
      <p class="text-yellow-800 text-sm flex items-start gap-2">
        <span>💡</span>
        <span>Для изменений нажмите "Редактировать"</span>
      </p>
    </div>
    
    <!-- Action Buttons (Stack on Mobile) -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <button 
        @click="$emit('prev')" 
        class="btn btn-secondary flex items-center justify-center gap-2 order-3 sm:order-1"
      >
        <PhArrowLeft :size="18" />
        Редактировать
      </button>
      
      <button 
        @click="downloadPdf" 
        class="btn btn-primary btn-lg flex items-center justify-center gap-2 order-1 sm:order-2"
        :disabled="downloadLoading"
      >
        <span v-if="downloadLoading" class="animate-spin">⌛</span>
        <PhDownload v-else :size="22" />
        Скачать PDF
      </button>
      
      <router-link 
        :to="{name: 'dashboard'}" 
        class="btn btn-secondary flex items-center justify-center gap-2 order-2 sm:order-3"
      >
        <PhHouse :size="18" />
        На главную
      </router-link>
    </div>
    
    <!-- Download Error -->
    <p v-if="downloadError" class="text-center text-red-500 text-sm">
      {{ downloadError }}
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { PhDownload, PhHouse, PhArrowLeft } from '@phosphor-icons/vue'
import { useEstimateStore } from '@/stores/estimate'
import pdfService from '@/services/pdfService'

const emit = defineEmits(['prev'])

const estimateStore = useEstimateStore()

const previewUrl = ref(null)
const previewLoading = ref(false)
const previewError = ref(null)
const downloadLoading = ref(false)
const downloadError = ref(null)

const loadPreview = async () => {
  if (!estimateStore.estimate?.id) return
  
  previewLoading.value = true
  previewError.value = null
  
  try {
    pdfService.revokePreviewUrl(previewUrl.value)
    const blob = await pdfService.previewPdf(estimateStore.estimate.id)
    previewUrl.value = pdfService.createPreviewUrl(blob)
  } catch (e) {
    console.error('Preview error:', e)
    previewError.value = 'Не удалось загрузить предпросмотр'
  } finally {
    previewLoading.value = false
  }
}

const downloadPdf = async () => {
  if (!estimateStore.estimate?.id) return
  
  downloadLoading.value = true
  downloadError.value = null
  
  try {
    const data = await pdfService.generatePdf(estimateStore.estimate.id)
    
    const url = window.URL.createObjectURL(new Blob([data], { type: 'application/pdf' }))
    const link = document.createElement('a')
    link.href = url
    
    const clientName = estimateStore.estimate.client_name?.replace(/[^a-zA-Zа-яА-Я0-9]/g, '_') || 'client'
    link.setAttribute('download', `KP_${estimateStore.estimate.id}_${clientName}.pdf`)
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Download error:', e)
    downloadError.value = 'Ошибка скачивания'
  } finally {
    downloadLoading.value = false
  }
}

onMounted(() => {
  loadPreview()
})

onUnmounted(() => {
  pdfService.revokePreviewUrl(previewUrl.value)
})
</script>
