<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 px-4">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-6 relative">
      <button @click="close" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
        <PhX :size="20" />
      </button>

      <h2 class="text-xl font-bold mb-4">{{ isEdit ? 'Редактировать позицию' : 'Новая позиция' }}</h2>

      <form @submit.prevent="save">
        <div class="space-y-4">
          <!-- Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Название</label>
            <input 
              v-model="form.name" 
              type="text" 
              required
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Например: Профиль ПВХ"
            />
          </div>

          <!-- Category -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Категория</label>
            <select 
              v-model="form.category_id" 
              required
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none bg-white"
            >
              <option :value="null" disabled>Выберите категорию</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4">
             <!-- Price -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Цена (₽)</label>
              <input 
                v-model.number="form.price" 
                type="number" 
                step="0.01"
                min="0"
                required
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>

            <!-- Unit -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Ед. изм.</label>
              <select 
                v-model="form.unit" 
                required
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none bg-white"
              >
                <option value="шт">шт</option>
                <option value="м.пог.">м.пог.</option>
                <option value="м2">м²</option>
                <option value="компл">компл</option>
                <option value="упак">упак</option>
              </select>
            </div>
          </div>

          <!-- Synonyms -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Синонимы 
              <span class="text-xs text-gray-500 font-normal ml-1">(для голосового ввода)</span>
            </label>
            <textarea 
              v-model="form.synonyms" 
              rows="2"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none text-sm"
              placeholder="Через запятую: багет, профиль стеновой..."
            ></textarea>
          </div>
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button 
            type="button" 
            @click="close"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Отмена
          </button>
          <button 
            type="submit" 
            :disabled="loading"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {{ loading ? 'Сохранение...' : 'Сохранить' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { usePriceStore } from '@/stores/price'
import { PhX } from '@phosphor-icons/vue'

const props = defineProps({
  isOpen: Boolean,
  item: Object,
  categories: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'saved'])
const priceStore = usePriceStore()
const loading = ref(false)

const isEdit = computed(() => !!props.item?.id)

const form = ref({
  name: '',
  category_id: null,
  price: 0,
  unit: 'шт',
  synonyms: '',
  is_active: true
})

// Initialize form when item changes or modal opens
watch(() => props.item, (newItem) => {
  if (newItem) {
    form.value = { ...newItem }
    // Ensure category_id is set if editing
  } else {
    // Reset for new item
    form.value = {
      name: '',
      category_id: props.categories[0]?.id || null, // Default to first cat if exists
      price: 0,
      unit: 'шт',
      synonyms: '',
      is_active: true
    }
  }
}, { immediate: true })

// Also watch categories to set default if new
watch(() => props.categories, (cats) => {
  if (!isEdit.value && !form.value.category_id && cats.length) {
    form.value.category_id = cats[0].id
  }
})

const close = () => {
  emit('close')
}

const save = async () => {
  loading.value = true
  try {
    if (isEdit.value) {
      await priceStore.updateItem(props.item.id, form.value)
    } else {
      await priceStore.createItem(form.value)
    }
    emit('saved')
    close()
  } catch (e) {
    console.error(e)
    alert(e.message || 'Ошибка сохранения')
  } finally {
    loading.value = false
  }
}
</script>
