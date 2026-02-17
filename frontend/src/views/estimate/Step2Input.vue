<template>
  <div class="space-y-4 md:space-y-6 relative">
    <!-- Dark Overlay during recording OR processing -->
    <div 
        v-if="recordingRoomIdx !== -1 || processingRoomIdx !== -1" 
        class="fixed inset-0 bg-black/60 z-[50] transition-opacity duration-300"
        @click="recordingRoomIdx !== -1 ? stopRoomRecording() : null"
    ></div>
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
          :class="[
            'bg-gray-50 rounded-xl transition-all duration-300',
            (recordingRoomIdx === idx || processingRoomIdx === idx) 
                ? 'z-[60] relative ring-4 ring-blue-400 shadow-2xl scale-105' 
                : 'overflow-hidden'
          ]"
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
                :class="{ 'opacity-30 pointer-events-none': isRecordingOrProcessing }"
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
                    :disabled="isRecordingOrProcessing"
                    :class="{ 'opacity-30 cursor-not-allowed': isRecordingOrProcessing }"
                  >
                    <PhX :size="16" />
                  </button>
              </div>
            </div>

            <div class="flex gap-2 mt-4">
                <!-- Quick Add -->
                <button 
                    @click="openQuickAdd(idx)"
                    class="flex-1 py-2.5 border-2 border-dashed border-blue-200 rounded-xl text-xs font-bold text-blue-500 bg-blue-50/50 hover:bg-blue-50 hover:border-blue-300 transition-all flex items-center justify-center gap-2"
                >
                    <div class="bg-blue-500 text-white rounded-full p-0.5">
                      <PhPlus :size="12" weight="bold" />
                    </div>
                    Позиция
                </button>

                <!-- Voice Add -->
                <button 
                    @click="toggleRoomRecording(idx)"
                    :class="[
                        'flex-1 py-2.5 border-2 border-dashed rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2',
                        recordingRoomIdx === idx
                            ? 'border-red-300 bg-red-50 text-red-600 animate-pulse'
                            : 'border-indigo-200 text-indigo-600 bg-indigo-50/50 hover:bg-indigo-50 hover:border-indigo-300'
                    ]"
                >
                    <template v-if="processingRoomIdx === idx">
                        <span class="animate-spin">⏳</span>
                    </template>
                    <template v-else-if="recordingRoomIdx === idx">
                        <div class="w-2 h-2 bg-red-600 rounded-full animate-pulse"></div>
                        Стоп
                    </template>
                    <template v-else>
                        <PhMicrophone :size="18" weight="fill" />
                        Голос
                    </template>
                </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Voice Add Room (Global/New Section) -->
    <div class="mt-4 mb-6">
        <button 
            @click="toggleRoomRecording(-2)"
            :class="[
                'w-full py-4 rounded-xl font-bold transition-all flex items-center justify-center gap-2 border-2 border-dashed relative',
                (recordingRoomIdx === -2 || processingRoomIdx === -2)
                    ? 'bg-red-50 text-red-600 border-red-200 animate-pulse z-[60] shadow-xl scale-105' 
                    : 'bg-indigo-50 text-indigo-600 border-indigo-200 hover:bg-indigo-100 hover:border-indigo-300',
                recordingRoomIdx !== -1 && recordingRoomIdx !== -2 ? 'opacity-20 pointer-events-none' : ''
            ]"
            :disabled="processingRoomIdx !== -1 && processingRoomIdx !== -2"
        >
            <template v-if="processingRoomIdx === -2">
                <span class="animate-spin text-xl">⏳</span>
                <span>Обработка...</span>
            </template>
            <template v-else-if="recordingRoomIdx === -2">
                <div class="w-2 h-2 bg-red-600 rounded-full animate-pulse pr-2"></div>
                Запись... (нажмите для остановки)
            </template>
            <template v-else>
                <PhMicrophone :size="24" weight="fill" />
                Добавить комнату голосом
            </template>
        </button>
    </div>

    <!-- Navigation Buttons (Fixed on Mobile) -->
    <div class="flex flex-col sm:flex-row justify-between gap-3 pt-4 border-t">
      <button @click="$emit('prev')" class="btn btn-secondary order-2 sm:order-1">
        ← Назад
      </button>
      <button 
        @click="handleNextClick" 
        class="btn btn-primary btn-lg order-1 sm:order-2 transition-all duration-300" 
        :class="{ 'opacity-50 cursor-not-allowed grayscale': isRecordingOrProcessing }"
        :disabled="estimateStore.rooms.length === 0 && !isRecordingOrProcessing"
      >
        <span v-if="processingRoomIdx !== -1">Обработка...</span>
        <span v-else>Далее →</span>
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
            <span class="truncate font-medium flex-1 pr-2">{{ item.original_text || item.name }}</span>
            <div class="flex gap-1">
                <button 
                    @click="openSynonymSearch(item, idx)"
                    class="text-amber-600 hover:text-amber-800 text-[10px] font-bold px-2 py-1 bg-amber-50 rounded"
                >
                    Синоним
                </button>
                <button 
                    @click="addUnknownToDb(item)"
                    class="text-blue-600 hover:text-blue-800 text-[10px] font-bold px-2 py-1 bg-blue-50 rounded"
                >
                    + В базу
                </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Search/Select Modal for Syonyms -->
    <ItemSearchModal 
        :is-open="showSynonymSearch"
        title="Привязать как синоним к..."
        @close="showSynonymSearch = false"
        @select="confirmSynonym"
    />

    <!-- Search/Select Modal for Quick Add -->
    <ItemSearchModal 
        :is-open="showQuickAdd"
        title="Добавить в комнату..."
        @close="showQuickAdd = false"
        @select="addItemToRoom"
    />

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
import { ref, reactive, computed, watch, onUnmounted } from 'vue'
import { useEstimateStore } from '@/stores/estimate'
import { usePriceStore } from '@/stores/price'
import { PhTrash, PhX, PhPlus, PhMicrophone } from '@phosphor-icons/vue'
import VoiceRecorder from '@/components/input/VoiceRecorder.vue'
import transcribeService from '@/services/transcribeService'
import estimateService from '@/services/estimateService'
import ItemAutocomplete from '@/components/input/ItemAutocomplete.vue'
import ItemSearchModal from '@/components/input/ItemSearchModal.vue'
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

// Synonym flow
const showSynonymSearch = ref(false)
const activeUnknownItem = ref(null)
const activeUnknownIdx = ref(-1)

// Quick Add flow
const showQuickAdd = ref(false)
const activeRoomIdx = ref(-1)

const isRecordingOrProcessing = computed(() => recordingRoomIdx.value !== -1 || processingRoomIdx.value !== -1)

const handleNextClick = () => {
    if (processingRoomIdx.value !== -1) return // Block during processing
    
    if (recordingRoomIdx.value !== -1) {
        // If recording, stop it
        stopRoomRecording()
        return
    }
    
    // Normal next behavior
    emit('next')
}

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

const openSynonymSearch = (item, idx) => {
    activeUnknownItem.value = item
    activeUnknownIdx.value = idx
    showSynonymSearch.value = true
}

const confirmSynonym = async (selectedItem) => {
    const textToAdd = activeUnknownItem.value.original_text || activeUnknownItem.value.name
    try {
        await priceStore.addSynonym(selectedItem.id, textToAdd)
        // Remove from unknown
        if (activeUnknownIdx.value > -1) {
            unknownItems.value.splice(activeUnknownIdx.value, 1)
        }
        showSynonymSearch.value = false
        alert(`Текст "${textToAdd}" добавлен как синоним к "${selectedItem.name}"`)
    } catch (e) {
        alert('Ошибка при добавлении синонима: ' + e.message)
    }
}

const openQuickAdd = (idx) => {
    activeRoomIdx.value = idx
    showQuickAdd.value = true
}

const addItemToRoom = (selectedItem) => {
    const room = estimateStore.rooms[activeRoomIdx.value]
    if (!room) return
    
    estimateStore.addItem({
        room: room.name,
        price_item_id: selectedItem.id,
        name: selectedItem.name,
        unit: selectedItem.unit,
        quantity: 1, // Default
        price: selectedItem.price
    })
    
    showQuickAdd.value = false
}

// Initial load needed for categories
priceStore.fetchCategories()

const formatPrice = (val) => new Intl.NumberFormat('ru-RU').format(val || 0)

// --- Added for Step 2 Room Recording & Manual Add ---
const recordingRoomIdx = ref(-1)
const processingRoomIdx = ref(-1)
let roomMediaRecorder = null
let roomAudioChunks = []

const toggleRoomRecording = async (idx) => {
    if (recordingRoomIdx.value === idx) {
        stopRoomRecording()
    } else {
        if (recordingRoomIdx.value !== -1) stopRoomRecording()
        await startRoomRecording(idx)
    }
}

const startRoomRecording = async (idx) => {
    roomAudioChunks = []
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        let mimeType = 'audio/webm'
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) mimeType = 'audio/webm;codecs=opus'
        
        roomMediaRecorder = new MediaRecorder(stream, { mimeType })
        roomMediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) roomAudioChunks.push(e.data) }
        roomMediaRecorder.onstop = async () => {
            stream.getTracks().forEach(t => t.stop())
            // Use plain audio/webm for best compatibility with backend whitelist
            const blob = new Blob(roomAudioChunks, { type: 'audio/webm' })
            await processRoomAudio(blob)
        }
        roomMediaRecorder.start()
        recordingRoomIdx.value = idx
    } catch (err) {
        alert('Ошибка доступа к микрофону: ' + err.message)
    }
}

const stopRoomRecording = () => {
    if (roomMediaRecorder && roomMediaRecorder.state !== 'inactive') {
        processingRoomIdx.value = recordingRoomIdx.value // save for processing phase
        roomMediaRecorder.stop()
    }
    recordingRoomIdx.value = -1
}

const processRoomAudio = async (blob) => {
    const rIdx = processingRoomIdx.value
    // processingRoomIdx is already set in stopRoomRecording
    try {
        const text = await transcribeService.transcribe(blob)
        if (!text) return
        
        const res = await estimateService.parseTranscript(text)
        
        // Contextual override: if recording for an EXISTING room (rIdx >= 0) 
        // and parser returned exactly 1 room, rename that 1 room to our target.
        if (res.rooms?.length === 1 && rIdx >= 0 && estimateStore.rooms[rIdx]) {
            res.rooms[0].name = estimateStore.rooms[rIdx].name
        }
        
        if (res.rooms?.length > 0) {
            if (rIdx >= 0) {
                // For existing room: merge items
                estimateStore.mergeParsedRooms(res.rooms)
            } else {
                // For new room/global: add as new
                estimateStore.addParsedRooms(res.rooms)
                
                // If we added a whole section/rooms, scroll to bottom
                setTimeout(() => {
                    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
                }, 100)
            }
            handleParseResult(res)
        } else {
            alert('Не удалось распознать комнаты или позиции.')
        }
    } catch (e) {
        alert('Ошибка: ' + (e.response?.data?.detail || e.message))
    } finally {
        processingRoomIdx.value = -1
    }
}

onUnmounted(() => {
    if (roomMediaRecorder && roomMediaRecorder.state !== 'inactive') roomMediaRecorder.stop()
})

const emit = defineEmits(['next', 'prev'])
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
