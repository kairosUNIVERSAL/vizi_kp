import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const usePriceStore = defineStore('price', () => {
    const categories = ref([])
    const items = ref([])
    const loading = ref(false)

    const activeItems = computed(() => items.value.filter(i => i.is_active))

    const fetchCategories = async () => {
        try {
            const { data } = await api.get('/price/categories')
            categories.value = data
        } catch (e) {
            console.error(e)
        }
    }

    const fetchItems = async () => {
        loading.value = true
        try {
            const { data } = await api.get('/price/items')
            items.value = data.items
        } catch (e) {
            console.error(e)
        } finally {
            loading.value = false
        }
    }

    return {
        categories,
        items,
        activeItems,
        loading,
        fetchCategories,
        fetchItems
    }
})
