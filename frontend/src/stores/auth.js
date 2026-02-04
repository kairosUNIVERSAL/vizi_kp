import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { jwtDecode } from "jwt-decode";
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
    const token = ref(localStorage.getItem('token') || null)
    const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

    const isAuthenticated = computed(() => !!token.value)

    const login = async (email, password) => {
        try {
            // OAuth2 expects form data, not JSON
            const formData = new URLSearchParams()
            formData.append('username', email)
            formData.append('password', password)

            const { data } = await api.post('/auth/login', formData, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            })

            token.value = data.access_token
            localStorage.setItem('token', data.access_token)

            // Fetch user profile
            await fetchUser()

            router.push({ name: 'dashboard' })
            return true
        } catch (error) {
            console.error('Login error:', error)
            throw error
        }
    }

    const register = async (email, password) => {
        await api.post('/auth/register', { email, password })
        await login(email, password)
    }

    const fetchUser = async () => {
        try {
            const { data } = await api.get('/users/me')
            user.value = data
            localStorage.setItem('user', JSON.stringify(data))
        } catch (error) {
            console.error("Fetch user error", error)
        }
    }

    const logout = () => {
        token.value = null
        user.value = null
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push({ name: 'login' })
    }

    return {
        token,
        user,
        isAuthenticated,
        login,
        register,
        logout,
        fetchUser
    }
})
