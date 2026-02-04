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
    }

    const createEstimate = async () => {
        const payload = {
            ...clientInfo.value,
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

        const data = await estimateService.createEstimate(payload)
        estimate.value = data
        return data
    }

    const parseTranscript = async (transcript) => {
        const data = await estimateService.parseTranscript(transcript)

        if (data.rooms) {
            // Merge AI rooms with existing rooms by name
            data.rooms.forEach(newRoom => {
                let room = rooms.value.find(r => r.name === newRoom.name)
                if (!room) {
                    rooms.value.push(newRoom)
                } else {
                    // Update area if parsed
                    if (newRoom.area) room.area = newRoom.area
                    // Append items
                    room.items.push(...newRoom.items)
                }
            })
            recalculate()
        }
        return data
    }

    const estimates = ref([])

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
        addItem,
        recalculate,
        clear,
        createEstimate,
        parseTranscript,
        fetchEstimates
    }
})
