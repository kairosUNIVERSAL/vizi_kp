<template>
  <div class="space-y-4 md:space-y-6">
    <!-- Header with mode toggle -->
    <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
      <h2 class="text-lg md:text-xl font-bold">Замер</h2>
      
      <!-- Mode Toggle Pills -->
      <div class="flex bg-gray-100 rounded-xl p-1 w-full sm:w-auto">
        <button 
          @click="mode = 'voice'" 
          :class="[
            'flex-1 sm:flex-none px-4 py-2 rounded-lg text-sm font-medium transition-all',
            mode === 'voice' 
              ? 'bg-white text-blue-700 shadow-sm' 
              : 'text-gray-500'
          ]"
        >
          🎤 Голос
        </button>
        <button 
          @click="mode = 'manual'" 
          :class="[
            'flex-1 sm:flex-none px-4 py-2 rounded-lg text-sm font-medium transition-all',
            mode === 'manual' 
              ? 'bg-white text-blue-700 shadow-sm' 
              : 'text-gray-500'
          ]"
        >
          ⌨️ Текст
        </button>
      </div>
    </div>
    
    <!-- Voice Input Mode -->
    <div v-show="mode === 'voice'" class="space-y-4">
      <VoiceRecorder v-model="transcript" />
      
      <div v-if="transcript" class="flex justify-end">
        <button 
          @click="processTranscript" 
          class="btn btn-primary btn-lg w-full sm:w-auto flex items-center justify-center gap-2"
          :disabled="processing"
        >
          <span v-if="processing" class="animate-spin">⌛</span>
          <span v-else>✨</span>
          Распознать
        </button>
      </div>
    </div>
    
    <!-- Manual Input Mode -->
    <div v-show="mode === 'manual'" class="space-y-4">
      <!-- Text Parsing Block -->
      <div class="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-2xl p-4">
        <label class="block text-sm font-medium text-green-800 mb-2">
          📝 Вставьте или введите текст:
        </label>
        <textarea
          v-model="manualText"
          rows="4"
          class="input input-lg"
          placeholder="Гостиная 24 квадрата, еврокраб 22 метра..."
        ></textarea>
        <div class="flex justify-end mt-3">
          <button 
            @click="processManualText" 
            class="btn btn-success w-full sm:w-auto flex items-center justify-center gap-2"
            :disabled="!manualText || processing"
          >
            <span v-if="processing" class="animate-spin">⌛</span>
            <span v-else>🔍</span>
            Распознать
          </button>
        </div>
      </div>
      
      <div class="text-center text-gray-400 text-sm py-2">— или —</div>
      
      <!-- Item Search -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          🔎 Найти позицию в прайсе:
        </label>
        <ItemAutocomplete />
      </div>
    </div>

    <!-- Added Items Summary -->
    <div class="border-t pt-4 md:pt-6">
      <h3 class="font-bold text-gray-700 mb-3 flex items-center justify-between">
        <span>Добавленные позиции</span>
        <span class="text-sm font-normal bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
          {{ estimateStore.rooms.length }} комнат
        </span>
      </h3>
      
      <!-- Empty State -->
      <div v-if="estimateStore.rooms.length === 0" class="text-center py-8 bg-gray-50 rounded-xl">
        <div class="text-4xl mb-2">📋</div>
        <p class="text-gray-400">Пока ничего нет</p>
        <p class="text-gray-400 text-sm">Надиктуйте или добавьте вручную</p>
      </div>
      
      <!-- Rooms List (Mobile Optimized) -->
      <div v-else class="space-y-4">
        <div 
          v-for="(room, idx) in estimateStore.rooms" 
          :key="idx" 
          class="bg-gray-50 rounded-xl overflow-hidden"
        >
          <!-- Room Headers and Items -->
          <div 
            class="flex justify-between items-center p-3 bg-gray-100 cursor-pointer touch-manipulation group"
            @click.self="toggleRoom(idx)"
          >
            <div class="flex items-center gap-2" @click="toggleRoom(idx)">
               <h4 class="font-bold flex items-center gap-2">
                 <span class="text-lg">🏠</span>
                 {{ room.name }}
               </h4>
            </div>
            
            <div class="flex items-center gap-3">
              <span class="text-sm font-bold text-blue-600" @click="toggleRoom(idx)">
                {{ formatPrice(room.subtotal) }} ₽
              </span>
              <button 
                @click.stop="removeRoom(idx)" 
                class="p-1 text-gray-400 hover:text-red-500 transition-colors z-10"
                title="Удалить комнату"
              >
                  <PhTrash :size="18" />
              </button>
              <span class="text-gray-400 transition-transform" :class="{ 'rotate-180': expandedRooms.has(idx) }" @click="toggleRoom(idx)">
                ▼
              </span>
            </div>
          </div>
          
          <!-- Room Items (Collapsible on Mobile) -->
          <div v-show="expandedRooms.has(idx)" class="p-3">
            <div 
              v-for="(item, i_idx) in room.items" 
              :key="i_idx" 
              class="flex justify-between items-center py-2 border-b border-gray-100 last:border-0"
            >
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium truncate">{{ item.name }}</p>
                <p class="text-xs text-gray-500">
                  {{ Number(item.quantity) }} {{ item.unit }} × {{ formatPrice(item.price) }}
                </p>
              </div>
              <div class="flex items-center gap-3 ml-3">
                  <p class="text-sm font-bold">
                    {{ formatPrice(item.price * item.quantity) }} ₽
                  </p>
                  <button 
                    @click="removeItem(idx, i_idx)"
                    class="text-gray-300 hover:text-red-500"
                  >
                    <PhX :size="16" />
                  </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Navigation Buttons (Fixed on Mobile) -->
    <div class="flex flex-col sm:flex-row justify-between gap-3 pt-4 border-t">
      <button @click="$emit('prev')" class="btn btn-secondary order-2 sm:order-1">
        ← Назад
      </button>
      <button 
        @click="$emit('next')" 
        class="btn btn-primary btn-lg order-1 sm:order-2" 
        :disabled="estimateStore.rooms.length === 0"
      >
        Далее →
      </button>
    </div>

    <!-- Unknown Items Modal / Notification -->
    <div v-if="unknownItems.length > 0" class="fixed bottom-20 right-4 left-4 md:left-auto md:w-96 z-40">
      <div class="bg-yellow-50 border border-yellow-200 rounded-xl shadow-lg p-4 animate-slide-up">
        <div class="flex justify-between items-start mb-2">
           <h3 class="font-bold text-yellow-800 flex items-center gap-2">
             <span>⚠️</span> Ненайденные позиции ({{ unknownItems.length }})
           </h3>
           <button @click="clearUnknown" class="text-yellow-600 hover:text-yellow-800"><PhX /></button>
        </div>
        <p class="text-xs text-yellow-700 mb-3">
          AI не нашел эти товары в базе. Добавьте их, чтобы использовать в смете.
        </p>
        <div class="space-y-2 max-h-48 overflow-y-auto">
          <div 
            v-for="(item, idx) in unknownItems" 
            :key="idx" 
            class="bg-white p-2 rounded border border-yellow-100 flex justify-between items-center text-sm"
          >
            <span class="truncate font-medium">{{ item.original_text || item.name }}</span>
            <button 
              @click="addUnknownToDb(item)"
              class="text-blue-600 hover:text-blue-800 text-xs font-bold px-2 py-1 bg-blue-50 rounded"
            >
              + В базу
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Price Item Modal -->
    <PriceItemModal 
      :is-open="showModal"
      :item="newItem"
      :categories="priceStore.categories"
      @close="showModal = false"
      @saved="onItemSaved"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useEstimateStore } from '@/stores/estimate'
import { usePriceStore } from '@/stores/price'
import { PhTrash, PhX } from '@phosphor-icons/vue'
import VoiceRecorder from '@/components/input/VoiceRecorder.vue'
import ItemAutocomplete from '@/components/input/ItemAutocomplete.vue'
import PriceItemModal from '@/views/price/PriceItemModal.vue'

const mode = ref('voice')
const transcript = ref('')
const manualText = ref('')
const processing = ref(false)
const expandedRooms = reactive(new Set([0])) // First room expanded by default
const estimateStore = useEstimateStore()
const priceStore = usePriceStore()

// Unknown items handling
const unknownItems = ref([])
const showModal = ref(false)
const newItem = ref(null)

// Watch for store changes to detect unknown items in parse result
// Since estimateStore.parseTranscript returns the result, we can capture it there
// But we need to update processTranscript/processManualText

const removeItem = (rIdx, iIdx) => {
    estimateStore.rooms[rIdx].items.splice(iIdx, 1)
    estimateStore.recalculate()
}

const removeRoom = (rIdx) => {
    if (confirm('Удалить эту комнату и все позиции в ней?')) {
        estimateStore.rooms.splice(rIdx, 1)
        expandedRooms.delete(rIdx) // Cleanup expansion state
        estimateStore.recalculate()
    }
}

const toggleRoom = (idx) => {
  if (expandedRooms.has(idx)) {
    expandedRooms.delete(idx)
  } else {
    expandedRooms.add(idx)
  }
}

const handleParseResult = (result) => {
    console.log("Parse result:", result)
    if (result.unknown_items && result.unknown_items.length > 0) {
        // Merge with existing
        unknownItems.value = [...unknownItems.value, ...result.unknown_items]
    }
}

const processTranscript = async () => {
  if (!transcript.value) return
  
  processing.value = true
  try {
    const result = await estimateStore.parseTranscript(transcript.value)
    handleParseResult(result)
    transcript.value = ''
  } catch (e) {
    alert('Ошибка распознавания: ' + e.message)
  } finally {
    processing.value = false
  }
}

const processManualText = async () => {
  if (!manualText.value) return
  
  processing.value = true
  try {
    const result = await estimateStore.parseTranscript(manualText.value)
    handleParseResult(result)
    manualText.value = ''
  } catch (e) {
    alert('Ошибка распознавания: ' + e.message)
  } finally {
    processing.value = false
  }
}

const clearUnknown = () => {
    unknownItems.value = []
}

const addUnknownToDb = (item) => {
    // Pre-fill modal
    newItem.value = {
        name: item.original_text || item.name,
        synonyms: item.original_text || item.name, // Good for future matching
        price: 0,
        unit: 'шт',
        is_active: true
    }
    showModal.value = true
}

const onItemSaved = async () => {
    // Refresh items
    await priceStore.fetchItems()
    
    // Remove from unknown list (by name estimation)
    if (newItem.value && newItem.value.name) {
        unknownItems.value = unknownItems.value.filter(i => {
           const text = i.original_text || i.name
           return text !== newItem.value.name && text !== newItem.value.synonyms
        })
    }
    
    // Optionally: auto-add to last room? Or let user re-scan?
    // Let's suggest user re-scan or manually add for now to avoid complexity.
    alert('Позиция добавлена в базу! Теперь вы можете добавить её в смету.')
}

// Initial load needed for categories
priceStore.fetchCategories()

const formatPrice = (val) => new Intl.NumberFormat('ru-RU').format(val || 0)

defineEmits(['next', 'prev'])
</script>

<style scoped>
.animate-slide-up {
  animation: slideUp 0.3s ease-out;
}
@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
</style>
