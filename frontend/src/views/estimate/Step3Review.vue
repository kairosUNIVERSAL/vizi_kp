<template>
  <div class="space-y-6">
    <h2 class="text-xl font-bold">Проверка сметы</h2>
    
    <div class="bg-gray-50 p-6 rounded-lg border border-gray-200">
        <div class="flex justify-between mb-4 pb-4 border-b border-gray-200">
            <div>
                <div class="text-sm text-gray-500">Клиент</div>
                <div class="font-bold text-lg">{{ estimateStore.estimate?.client_name || clientInfo.client_name }}</div>
            </div>
            <div class="text-right">
                <div class="text-sm text-gray-500">Итоговая сумма</div>
                <div class="font-bold text-2xl text-blue-600">{{ formatPrice(totalSum) }} ₽</div>
            </div>
        </div>
        
        <div class="space-y-6">
            <div v-for="(room, rIdx) in estimateStore.rooms" :key="rIdx" class="bg-white p-4 rounded-lg shadow-sm">
                <div class="flex justify-between font-bold mb-4 border-b pb-2">
                    <div class="flex items-center gap-2">
                        <span>{{ room.name }}</span>
                        <div class="flex items-center gap-1 ml-2 font-normal text-sm text-gray-500">
                            <input 
                                v-model.number="room.area" 
                                type="number" 
                                class="w-16 px-1 border rounded"
                                @change="estimateStore.recalculate()"
                            /> м²
                        </div>
                    </div>
                    <span>{{ formatPrice(room.subtotal) }} ₽</span>
                </div>
                
                <div class="space-y-4">
                    <div v-for="(item, iIdx) in room.items" :key="iIdx" class="py-2 border-b border-gray-50 last:border-0">
                        <div class="flex flex-col sm:flex-row sm:items-center gap-2">
                            <!-- Name and Base Price -->
                            <div class="flex-1 min-w-0">
                                <div class="font-medium text-gray-900 leading-tight">{{ item.name }}</div>
                                <div class="text-gray-400 text-[10px] mt-0.5">
                                    {{ formatPrice(item.price) }} / {{ item.unit }}
                                </div>
                            </div>
                            
                            <!-- Controls and Subtotal -->
                            <div class="flex items-center justify-between sm:justify-end gap-4 mt-1 sm:mt-0">
                                <!-- Quantity Controls -->
                                <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
                                    <button 
                                        @click="updateQuantity(rIdx, iIdx, -1)"
                                        class="px-2 py-1.5 hover:bg-gray-200 border-r border-gray-200 transition-colors"
                                    >
                                        <PhMinus :size="10" weight="bold" />
                                    </button>
                                    <input 
                                        v-model.number="item.quantity" 
                                        type="number" 
                                        class="w-10 text-center text-xs font-bold focus:ring-0 border-0 bg-transparent"
                                        @change="estimateStore.recalculate()"
                                    />
                                    <button 
                                        @click="updateQuantity(rIdx, iIdx, 1)"
                                        class="px-2 py-1.5 hover:bg-gray-200 border-l border-gray-200 transition-colors"
                                    >
                                        <PhPlus :size="10" weight="bold" />
                                    </button>
                                </div>
                                
                                <!-- Sum -->
                                <div class="w-20 text-right font-bold text-gray-800">
                                    {{ formatPrice(item.price * item.quantity) }} ₽
                                </div>
                                
                                <!-- Delete -->
                                <button @click="removeItem(rIdx, iIdx)" class="p-1 text-gray-300 hover:text-red-500 transition-colors">
                                    <PhX :size="18" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div v-if="room.items.length === 0" class="text-center py-2 text-gray-400 text-sm italic">
                    Пустая комната. Будет удалена.
                </div>

                <!-- Quick Add Button -->
                <button 
                    @click="openQuickAdd(rIdx)"
                    class="w-full mt-4 py-2.5 border-2 border-dashed border-blue-200 rounded-xl text-xs font-bold text-blue-500 bg-blue-50/50 hover:bg-blue-50 hover:border-blue-300 transition-all flex items-center justify-center gap-2"
                >
                    <div class="bg-blue-500 text-white rounded-full p-0.5">
                        <PhPlus :size="10" weight="bold" />
                    </div>
                    Добавить позицию
                </button>

                <!-- Add Room Voice Button -->
                <button 
                    @click="toggleRoomRecording"
                    :class="[
                        'w-full mt-3 py-3 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2',
                        isRecordingRoom 
                            ? 'bg-red-50 text-red-600 border border-red-200 animate-pulse' 
                            : 'bg-indigo-50 text-indigo-600 border border-indigo-200 hover:bg-indigo-100'
                    ]"
                >
                    <template v-if="isProcessingRoom">
                        <span class="animate-spin">⏳</span>
                        Обработка...
                    </template>
                    <template v-else-if="isRecordingRoom">
                        <div class="w-2 h-2 bg-red-600 rounded-full animate-pulse"></div>
                        Запись... (нажмите для остановки)
                    </template>
                    <template v-else>
                        <PhMicrophone :size="18" weight="fill" />
                        Добавить комнату
                    </template>
                </button>
            </div>
        </div>

        <!-- Add Room Button -->
        <button 
            @click="addNewRoom"
            class="w-full mt-6 py-4 border-2 border-dashed border-gray-300 rounded-xl font-bold text-gray-500 hover:border-blue-400 hover:text-blue-500 hover:bg-blue-50 transition-all flex items-center justify-center gap-2"
        >
            <PhPlus :size="20" weight="bold" />
            Добавить новую комнату
        </button>

        <!-- Discount Inputs -->
        <div class="mt-8 pt-6 border-t border-gray-200">
            <h3 class="text-lg font-bold mb-4">Скидки</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Скидка на Услуги (%)</label>
                    <input 
                        type="number" 
                        v-model.number="estimateStore.discountPrWork" 
                        class="w-full border-gray-300 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="0"
                    />
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Скидка на Оборудование (%)</label>
                    <input 
                        type="number" 
                        v-model.number="estimateStore.discountEquipment" 
                        class="w-full border-gray-300 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="0"
                    />
                </div>
            </div>
        </div>

    </div>
    
    <div class="flex justify-between pt-4">
      <button @click="$emit('prev')" class="btn bg-gray-200 hover:bg-gray-300" :disabled="loading">← Назад</button>
      <button 
        @click="finishEstimate" 
        class="btn btn-primary flex items-center gap-2"
        :disabled="loading || totalSum === 0"
      >
        <span v-if="loading" class="animate-spin">⌛</span>
        Сохранить и создать PDF
      </button>
    </div>

    <!-- Quick Add Search Modal -->
    <ItemSearchModal 
        :is-open="showQuickAdd"
        title="Добавить в комнату..."
        @close="showQuickAdd = false"
        @select="addItemToRoom"
    />
  </div>
</template>

<script setup>
import { computed, ref, toRefs, onUnmounted } from 'vue'
import { useEstimateStore } from '@/stores/estimate'
import { PhMinus, PhPlus, PhX, PhMicrophone } from '@phosphor-icons/vue'
import transcribeService from '@/services/transcribeService'
import estimateService from '@/services/estimateService'
import ItemSearchModal from '@/components/input/ItemSearchModal.vue'

const emit = defineEmits(['next', 'prev'])
const estimateStore = useEstimateStore()
const { clientInfo } = toRefs(estimateStore)
const loading = ref(false)
const showQuickAdd = ref(false)
const activeRoomIdx = ref(-1)

// Recording state
const isRecordingRoom = ref(false)
const isProcessingRoom = ref(false)
let mediaRecorder = null
let audioChunks = []

const totalSum = computed(() => {
    return estimateStore.rooms.reduce((acc, r) => acc + (Number(r.subtotal) || 0), 0)
})

const formatPrice = (val) => new Intl.NumberFormat('ru-RU').format(val || 0)

const openQuickAdd = (idx) => {
    activeRoomIdx.value = idx
    showQuickAdd.value = true
}

const addNewRoom = () => {
    const name = prompt("Введите название комнаты:", "Новая комната")
    if (name) {
        estimateStore.addRoom(name)
    }
}

const addItemToRoom = (selectedItem) => {
    const room = estimateStore.rooms[activeRoomIdx.value]
    if (!room) return
    
    estimateStore.addItem({
        roomIndex: activeRoomIdx.value, // Pass index for precise lookup
        room: room.name,
        price_item_id: selectedItem.id,
        name: selectedItem.name,
        unit: selectedItem.unit,
        quantity: 1,
        price: selectedItem.price
    })
    
    showQuickAdd.value = false
}

const updateQuantity = (rIdx, iIdx, delta) => {
    const item = estimateStore.rooms[rIdx].items[iIdx]
    item.quantity = Math.max(0.1, Number(item.quantity) + delta)
    estimateStore.recalculate()
}

const removeItem = (rIdx, iIdx) => {
    estimateStore.rooms[rIdx].items.splice(iIdx, 1)
    if (estimateStore.rooms[rIdx].items.length === 0) {
        estimateStore.rooms.splice(rIdx, 1)
    }
    estimateStore.recalculate()
}

// Room Recording Logic
const toggleRoomRecording = async () => {
    if (isRecordingRoom.value) {
        stopRoomRecording()
    } else {
        await startRoomRecording()
    }
}

const startRoomRecording = async () => {
    audioChunks = []
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        
        // Try supported formats
        const mimeTypes = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/mp4',
            'audio/ogg;codecs=opus'
        ]
        
        let selectedMimeType = ''
        for (const mimeType of mimeTypes) {
            if (MediaRecorder.isTypeSupported(mimeType)) {
                selectedMimeType = mimeType
                break
            }
        }
        
        const options = selectedMimeType ? { mimeType: selectedMimeType } : {}
        mediaRecorder = new MediaRecorder(stream, options)
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data)
            }
        }
        
        mediaRecorder.onstop = async () => {
            stream.getTracks().forEach(track => track.stop())
            const audioBlob = new Blob(audioChunks, { type: selectedMimeType || 'audio/webm' })
            await processRoomAudio(audioBlob)
        }
        
        mediaRecorder.start()
        isRecordingRoom.value = true
        
    } catch (err) {
        alert('Ошибка доступа к микрофону: ' + err.message)
    }
}

const stopRoomRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop()
    }
    isRecordingRoom.value = false
}

const processRoomAudio = async (audioBlob) => {
    isProcessingRoom.value = true
    try {
        // Transcribe
        const transcript = await transcribeService.transcribe(audioBlob)
        if (!transcript) return

        // Parse (using clean parse via service)
        const parsedData = await estimateService.parseTranscript(transcript)
        
        if (parsedData.rooms && parsedData.rooms.length > 0) {
            // Add as NEW rooms
            estimateStore.addParsedRooms(parsedData.rooms)
            // Scroll to bottom
            setTimeout(() => {
                 window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
            }, 100)
        } else {
            alert('Не удалось распознать комнаты или позиции. Попробуйте еще раз.')
        }

    } catch (err) {
        alert('Ошибка обработки: ' + (err.response?.data?.detail || err.message))
    } finally {
        isProcessingRoom.value = false
    }
}

onUnmounted(() => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop()
    }
})

const finishEstimate = async () => {
    loading.value = true
    try {
        if (estimateStore.isEditing) {
            await estimateStore.updateEstimate()
        } else {
            await estimateStore.createEstimate()
        }
        emit('next')
    } catch (e) {
        alert('Ошибка при сохранении: ' + e.message)
    } finally {
        loading.value = false
    }
}
</script>
