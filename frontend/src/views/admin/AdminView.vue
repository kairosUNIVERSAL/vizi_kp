<template>
  <div class="p-8 max-w-6xl mx-auto">
    <div class="flex justify-between items-center mb-8">
      <div>
        <router-link :to="{name: 'dashboard'}" class="text-blue-600 hover:text-blue-800 text-sm mb-2 inline-flex items-center gap-1">
          <PhCaretLeft :size="16" /> Назад
        </router-link>
        <h1 class="text-2xl font-bold">Администрирование</h1>
      </div>
      <button @click="showCreateModal = true" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center gap-2">
        <PhPlus :size="20" /> Создать пользователя
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div class="text-sm text-gray-500">Пользователей</div>
        <div class="text-3xl font-bold">{{ stats.total_users }}</div>
      </div>
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div class="text-sm text-gray-500">Всего смет</div>
        <div class="text-3xl font-bold">{{ stats.total_estimates }}</div>
      </div>
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div class="text-sm text-gray-500">Токенов использовано</div>
        <div class="text-3xl font-bold">{{ formatNumber(stats.total_tokens_used) }}</div>
      </div>
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div class="text-sm text-gray-500">Затраты API ($)</div>
        <div class="text-3xl font-bold text-blue-600">${{ stats.total_api_cost?.toFixed(2) || '0.00' }}</div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-100">
        <h2 class="font-bold text-lg">Пользователи</h2>
      </div>
      
      <div v-if="loading" class="p-12 text-center text-gray-400">Загрузка...</div>
      
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-gray-50 text-xs font-bold text-gray-500 uppercase tracking-wider">
            <tr>
              <th class="px-6 py-3">Email</th>
              <th class="px-6 py-3">Компания</th>
              <th class="px-6 py-3 text-right">Смет</th>
              <th class="px-6 py-3 text-right">Токенов</th>
              <th class="px-6 py-3 text-right">Затраты ($)</th>
              <th class="px-6 py-3">Создан</th>
              <th class="px-6 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <div class="font-medium">{{ user.email }}</div>
                <div class="text-xs text-gray-500">
                  <span v-if="user.is_admin" class="text-purple-600">Админ</span>
                  <span v-else-if="!user.is_active" class="text-red-600">Неактивен</span>
                </div>
              </td>
              <td class="px-6 py-4 text-sm">{{ user.company?.name || '—' }}</td>
              <td class="px-6 py-4 text-right">{{ user.estimates_count }}</td>
              <td class="px-6 py-4 text-right">{{ formatNumber(user.total_tokens_used) }}</td>
              <td class="px-6 py-4 text-right">${{ Number(user.total_api_cost || 0).toFixed(4) }}</td>
              <td class="px-6 py-4 text-sm text-gray-500">{{ formatDate(user.created_at) }}</td>
              <td class="px-6 py-4 text-right">
                <button 
                  v-if="!user.is_admin"
                  @click="deleteUser(user)"
                  class="text-gray-400 hover:text-red-600 transition"
                  title="Удалить"
                >
                  <PhTrash :size="18" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create User Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showCreateModal = false">
      <div class="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
        <h3 class="text-lg font-bold mb-4">Создать пользователя</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input v-model="newUser.email" type="email" class="w-full border rounded-lg px-4 py-2" placeholder="user@example.com">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
            <input v-model="newUser.password" type="password" class="w-full border rounded-lg px-4 py-2" placeholder="••••••••">
          </div>
          <label class="flex items-center gap-2">
            <input v-model="newUser.is_admin" type="checkbox" class="rounded">
            <span class="text-sm">Администратор</span>
          </label>
        </div>
        
        <div v-if="createError" class="mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">{{ createError }}</div>
        
        <div class="flex justify-end gap-3 mt-6">
          <button @click="showCreateModal = false" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            Отмена
          </button>
          <button @click="createUser" :disabled="creating" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
            {{ creating ? 'Создание...' : 'Создать' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { PhCaretLeft, PhPlus, PhTrash } from '@phosphor-icons/vue'
import api from '@/services/api'

const loading = ref(true)
const users = ref([])
const stats = ref({})
const showCreateModal = ref(false)
const creating = ref(false)
const createError = ref(null)

const newUser = ref({
  email: '',
  password: '',
  is_admin: false
})

const formatNumber = (n) => n?.toLocaleString('ru-RU') || '0'
const formatDate = (d) => new Date(d).toLocaleDateString('ru-RU')

onMounted(async () => {
  await loadData()
})

const loadData = async () => {
  loading.value = true
  try {
    const [usersRes, statsRes] = await Promise.all([
      api.get('/admin/users'),
      api.get('/admin/stats')
    ])
    users.value = usersRes
    stats.value = statsRes
  } catch (e) {
    console.error('Failed to load admin data:', e)
  } finally {
    loading.value = false
  }
}

const createUser = async () => {
  if (!newUser.value.email || !newUser.value.password) {
    createError.value = 'Заполните все поля'
    return
  }
  
  creating.value = true
  createError.value = null
  
  try {
    await api.post('/admin/users', newUser.value)
    showCreateModal.value = false
    newUser.value = { email: '', password: '', is_admin: false }
    await loadData()
  } catch (e) {
    createError.value = e.message || 'Ошибка создания пользователя'
  } finally {
    creating.value = false
  }
}

const deleteUser = async (user) => {
  if (!confirm(`Удалить пользователя "${user.email}"? Все его данные будут удалены.`)) return
  
  try {
    await api.delete(`/admin/users/${user.id}`)
    await loadData()
  } catch (e) {
    alert(e.message || 'Ошибка удаления')
  }
}
</script>
