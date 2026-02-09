<template>
  <div class="p-8 max-w-3xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex items-center gap-4 mb-2">
      <router-link 
        :to="{name: 'dashboard'}" 
        class="text-blue-600 hover:text-blue-800 flex items-center gap-1"
      >
        <PhCaretLeft :size="18" /> Назад
      </router-link>
      <h1 class="text-2xl font-bold">Личный кабинет</h1>
    </div>

    <!-- User Info -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center gap-4">
      <div class="bg-blue-100 text-blue-600 p-4 rounded-full">
        <PhUser :size="32" weight="fill" />
      </div>
      <div>
        <div class="font-bold text-lg">{{ authStore.user?.email }}</div>
        <div class="text-sm text-gray-500">
          {{ authStore.user?.is_admin ? 'Администратор' : 'Пользователь' }}
        </div>
      </div>
    </div>

    <!-- Menu Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <!-- Profile -->
      <router-link :to="{name: 'profile'}" class="block group">
        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 hover:border-blue-300 hover:shadow-md transition-all flex items-center gap-4">
          <div class="bg-purple-100 p-3 rounded-lg text-purple-600 group-hover:scale-110 transition-transform">
            <PhUserGear :size="28" />
          </div>
          <div>
            <h3 class="font-bold text-gray-900">Профиль</h3>
            <p class="text-xs text-gray-500">Настройки компании и PDF</p>
          </div>
        </div>
      </router-link>

      <!-- Price List -->
      <router-link :to="{name: 'prices'}" class="block group">
        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 hover:border-blue-300 hover:shadow-md transition-all flex items-center gap-4">
          <div class="bg-emerald-100 p-3 rounded-lg text-emerald-600 group-hover:scale-110 transition-transform">
            <PhListBullets :size="28" />
          </div>
          <div>
            <h3 class="font-bold text-gray-900">Прайс-лист</h3>
            <p class="text-xs text-gray-500">Редактировать цены и позиции</p>
          </div>
        </div>
      </router-link>

      <!-- Admin (only for admins) -->
      <router-link v-if="authStore.user?.is_admin" :to="{name: 'admin'}" class="block group">
        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 hover:border-blue-300 hover:shadow-md transition-all flex items-center gap-4">
          <div class="bg-orange-100 p-3 rounded-lg text-orange-600 group-hover:scale-110 transition-transform">
            <PhShieldCheck :size="28" />
          </div>
          <div>
            <h3 class="font-bold text-gray-900">Администрирование</h3>
            <p class="text-xs text-gray-500">Пользователи и статистика</p>
          </div>
        </div>
      </router-link>

      <!-- Logout -->
      <button @click="handleLogout" class="block group text-left w-full">
        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 hover:border-red-300 hover:shadow-md transition-all flex items-center gap-4">
          <div class="bg-red-100 p-3 rounded-lg text-red-600 group-hover:scale-110 transition-transform">
            <PhSignOut :size="28" />
          </div>
          <div>
            <h3 class="font-bold text-gray-900">Выход</h3>
            <p class="text-xs text-gray-500">Выйти из аккаунта</p>
          </div>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { PhCaretLeft, PhUser, PhUserGear, PhListBullets, PhShieldCheck, PhSignOut } from '@phosphor-icons/vue'

const authStore = useAuthStore()

const handleLogout = () => {
  if (confirm('Вы уверены, что хотите выйти?')) {
    authStore.logout()
  }
}
</script>
