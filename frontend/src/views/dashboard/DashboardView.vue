<template>
  <div class="p-8 max-w-7xl mx-auto space-y-8">
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold">Панель управления</h1>
      <div class="flex gap-4 items-center">
        <span class="text-gray-600 font-medium">{{ authStore.user?.email }}</span>
        <button @click="authStore.logout()" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
           <PhSignOut :size="20" />
           Выйти
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- New Estimate Card -->
        <router-link :to="{name: 'estimate-new'}" class="block group lg:col-span-2">
            <div class="h-full bg-blue-600 text-white p-8 rounded-xl shadow-lg hover:bg-blue-700 transition-all flex flex-col items-center justify-center text-center transform hover:-translate-y-1">
                <div class="text-5xl mb-4 group-hover:scale-110 transition-transform">
                   <PhPlusCircle :size="64" weight="fill" />
                </div>
                <h2 class="text-2xl font-bold mb-2">Новая смета</h2>
                <p class="text-blue-100 italic">Надиктуйте или введите вручную</p>
            </div>
        </router-link>
        
        <!-- Stats Card 1 -->
        <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-center">
             <div class="text-sm text-gray-500 mb-1">Всего смет</div>
             <div class="text-3xl font-bold text-gray-900">{{ estimateStore.estimates.length }}</div>
        </div>

        <!-- Stats Card 2 -->
        <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-center">
             <div class="text-sm text-gray-500 mb-1">Общая сумма</div>
             <div class="text-2xl font-bold text-blue-600">{{ formatPrice(totalStats.sum) }} ₽</div>
        </div>
    </div>

    <!-- Recent Estimates Table -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
        <h2 class="font-bold text-lg">История последних смет</h2>
      </div>

      <div v-if="loading" class="p-12 text-center text-gray-400">
        <div class="animate-spin inline-block mb-2">
           <PhCircleNotch :size="32" class="animate-spin" />
        </div>
        <div>Загрузка данных...</div>
      </div>

      <div v-else-if="estimateStore.estimates.length === 0" class="p-12 text-center space-y-4">
        <div class="text-gray-300">
          <PhFileText :size="64" class="mx-auto" />
        </div>
        <p class="text-gray-500">У вас пока нет созданных смет.</p>
        <router-link :to="{name: 'estimate-new'}" class="text-blue-600 font-medium hover:underline">
          Создать первую смету
        </router-link>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-gray-50 text-xs font-bold text-gray-500 uppercase tracking-wider">
            <tr>
              <th class="px-6 py-3">Дата</th>
              <th class="px-6 py-3">Клиент</th>
              <th class="px-6 py-3 text-right">Площадь</th>
              <th class="px-6 py-3 text-right">Сумма</th>
              <th class="px-6 py-3">Статус</th>
              <th class="px-6 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="est in estimateStore.estimates" :key="est.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 text-sm text-gray-600">
                {{ formatDate(est.created_at) }}
              </td>
              <td class="px-6 py-4">
                <div class="font-bold text-gray-900">{{ est.client_name }}</div>
                <div class="text-xs text-gray-500">{{ est.client_phone }}</div>
              </td>
              <td class="px-6 py-4 text-sm text-right">
                {{ est.total_area }} м²
              </td>
              <td class="px-6 py-4 text-right font-bold text-blue-600">
                {{ formatPrice(est.total_sum) }} ₽
              </td>
              <td class="px-6 py-4">
                <span :class="['px-2 py-1 rounded-full text-xs font-medium', getStatusClass(est.status)]">
                  {{ est.status }}
                </span>
              </td>
              <td class="px-6 py-4 text-right">
                <button class="text-gray-400 hover:text-blue-600 transition-colors">
                  <PhArrowRight :size="20" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useEstimateStore } from '@/stores/estimate'

const authStore = useAuthStore()
const estimateStore = useEstimateStore()
const loading = ref(false)

const totalStats = computed(() => {
  return estimateStore.estimates.reduce((acc, est) => {
    acc.sum += Number(est.total_sum)
    acc.area += Number(est.total_area)
    return acc
  }, { sum: 0, area: 0 })
})

const formatPrice = (val) => new Intl.NumberFormat('ru-RU').format(val)
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const getStatusClass = (status) => {
  const classes = {
    'draft': 'bg-gray-100 text-gray-600',
    'completed': 'bg-green-100 text-green-700',
    'sent': 'bg-blue-100 text-blue-700'
  }
  return classes[status] || 'bg-gray-100 text-gray-600'
}

onMounted(async () => {
  loading.value = true
  try {
    await estimateStore.fetchEstimates()
  } finally {
    loading.value = false
  }
})
</script>
