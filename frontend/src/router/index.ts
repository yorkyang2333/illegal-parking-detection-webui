import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'
import LoginPage from '@/views/LoginPage.vue'
import RegisterPage from '@/views/RegisterPage.vue'
import AnalysisPage from '@/views/AnalysisPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/analysis',
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { requiresAuth: false },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterPage,
      meta: { requiresAuth: false },
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: AnalysisPage,
      meta: { requiresAuth: true },
    },
    // 兼容旧的 /chat 路由
    {
      path: '/chat',
      redirect: '/analysis',
    },
  ],
})

// Navigation guard
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    // Redirect to login if not authenticated
    next({ name: 'login' })
  } else if (!requiresAuth && authStore.isAuthenticated && (to.name === 'login' || to.name === 'register')) {
    // Redirect to analysis if already logged in and trying to access login/register
    next({ name: 'analysis' })
  } else {
    next()
  }
})

export default router

