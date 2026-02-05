<template>
  <div class="mobile-container safe-area-pt">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <router-link 
          :to="{name: 'dashboard'}" 
          class="text-blue-600 hover:text-blue-800 text-sm mb-2 inline-flex items-center gap-1"
        >
          <PhCaretLeft :size="16" /> Назад к списку
        </router-link>
        <h1 class="text-2xl font-bold">Смета #{{ estimateId }}</h1>
      </div>
      <div class="flex gap-2">
        <button 
          @click="downloadPdf"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition"
        >
          <PhFilePdf :size="20" />
          <span class="hidden sm:inline">PDF</span>
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin text-4xl mb-2">⌛</div>
      <p class="text-gray-500">Загрузка...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-12 bg-red-50 rounded-xl">
      <p class="text-red-600">{{ error }}</p>
      <router-link :to="{name: 'dashboard'}" class="text-blue-600 mt-2 inline-block">
        Вернуться на главную
      </router-link>
    </div>

    <!-- Content -->
    <div v-else-if="estimate" class="space-y-6">
      <!-- Client Info Card -->
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h2 class="font-bold text-lg mb-4">Информация о клиенте</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <span class="text-sm text-gray-500">Клиент</span>
            <p class="font-medium">{{ estimate.client_name }}</p>
          </div>
          <div>
            <span class="text-sm text-gray-500">Телефон</span>
            <p class="font-medium">{{ estimate.client_phone || '—' }}</p>
          </div>
          <div>
            <span class="text-sm text-gray-500">Адрес</span>
            <p class="font-medium">{{ estimate.client_address || '—' }}</p>
          </div>
        </div>
      </div>

      <!-- Rooms -->
      <div 
        v-for="room in estimate.rooms" 
        :key="room.id" 
        class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden"
      >
        <div class="bg-gray-50 px-6 py-4 flex justify-between items-center">
          <div class="flex items-center gap-2">
            <span class="text-lg">🏠</span>
            <h3 class="font-bold">{{ room.name }}</h3>
            <span v-if="room.area" class="text-sm text-gray-500">({{ room.area }} м²)</span>
          </div>
          <span class="font-bold text-blue-600">{{ formatPrice(room.subtotal) }} ₽</span>
        </div>
        
        <table class="w-full">
          <thead class="text-xs text-gray-500 uppercase bg-gray-50">
            <tr>
              <th class="px-6 py-2 text-left">Позиция</th>
              <th class="px-6 py-2 text-center">Кол-во</th>
              <th class="px-6 py-2 text-right">Цена</th>
              <th class="px-6 py-2 text-right">Сумма</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="item in room.items" :key="item.id">
              <td class="px-6 py-3">{{ item.name }}</td>
              <td class="px-6 py-3 text-center text-gray-600">{{ item.quantity }} {{ item.unit }}</td>
              <td class="px-6 py-3 text-right text-gray-600">{{ formatPrice(item.price) }} ₽</td>
              <td class="px-6 py-3 text-right font-medium">{{ formatPrice(item.sum) }} ₽</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Total -->
      <div class="bg-blue-50 p-6 rounded-xl border border-blue-200 flex justify-between items-center">
        <div>
          <span class="text-sm text-blue-600">Общая площадь: {{ estimate.total_area }} м²</span>
        </div>
        <div class="text-right">
          <span class="text-sm text-gray-500">Итого:</span>
          <p class="text-2xl font-bold text-blue-700">{{ formatPrice(estimate.total_sum) }} ₽</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { PhCaretLeft, PhFilePdf } from '@phosphor-icons/vue'
import api from '@/services/api'

const route = useRoute()
const estimateId = route.params.id

const estimate = ref(null)
const loading = ref(true)
const error = ref(null)

const formatPrice = (val) => new Intl.NumberFormat('ru-RU').format(val || 0)

const loadEstimate = async () => {
  loading.value = true
  error.value = null
  try {
    const { data } = await api.get(`/estimates/${estimateId}`)
    estimate.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Смета не найдена'
  } finally {
    loading.value = false
  }
}

const downloadPdf = async () => {
  try {
    const { data } = await api.post('/pdf/generate', {
      estimate_id: Number(estimateId)
    }, { responseType: 'blob' })
    
    const url = window.URL.createObjectURL(new Blob([data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `estimate_${estimateId}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (e) {
    alert('Ошибка генерации PDF: ' + (e.message || 'Неизвестная ошибка'))
  }
}

onMounted(loadEstimate)
</script>
