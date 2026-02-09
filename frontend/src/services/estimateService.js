import api from './api'

export default {
    async createEstimate(data) {
        const response = await api.post('/estimates/', data)
        return response.data
    },

    async updateEstimate(id, data) {
        const response = await api.put(`/estimates/${id}`, data)
        return response.data
    },

    async getEstimate(id) {
        const response = await api.get(`/estimates/${id}`)
        return response.data
    },

    async parseTranscript(transcript) {
        const response = await api.post('/estimates/parse', { transcript })
        return response.data
    },

    async getEstimates(params = {}) {
        const response = await api.get('/estimates/', { params })
        return response.data
    }
}
