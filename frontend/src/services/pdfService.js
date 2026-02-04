import api from './api'

export default {
    async generatePdf(estimateId) {
        const response = await api.post('/pdf/generate',
            { estimate_id: estimateId },
            { responseType: 'blob' }
        )
        return response.data
    },

    async previewPdf(estimateId) {
        const response = await api.get(`/pdf/preview/${estimateId}`, {
            responseType: 'blob'
        })
        return response.data
    },

    createPreviewUrl(blob) {
        return window.URL.createObjectURL(blob)
    },

    revokePreviewUrl(url) {
        if (url) window.URL.revokeObjectURL(url)
    }
}
