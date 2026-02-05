<template>
  <div v-if="isOpen" class="fixed inset-0 z-[60] flex items-center justify-center bg-black bg-opacity-50 px-4">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-5 relative max-h-[90vh] flex flex-col">
      <button @click="$emit('close')" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
        <PhX :size="20" />
      </button>

      <h2 class="text-xl font-bold mb-4">{{ title }}</h2>
      
      <div class="relative mb-4">
        <PhMagnifyingGlass :size="20" class="absolute left-3 top-3 text-gray-400" />
        <input 
          v-model="query"
          ref="searchInput"
          type="text"
          class="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Поиск по названию или синониму..."
          @input="onSearch"
        />
      </div>

      <div class="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
        <div 
          v-for="item in results" 
          :key="item.id"
          @click="$emit('select', item)"
          class="p-3 border rounded-xl hover:bg-blue-50 border-gray-100 hover:border-blue-200 cursor-pointer transition-all"
        >
          <div class="flex justify-between items-start">
            <div class="min-w-0 flex-1 pr-2">
              <div class="font-bold text-gray-900 truncate">{{ item.name }}</div>
              <div class="text-[10px] text-gray-400 mt-0.5">{{ item.category_name }}</div>
            </div>
            <div class="text-right">
              <div class="font-bold text-blue-600">{{ formatPrice(item.price) }} ₽</div>
              <div class="text-[10px] text-gray-400">{{ item.unit }}</div>
            </div>
          </div>
        </div>
        
        <div v-if="results.length === 0 && query.length >= 2" class="text-center py-10">
           <div class="text-3xl mb-2">🔍</div>
           <p class="text-gray-500">Ничего не найдено</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { PhX, PhMagnifyingGlass } from '@phosphor-icons/vue'
import { usePriceStore } from '@/stores/price'

const props = defineProps({
  isOpen: Boolean,
  title: {
    type: String,
    default: 'Поиск позиции'
  }
})

const emit = defineEmits(['close', 'select'])
const priceStore = usePriceStore()
const query = ref('')
const results = ref([])
const searchInput = ref(null)

const onSearch = () => {
    if (query.value.length < 2) {
        results.value = []
        return
    }
    
    const q = query.value.toLowerCase()
    results.value = priceStore.items.filter(item => {
        return item.is_active && (
            item.name.toLowerCase().includes(q) || 
            (item.synonyms && item.synonyms.toLowerCase().includes(q))
        )
    }).slice(0, 20)
}

watch(() => props.isOpen, (val) => {
    if (val) {
        query.value = ''
        results.value = []
        setTimeout(() => {
            searchInput.value?.focus()
        }, 100)
    }
})

const formatPrice = (val) => new Intl.NumberFormat('ru-RU').format(val || 0)
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #E5E7EB;
  border-radius: 10px;
}
</style>
