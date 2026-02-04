<template>
  <div class="flex min-h-screen items-center justify-center p-4">
    <div class="w-full max-w-md space-y-8 bg-white p-8 rounded-xl shadow-lg">
      <h2 class="text-3xl font-bold text-center">Register</h2>
      <form @submit.prevent="handleRegister" class="space-y-6">
        <input v-model="email" type="email" placeholder="Email" class="input" required />
        <input v-model="password" type="password" placeholder="Password" class="input" required />
        <button type="submit" class="w-full btn btn-primary">Sign Up</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const email = ref('')
const password = ref('')
const authStore = useAuthStore()

const handleRegister = async () => {
  await authStore.register(email.value, password.value)
}
</script>
