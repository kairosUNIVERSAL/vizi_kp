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

    const createItem = async (itemData) => {
        const { data } = await api.post('/price/items', itemData)
        items.value.push(data)
        return data
    }

    const updateItem = async (id, itemData) => {
        const { data } = await api.put(`/price/items/${id}`, itemData)
        const index = items.value.findIndex(i => i.id === id)
        if (index !== -1) items.value[index] = data
        return data
    }

    const deleteItem = async (id) => {
        await api.delete(`/price/items/${id}`)
        items.value = items.value.filter(i => i.id !== id)
    }

    const addSynonym = async (itemId, synonym) => {
        const { data } = await api.post(`/price/items/${itemId}/add-synonym`, { synonym })
        const index = items.value.findIndex(i => i.id === itemId)
        if (index !== -1) items.value[index] = data
        return data
    }

    const fetchItems = async () => {
        loading.value = true
        try {
            const { data } = await api.get('/price/items?active_only=false') // Fetch all for management
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
        fetchItems,
        createItem,
        updateItem,
        deleteItem,
        addSynonym
    }
})
