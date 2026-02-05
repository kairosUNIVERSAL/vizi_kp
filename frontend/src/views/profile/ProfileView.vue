<template>
  <div class="p-8 max-w-4xl mx-auto">
    <div class="flex justify-between items-center mb-8">
      <div>
        <router-link :to="{name: 'dashboard'}" class="text-blue-600 hover:text-blue-800 text-sm mb-2 inline-flex items-center gap-1">
          <PhCaretLeft :size="16" /> Назад
        </router-link>
        <h1 class="text-2xl font-bold">Настройки профиля</h1>
      </div>
      <button 
        @click="saveProfile" 
        :disabled="saving"
        class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
      >
        {{ saving ? 'Сохранение...' : 'Сохранить' }}
      </button>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-500">Загрузка...</div>
    <div v-else class="space-y-8">
      
      <!-- Basic Info -->
      <section class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-4">
        <h2 class="font-bold text-lg border-b pb-2">Основная информация</h2>
        
        <div class="grid md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Название компании / ФИО ИП</label>
            <input v-model="form.name" type="text" class="w-full border rounded-lg px-4 py-2" placeholder="ООО Натяжные потолки">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
            <input v-model="form.phone" type="tel" class="w-full border rounded-lg px-4 py-2" placeholder="+7 (999) 123-45-67">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Город</label>
            <input v-model="form.city" type="text" class="w-full border rounded-lg px-4 py-2" placeholder="Москва">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Адрес офиса</label>
            <input v-model="form.address" type="text" class="w-full border rounded-lg px-4 py-2" placeholder="ул. Примерная, д. 1">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Сайт</label>
            <input v-model="form.website" type="url" class="w-full border rounded-lg px-4 py-2" placeholder="https://example.ru">
          </div>
        </div>
      </section>

      <!-- Contacts -->
      <section class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-4">
        <h2 class="font-bold text-lg border-b pb-2">Мессенджеры</h2>
        
        <div class="grid md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Контакт (@username или номер)</label>
            <input v-model="form.messenger_contact" type="text" class="w-full border rounded-lg px-4 py-2" placeholder="@username">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Мессенджер</label>
            <select v-model="form.messenger_type" class="w-full border rounded-lg px-4 py-2">
              <option value="telegram">Telegram</option>
              <option value="whatsapp">WhatsApp</option>
            </select>
          </div>
        </div>
      </section>

      <!-- Warranties -->
      <section class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-4">
        <h2 class="font-bold text-lg border-b pb-2">Гарантии и условия</h2>
        
        <div class="grid md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Гарантия на полотно (лет)</label>
            <input v-model.number="form.warranty_material" type="number" min="1" class="w-full border rounded-lg px-4 py-2">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Гарантия на монтаж (лет)</label>
            <input v-model.number="form.warranty_work" type="number" min="1" class="w-full border rounded-lg px-4 py-2">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Срок действия КП (дней)</label>
            <input v-model.number="form.validity_days" type="number" min="1" class="w-full border rounded-lg px-4 py-2">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Скидка за быстрое решение (%)</label>
            <input v-model.number="form.discount" type="number" min="0" max="100" class="w-full border rounded-lg px-4 py-2">
          </div>
        </div>
      </section>

      <!-- Logo -->
      <section class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-4">
        <h2 class="font-bold text-lg border-b pb-2">Логотип</h2>
        
        <div class="flex items-start gap-6">
          <div v-if="form.logo_path" class="w-32 h-32 rounded-lg border overflow-hidden bg-gray-50">
            <img :src="logoUrl" alt="Logo" class="w-full h-full object-contain">
          </div>
          <div v-else class="w-32 h-32 rounded-lg border border-dashed border-gray-300 flex items-center justify-center text-gray-400">
            Нет логотипа
          </div>
          
          <div class="flex-1 space-y-2">
            <input type="file" ref="logoInput" @change="uploadLogo" accept=".jpg,.jpeg,.png,.gif,.webp" class="hidden">
            <button @click="$refs.logoInput.click()" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
              {{ form.logo_path ? 'Заменить' : 'Загрузить' }} логотип
            </button>
            <button v-if="form.logo_path" @click="deleteLogo" class="px-4 py-2 text-red-600 hover:text-red-700">
              Удалить
            </button>
            <p class="text-xs text-gray-500">JPG, PNG, GIF, WebP. Макс. 5 МБ.</p>
          </div>
        </div>
      </section>

      <!-- Payment Details -->
      <section class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-4">
        <h2 class="font-bold text-lg border-b pb-2">Реквизиты для оплаты</h2>
        
        <div class="grid md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">ИНН</label>
            <input v-model="form.inn" type="text" maxlength="12" class="w-full border rounded-lg px-4 py-2" placeholder="1234567890">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">КПП</label>
            <input v-model="form.kpp" type="text" maxlength="9" class="w-full border rounded-lg px-4 py-2" placeholder="123456789">
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Название банка</label>
            <input v-model="form.bank_name" type="text" class="w-full border rounded-lg px-4 py-2" placeholder="Сбербанк">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Расчётный счёт</label>
            <input v-model="form.bank_account" type="text" maxlength="20" class="w-full border rounded-lg px-4 py-2" placeholder="40702810000000000001">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">БИК</label>
            <input v-model="form.bank_bik" type="text" maxlength="9" class="w-full border rounded-lg px-4 py-2" placeholder="044525225">
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Корр. счёт</label>
            <input v-model="form.bank_corr" type="text" maxlength="20" class="w-full border rounded-lg px-4 py-2" placeholder="30101810400000000225">
          </div>
        </div>
      </section>

    </div>

    <div v-if="error" class="mt-4 p-4 bg-red-50 text-red-700 rounded-lg">{{ error }}</div>
    <div v-if="success" class="mt-4 p-4 bg-green-50 text-green-700 rounded-lg">{{ success }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { PhCaretLeft } from '@phosphor-icons/vue'
import api from '@/services/api'

const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const success = ref(null)
const logoInput = ref(null)

const form = ref({
  name: '',
  phone: '',
  city: '',
  address: '',
  website: '',
  messenger_contact: '',
  messenger_type: 'telegram',
  warranty_material: 15,
  warranty_work: 3,
  validity_days: 14,
  discount: 5,
  logo_path: null,
  inn: '',
  kpp: '',
  bank_name: '',
  bank_account: '',
  bank_bik: '',
  bank_corr: ''
})

const logoUrl = computed(() => {
  if (!form.value.logo_path) return null
  const filename = form.value.logo_path.split('/').pop()
  return `/api/upload/logo/${filename}`
})

onMounted(async () => {
  try {
    const res = await api.get('/users/me')
    if (res.data.company) {
      Object.assign(form.value, res.data.company)
    }
  } catch (e) {
    error.value = 'Ошибка загрузки профиля'
  } finally {
    loading.value = false
  }
})

const saveProfile = async () => {
  saving.value = true
  error.value = null
  success.value = null
  
  try {
    await api.put('/users/me/company', form.value)
    success.value = 'Настройки сохранены'
    setTimeout(() => { success.value = null }, 3000)
  } catch (e) {
    error.value = e.message || 'Ошибка сохранения'
  } finally {
    saving.value = false
  }
}

const uploadLogo = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const res = await api.post('/upload/logo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    form.value.logo_path = res.data.logo_path
    success.value = 'Логотип загружен'
    setTimeout(() => { success.value = null }, 3000)
  } catch (e) {
    error.value = e.message || 'Ошибка загрузки логотипа'
  }
}

const deleteLogo = async () => {
  try {
    await api.delete('/upload/logo')
    form.value.logo_path = null
    success.value = 'Логотип удалён'
    setTimeout(() => { success.value = null }, 3000)
  } catch (e) {
    error.value = e.message || 'Ошибка удаления'
  }
}
</script>
