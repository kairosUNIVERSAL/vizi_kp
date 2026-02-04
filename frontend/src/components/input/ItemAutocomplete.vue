<template>
  <div class="item-autocomplete relative">
    <div class="relative">
      <input
        v-model="searchQuery"
        @input="onSearch"
        @focus="showDropdown = true"
        @keydown.down.prevent="navigateDown"
        @keydown.up.prevent="navigateUp"
        @keydown.enter.prevent="selectHighlighted"
        @keydown.escape="showDropdown = false"
        type="text"
        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
        placeholder="Начните вводить название позиции..."
      />
      <span class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
        🔍
      </span>
    </div>
    
    <div
      v-if="showDropdown && filteredItems.length > 0"
      class="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-64 overflow-y-auto"
    >
      <div
        v-for="(item, index) in filteredItems"
        :key="item.id"
        @click="selectItem(item)"
        @mouseenter="highlightedIndex = index"
        :class="[
          'px-4 py-3 cursor-pointer border-b border-gray-100 last:border-0',
          highlightedIndex === index ? 'bg-blue-50' : 'hover:bg-gray-50'
        ]"
      >
        <div class="flex justify-between items-start">
          <div>
            <div class="font-medium text-gray-900">{{ item.name }}</div>
            <div class="text-sm text-gray-500">{{ item.category_name }}</div>
          </div>
          <div class="text-right">
            <div class="font-medium text-gray-900">{{ formatPrice(item.price) }} ₽</div>
            <div class="text-sm text-gray-500">{{ item.unit }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- No results -->
    <div
      v-if="showDropdown && searchQuery.length >= 2 && filteredItems.length === 0 && !loading"
      class="absolute z-50 w-full mt-1 bg-yellow-50 border border-yellow-200 rounded-lg p-4"
    >
      <p class="text-yellow-800 text-sm">
        Позиция не найдена в прайсе. 
      </p>
    </div>
    
    <!-- Selected Item Preview & Config -->
    <div v-if="selectedItem" class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
      <div class="flex justify-between items-start mb-4">
        <div>
          <div class="font-medium">{{ selectedItem.name }}</div>
          <div class="text-sm text-gray-500">{{ selectedItem.category_name }}</div>
        </div>
        <button @click="clearSelection" class="text-gray-400 hover:text-gray-600">✕</button>
      </div>
      
      <div class="grid grid-cols-3 gap-4">
        <div>
          <label class="block text-sm text-gray-600 mb-1">Количество</label>
          <input
            v-model.number="quantity"
            type="number"
            min="0.1"
            step="0.1"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none"
          />
        </div>
        
        <div>
          <label class="block text-sm text-gray-600 mb-1">Ед. изм.</label>
          <input
            :value="selectedItem.unit"
            disabled
            class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-100 outline-none"
          />
        </div>
        
        <div>
          <label class="block text-sm text-gray-600 mb-1">Сумма</label>
          <input
            :value="formatPrice(selectedItem.price * quantity)"
            disabled
            class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-100 font-medium outline-none"
          />
        </div>
      </div>
      
      <div class="mt-4">
        <label class="block text-sm text-gray-600 mb-1">Комната</label>
        <select
          v-model="selectedRoom"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none"
        >
            <option value="" disabled>Выберите комнату</option>
            <option v-for="room in rooms" :key="room" :value="room">{{ room }}</option>
            <option value="__new__">+ Добавить комнату</option>
        </select>
        <input 
            v-if="selectedRoom === '__new__'"
            v-model="newRoomName"
            placeholder="Название комнаты"
            class="mt-2 w-full px-3 py-2 border border-gray-300 rounded-lg outline-none"
        />
      </div>
      
      <button
        @click="addToEstimate"
        :disabled="!quantity || (!selectedRoom && !newRoomName)"
        class="mt-4 w-full px-4 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
      >
        + Добавить в смету
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePriceStore } from '@/stores/price'
import { useEstimateStore } from '@/stores/estimate'

const priceStore = usePriceStore()
const estimateStore = useEstimateStore()

const searchQuery = ref('')
const showDropdown = ref(false)
const highlightedIndex = ref(0)
const selectedItem = ref(null)
const quantity = ref(1)
const selectedRoom = ref('')
const newRoomName = ref('')
const loading = ref(false)

const rooms = computed(() => estimateStore.rooms.map(r => r.name))

const filteredItems = computed(() => {
  if (searchQuery.value.length < 2) return []
  
  const query = searchQuery.value.toLowerCase()
  return priceStore.activeItems
    .filter(item => {
      const nameMatch = item.name.toLowerCase().includes(query)
      const synonymsMatch = item.synonyms?.toLowerCase().includes(query)
      return nameMatch || synonymsMatch
    })
    .slice(0, 10)
})

const onSearch = () => {
  highlightedIndex.value = 0
  showDropdown.value = true
}

const navigateDown = () => {
  if (highlightedIndex.value < filteredItems.value.length - 1) {
    highlightedIndex.value++
  }
}

const navigateUp = () => {
  if (highlightedIndex.value > 0) {
    highlightedIndex.value--
  }
}

const selectHighlighted = () => {
  if (filteredItems.value[highlightedIndex.value]) {
    selectItem(filteredItems.value[highlightedIndex.value])
  }
}

const selectItem = (item) => {
  selectedItem.value = item
  searchQuery.value = ''
  showDropdown.value = false
  quantity.value = 1
}

const clearSelection = () => {
  selectedItem.value = null
  quantity.value = 1
  selectedRoom.value = ''
  newRoomName.value = ''
}

const addToEstimate = () => {
  let roomName = selectedRoom.value
  if (roomName === '__new__') {
      roomName = newRoomName.value
  }
  
  if (!selectedItem.value || !quantity.value || !roomName) return
  
  estimateStore.addItem({
    room: roomName,
    price_item_id: selectedItem.value.id,
    name: selectedItem.value.name,
    unit: selectedItem.value.unit,
    quantity: quantity.value,
    price: selectedItem.value.price
  })
  
  clearSelection()
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(price)
}

const handleClickOutside = (event) => {
  if (!event.target.closest('.item-autocomplete')) {
    showDropdown.value = false
  }
}

onMounted(() => {
  if (priceStore.items.length === 0) {
      priceStore.fetchItems()
  }
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
