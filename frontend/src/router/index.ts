import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'
import LoginPage from '@/views/LoginPage.vue'
import RegisterPage from '@/views/RegisterPage.vue'
import InputPage from '@/views/InputPage.vue'
import OutputPage from '@/views/OutputPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/input',
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
      path: '/input',
      name: 'input',
      component: InputPage,
      meta: { requiresAuth: true },
    },
    {
      path: '/output',
      name: 'output',
      component: OutputPage,
      meta: { requiresAuth: true },
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
    // Redirect to input if already logged in and trying to access login/register
    next({ name: 'input' })
  } else {
    next()
  }
})

export default router
