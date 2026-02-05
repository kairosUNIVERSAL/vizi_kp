<template>
  <div class="mobile-container safe-area-pt">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">Прайс-лист</h1>
      <button 
        @click="openModal()" 
        class="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition"
      >
        <PhPlus :size="20" />
        <span class="hidden sm:inline">Добавить</span>
      </button>
    </div>

    <!-- Search & Filter -->
    <div class="bg-white p-4 rounded-xl shadow-sm mb-6 sticky top-0 z-10 border border-gray-100">
      <div class="relative">
        <PhMagnifyingGlass :size="20" class="absolute left-3 top-3 text-gray-400" />
        <input 
          v-model="searchQuery" 
          @input="handleSearch"
          type="text" 
          placeholder="Поиск по названию или синонимам..." 
          class="w-full pl-10 pr-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button 
          v-if="searchQuery"
          @click="clearSearch"
          class="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
        >
          <PhX :size="16" />
        </button>
      </div>
      
      <!-- Categories Filter (Horizontal Scroll) -->
      <div class="flex gap-2 mt-3 overflow-x-auto pb-1 hide-scrollbar">
        <button 
          @click="activeCategory = null"
          :class="[
            'px-3 py-1 rounded-full text-sm whitespace-nowrap transition-colors',
            activeCategory === null ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          Все
        </button>
        <button 
          v-for="cat in priceStore.categories" 
          :key="cat.id"
          @click="activeCategory = cat.id"
          :class="[
            'px-3 py-1 rounded-full text-sm whitespace-nowrap transition-colors',
            activeCategory === cat.id ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          {{ cat.name }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin text-4xl mb-2">⌛</div>
      <p class="text-gray-500">Загрузка...</p>
    </div>

    <!-- Items List -->
    <div v-else class="space-y-4 pb-20">
      <div 
        v-for="item in filteredItems" 
        :key="item.id" 
        class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex justify-between items-start"
      >
        <div class="flex-1 min-w-0 pr-4">
          <div class="flex items-center gap-2 mb-1">
            <span class="font-semibold text-lg truncate">{{ item.name }}</span>
            <span v-if="!item.is_active" class="bg-red-100 text-red-600 text-xs px-2 py-0.5 rounded-full">Скрыт</span>
          </div>
          
          <p class="text-sm text-gray-500 mb-2">{{ item.category?.name || 'Без категории' }}</p>
          
          <div class="flex items-center gap-4 text-sm">
             <span class="font-medium bg-blue-50 text-blue-700 px-2 py-1 rounded-md">
               {{ formatPrice(item.price) }} ₽ / {{ item.unit }}
             </span>
          </div>
          
          <p v-if="item.synonyms" class="text-xs text-gray-400 mt-2 truncate">
            🔍 {{ item.synonyms }}
          </p>
        </div>

        <!-- Actions -->
        <div class="flex flex-col gap-2">
          <button 
            @click="openModal(item)" 
            class="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          >
            <PhPencilSimple :size="20" />
          </button>
          <button 
            @click="confirmDelete(item)" 
            class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <PhTrash :size="20" />
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredItems.length === 0" class="text-center py-12 bg-gray-50 rounded-xl">
        <p class="text-gray-500">Ничего не найдено</p>
        <button @click="openModal()" class="text-blue-600 font-medium mt-2 hover:underline">Добавить новую позицию?</button>
      </div>
    </div>

    <!-- Modal -->
    <PriceItemModal 
      :is-open="showModal"
      :item="editingItem"
      :categories="priceStore.categories"
      @close="closeModal"
      @saved="refreshData"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePriceStore } from '@/stores/price'
import { PhPlus, PhMagnifyingGlass, PhX, PhPencilSimple, PhTrash } from '@phosphor-icons/vue'
import PriceItemModal from './PriceItemModal.vue'
import { debounce } from 'lodash'

const priceStore = usePriceStore()
const loading = ref(true)
const searchQuery = ref('')
const activeCategory = ref(null)

// Modal state
const showModal = ref(false)
const editingItem = ref(null)

onMounted(async () => {
  await loadData()
})

const loadData = async () => {
    loading.value = true
    try {
        await priceStore.fetchCategories()
        await priceStore.fetchItems()
    } finally {
        loading.value = false
    }
}

const handleSearch = debounce(async () => {
   // Local filtering is enough for small datasets, but store supports search
   // For now, let's just filter locally since we fetched all items
}, 300)

const clearSearch = () => {
    searchQuery.value = ''
}

const filteredItems = computed(() => {
    let items = priceStore.items
    
    if (activeCategory.value) {
        items = items.filter(i => i.category_id === activeCategory.value)
    }
    
    if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase()
        items = items.filter(i => 
            i.name.toLowerCase().includes(q) || 
            (i.synonyms && i.synonyms.toLowerCase().includes(q))
        )
    }
    
    return items
})

const openModal = (item = null) => {
    editingItem.value = item
    showModal.value = true
}

const closeModal = () => {
    showModal.value = false
    editingItem.value = null
}

const refreshData = async () => {
    await priceStore.fetchItems()
}

const confirmDelete = async (item) => {
    if (confirm(`Вы уверены, что хотите удалить "${item.name}"?`)) {
        try {
            await priceStore.deleteItem(item.id)
            await refreshData()
        } catch (e) {
            alert('Ошибка удаления: ' + (e.message || 'Неизвестная ошибка'))
        }
    }
}

const formatPrice = (val) => new Intl.NumberFormat('ru-RU').format(val || 0)
</script>
