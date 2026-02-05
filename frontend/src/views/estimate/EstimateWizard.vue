<template>
  <div class="mobile-container safe-area-pt">
    <!-- Mobile Header -->
    <div class="mb-4 md:mb-8">
      <div class="flex justify-between items-center mb-3">
        <h1 class="text-xl md:text-3xl font-bold">Создание сметы</h1>
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
    
    <!-- Step Content -->
    <div class="card md:p-6">
      <component :is="currentStepComponent" @next="nextStep" @prev="prevStep" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { PhHouse } from '@phosphor-icons/vue'
import Step1Client from './Step1Client.vue'
import Step2Input from './Step2Input.vue'
import Step3Review from './Step3Review.vue' 
import Step4Pdf from './Step4Pdf.vue'

const step = ref(1)

const stepLabels = ['Клиент', 'Замер', 'Проверка', 'PDF']

const steps = {
  1: Step1Client,
  2: Step2Input,
  3: Step3Review,
  4: Step4Pdf
}

const currentStepComponent = computed(() => steps[step.value] || Step1Client)

const nextStep = () => {
  if (step.value < 4) step.value++
}

const prevStep = () => {
  if (step.value > 1) step.value--
}
</script>
