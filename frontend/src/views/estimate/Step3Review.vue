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
  </div>
</template>

<script setup>
import { computed, ref, toRefs } from 'vue'
import { useEstimateStore } from '@/stores/estimate'
import { PhMinus, PhPlus, PhX } from '@phosphor-icons/vue'

const emit = defineEmits(['next', 'prev'])
const estimateStore = useEstimateStore()
const { clientInfo } = toRefs(estimateStore)
const loading = ref(false)

const totalSum = computed(() => {
    return estimateStore.rooms.reduce((acc, r) => acc + (Number(r.subtotal) || 0), 0)
})

const formatPrice = (val) => new Intl.NumberFormat('ru-RU').format(val)

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

const finishEstimate = async () => {
    loading.value = true
    try {
        await estimateStore.createEstimate()
        emit('next')
    } catch (e) {
        alert('Ошибка при сохранении: ' + e.message)
    } finally {
        loading.value = false
    }
}
</script>
