import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/index.css'

import PhosphorIcons from "@phosphor-icons/vue"

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Register Phosphor Icons globally if needed or let components import them
// For now let's not register all of them to save bundle size, but use the plugin if available or just skip global reg.
// The task_viso.md suggested a plugin approach. Let's implementing a simple plugin for it or just use imports.
// Keeping it simple for now.

app.mount('#app')
