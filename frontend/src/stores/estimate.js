import { defineStore } from 'pinia'
import { ref } from 'vue'
import estimateService from '@/services/estimateService'

export const useEstimateStore = defineStore('estimate', () => {
    const estimate = ref(null)
    const rooms = ref([])
    const clientInfo = ref({
        client_name: '',
        client_phone: '',
        client_address: ''
    })
    const isEditing = ref(false)
    const currentStep = ref(1)
    const estimates = ref([])

    const addItem = (item) => {
        let room = rooms.value.find(r => r.name === item.room)
        if (!room) {
            room = { name: item.room, items: [], area: 0, subtotal: 0 }
            rooms.value.push(room)
        }

        room.items.push({
            name: item.name,
            price_item_id: item.price_item_id,
            unit: item.unit,
            quantity: Number(item.quantity),
            price: Number(item.price),
            sum: Number(item.quantity) * Number(item.price)
        })

        recalculate()
    }

    const recalculate = () => {
        rooms.value.forEach(r => {
            r.subtotal = r.items.reduce((acc, i) => acc + (Number(i.price) * Number(i.quantity)), 0)
        })
    }

    const clear = () => {
        estimate.value = null
        rooms.value = []
        clientInfo.value = {
            client_name: '',
            client_phone: '',
            client_address: ''
        }
        isEditing.value = false
        currentStep.value = 1
    }

    const loadEstimate = async (id) => {
        const data = await estimateService.getEstimate(id)
        estimate.value = data
        isEditing.value = true
        currentStep.value = data.last_step || 1

        clientInfo.value = {
            client_name: data.client_name || '',
            client_phone: data.client_phone || '',
            client_address: data.client_address || ''
        }

        rooms.value = (data.rooms || []).map(r => ({
            name: r.name,
            area: Number(r.area) || 0,
            subtotal: Number(r.subtotal) || 0,
            items: (r.items || []).map(i => ({
                name: i.name,
                price_item_id: i.price_item_id,
                unit: i.unit,
                quantity: Number(i.quantity),
                price: Number(i.price),
                sum: Number(i.sum) || Number(i.quantity) * Number(i.price)
            }))
        }))

        return data
    }

    const buildPayload = () => {
        return {
            ...clientInfo.value,
            last_step: currentStep.value,
            rooms: rooms.value.map(r => ({
                name: r.name,
                area: r.area || 0,
                items: r.items.map(i => ({
                    price_item_id: i.price_item_id,
                    name: i.name,
                    unit: i.unit,
                    quantity: i.quantity,
                    price: i.price
                }))
            }))
        }
    }

    const createEstimate = async () => {
        const payload = { ...buildPayload(), status: 'completed' }
        const data = await estimateService.createEstimate(payload)
        estimate.value = data
        isEditing.value = true
        return data
    }

    const updateEstimate = async () => {
        if (!estimate.value?.id) return
        const payload = { ...buildPayload(), status: 'completed' }
        const data = await estimateService.updateEstimate(estimate.value.id, payload)
        estimate.value = data
        return data
    }

    const saveDraft = async () => {
        // Don't save empty drafts
        const hasData = clientInfo.value.client_name || rooms.value.length > 0
        if (!hasData) return

        const payload = { ...buildPayload(), status: 'draft' }

        if (estimate.value?.id) {
            const data = await estimateService.updateEstimate(estimate.value.id, payload)
            estimate.value = data
        } else {
            const data = await estimateService.createEstimate(payload)
            estimate.value = data
            isEditing.value = true
        }
    }

    const parseTranscript = async (transcript) => {
        const data = await estimateService.parseTranscript(transcript)

        if (data.rooms) {
            data.rooms.forEach(newRoom => {
                let room = rooms.value.find(r => r.name === newRoom.name)
                if (!room) {
                    rooms.value.push(newRoom)
                } else {
                    if (newRoom.area) room.area = newRoom.area
                    room.items.push(...newRoom.items)
                }
            })
            recalculate()
        }
        return data
    }

    const fetchEstimates = async () => {
        const data = await estimateService.getEstimates()
        estimates.value = data
        return data
    }

    return {
        estimate,
        rooms,
        estimates,
        clientInfo,
        isEditing,
        currentStep,
        addItem,
        recalculate,
        clear,
        loadEstimate,
        createEstimate,
        updateEstimate,
        saveDraft,
        parseTranscript,
        fetchEstimates
    }
})
