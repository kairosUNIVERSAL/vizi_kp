<template>
  <div class="space-y-4 md:space-y-6">
    <h2 class="text-lg md:text-xl font-bold">Данные клиента</h2>
    
    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Имя клиента <span class="text-red-500">*</span>
        </label>
        <input 
          v-model="clientInfo.client_name" 
          type="text" 
          class="input input-lg" 
          placeholder="Иван Петров"
          autocomplete="name"
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Телефон</label>
        <input 
          v-model="clientInfo.client_phone" 
          type="tel" 
          class="input input-lg" 
          placeholder="+7 999 123 45 67"
          autocomplete="tel"
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Адрес объекта</label>
        <input 
          v-model="clientInfo.client_address" 
          type="text" 
          class="input input-lg" 
          placeholder="г. Москва, ул. ..."
          autocomplete="street-address"
        />
      </div>
    </div>
    
    <!-- Next Button (Full Width on Mobile) -->
    <div class="pt-4">
      <button 
        @click="$emit('next')" 
        class="btn btn-primary btn-lg w-full sm:w-auto sm:float-right"
        :disabled="!clientInfo.client_name"
      >
        Далее →
      </button>
    </div>
  </div>
</template>

<script setup>
import { useEstimateStore } from '@/stores/estimate'
import { toRefs } from 'vue'

const estimateStore = useEstimateStore()
const { clientInfo } = toRefs(estimateStore)

defineEmits(['next'])
</script>
