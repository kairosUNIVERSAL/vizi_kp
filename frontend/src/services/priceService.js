import api from './api'

export default {
    async getCategories() {
        const response = await api.get('/price/categories')
        return response.data
    },

    async getItems(params = {}) {
        const response = await api.get('/price/items', { params })
        return response.data
    },

    async searchItems(query, limit = 10) {
        const response = await api.get('/price/search', { params: { q: query, limit } })
        return response.data
    }
}
