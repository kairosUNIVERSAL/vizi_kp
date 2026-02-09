<template>
  <div class="mobile-container safe-area-pt">
    <!-- Mobile Header -->
    <div class="mb-4 md:mb-8">
      <div class="flex justify-between items-center mb-3">
        <h1 class="text-xl md:text-3xl font-bold">
          {{ isEditing ? 'Редактирование сметы' : 'Создание сметы' }}
        </h1>
        <router-link 
          :to="{name: 'dashboard'}" 
          class="flex items-center gap-2 text-gray-500 hover:text-blue-600 transition-colors px-3 py-2 rounded-lg hover:bg-gray-100"
        >
          <PhHouse :size="20" />
          <span class="hidden sm:inline text-sm">На главную</span>
        </router-link>
      </div>
      
      <!-- Mobile Stepper -->
      <div class="stepper hide-scrollbar">
        <div v-for="(s, i) in stepLabels" :key="i" class="stepper-item">
          <div 
            :class="[
              'stepper-circle', 
              step > i + 1 ? 'completed' : step === i + 1 ? 'active' : 'pending'
            ]"
          >
            <span v-if="step > i + 1">✓</span>
            <span v-else>{{ i + 1 }}</span>
          </div>
          <span class="stepper-label" :class="{ 'text-blue-600 font-semibold': step === i + 1 }">
            {{ s }}
          </span>
          <div 
            v-if="i < stepLabels.length - 1" 
            class="stepper-connector"
            :class="step > i + 1 ? 'bg-green-500' : 'bg-gray-300'"
          ></div>
        </div>
      </div>
    </div>
    
    <!-- Loading state for edit mode -->
    <div v-if="loadingEstimate" class="card md:p-6 text-center py-12">
      <div class="animate-spin text-4xl mb-2">⌛</div>
      <p class="text-gray-500">Загрузка сметы...</p>
    </div>

    <!-- Step Content -->
    <div v-else class="card md:p-6">
      <component :is="currentStepComponent" @next="nextStep" @prev="prevStep" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, onBeforeRouteLeave } from 'vue-router'
import { PhHouse } from '@phosphor-icons/vue'
import { useEstimateStore } from '@/stores/estimate'
import Step1Client from './Step1Client.vue'
import Step2Input from './Step2Input.vue'
import Step3Review from './Step3Review.vue' 
import Step4Pdf from './Step4Pdf.vue'

const route = useRoute()
const estimateStore = useEstimateStore()
const loadingEstimate = ref(false)

const step = ref(1)
const isEditing = computed(() => estimateStore.isEditing)

const stepLabels = ['Клиент', 'Замер', 'Проверка', 'PDF']

const steps = {
  1: Step1Client,
  2: Step2Input,
  3: Step3Review,
  4: Step4Pdf
}

const currentStepComponent = computed(() => steps[step.value] || Step1Client)

const nextStep = () => {
  if (step.value < 4) {
    step.value++
    estimateStore.currentStep = step.value
  }
}

const prevStep = () => {
  if (step.value > 1) {
    step.value--
    estimateStore.currentStep = step.value
  }
}

// Load existing estimate if editing
onMounted(async () => {
  const editId = route.params.id
  if (editId) {
    loadingEstimate.value = true
    try {
      await estimateStore.loadEstimate(editId)
      step.value = estimateStore.currentStep
    } catch (e) {
      alert('Ошибка загрузки сметы: ' + (e.message || 'Неизвестная ошибка'))
    } finally {
      loadingEstimate.value = false
    }
  }
})

// Auto-save draft when leaving the page
onBeforeRouteLeave(async (to, from, next) => {
  // Don't save if going to PDF step (step 4) or already completed
  if (step.value === 4) {
    next()
    return
  }
  
  try {
    await estimateStore.saveDraft()
  } catch (e) {
    console.error('Draft save error:', e)
  }
  next()
})
</script>
