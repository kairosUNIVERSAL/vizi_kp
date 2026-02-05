import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
    {
        path: '/login',
        name: 'login',
        component: () => import('@/views/auth/LoginView.vue'),
        meta: { public: true }
    },
    {
        path: '/register',
        name: 'register',
        component: () => import('@/views/auth/RegisterView.vue'),
        meta: { public: true }
    },
    {
        path: '/',
        name: 'dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
    },
    {
        path: '/estimate/new',
        name: 'estimate-new',
        component: () => import('@/views/estimate/EstimateWizard.vue'),
    },
    {
        path: '/prices',
        name: 'prices',
        component: () => import('@/views/price/PriceListView.vue'),
    },
    {
        path: '/estimate/:id',
        name: 'estimate-view',
        component: () => import('@/views/estimate/EstimateDetailView.vue'),
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    if (!to.meta.public && !authStore.isAuthenticated) {
        next({ name: 'login' })
    } else {
        next()
    }
})

export default router
