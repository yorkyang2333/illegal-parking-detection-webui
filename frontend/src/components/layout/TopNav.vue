<template>
  <header class="top-nav">
    <div class="top-nav__inner">
      <div class="top-nav__left">
        <router-link to="/" class="top-nav__brand">
          <span class="top-nav__logo">✦</span>
          <span class="top-nav__title">车辆违停感知</span>
        </router-link>
      </div>

      <nav class="top-nav__links">
        <router-link to="/analysis" class="nav-link" active-class="nav-link--active">分析</router-link>
        <router-link to="/chat" class="nav-link" active-class="nav-link--active">对话</router-link>
        <router-link to="/history" class="nav-link" active-class="nav-link--active">历史</router-link>
      </nav>

      <div class="top-nav__right">
        <BaseDropdown align="right">
          <template #trigger>
            <button class="user-trigger">
              <span class="user-avatar">{{ userInitial }}</span>
              <ChevronDown :size="14" />
            </button>
          </template>
          <router-link to="/settings" class="dropdown-item">
            <Settings :size="16" />
            <span>设置</span>
          </router-link>
          <button class="dropdown-item dropdown-item--danger" @click="handleLogout">
            <LogOut :size="16" />
            <span>退出登录</span>
          </button>
        </BaseDropdown>
      </div>

      <button class="top-nav__hamburger" @click="mobileMenuOpen = !mobileMenuOpen">
        <Menu :size="22" />
      </button>
    </div>

    <Transition name="slide">
      <div v-if="mobileMenuOpen" class="mobile-menu">
        <router-link to="/analysis" class="mobile-menu__link" @click="mobileMenuOpen = false">分析</router-link>
        <router-link to="/chat" class="mobile-menu__link" @click="mobileMenuOpen = false">对话</router-link>
        <router-link to="/history" class="mobile-menu__link" @click="mobileMenuOpen = false">历史</router-link>
        <router-link to="/settings" class="mobile-menu__link" @click="mobileMenuOpen = false">设置</router-link>
        <button class="mobile-menu__link mobile-menu__link--danger" @click="handleLogout">退出登录</button>
      </div>
    </Transition>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronDown, Settings, LogOut, Menu } from 'lucide-vue-next'
import BaseDropdown from '@/components/ui/BaseDropdown.vue'
import { useAuthStore } from '@/stores/useAuthStore'

const router = useRouter()
const authStore = useAuthStore()
const mobileMenuOpen = ref(false)

const userInitial = computed(() => {
  return authStore.user?.username?.charAt(0).toUpperCase() || 'U'
})

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped lang="scss">
.top-nav {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--color-canvas);
  border-bottom: 1px solid var(--color-hairline-soft);
}

.top-nav__inner {
  display: flex;
  align-items: center;
  height: var(--nav-height);
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: 0 var(--space-lg);
}

.top-nav__left {
  flex-shrink: 0;
}

.top-nav__brand {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.top-nav__logo {
  font-size: 20px;
  color: var(--color-primary);
}

.top-nav__title {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 400;
  letter-spacing: -0.3px;
  color: var(--color-ink);
}

.top-nav__links {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  margin-left: var(--space-xxl);

  @media (max-width: 767px) {
    display: none;
  }
}

.nav-link {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-muted);
  padding: 8px 14px;
  border-radius: var(--radius-md);
  transition: color 0.15s, background-color 0.15s;

  &:hover {
    color: var(--color-ink);
    background: var(--color-surface-soft);
  }

  &--active {
    color: var(--color-ink);
    background: var(--color-surface-card);
  }
}

.top-nav__right {
  margin-left: auto;

  @media (max-width: 767px) {
    display: none;
  }
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: 6px 10px;
  border-radius: var(--radius-md);
  color: var(--color-muted);

  &:hover {
    background: var(--color-surface-soft);
    color: var(--color-ink);
  }
}

.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--color-surface-card);
  color: var(--color-ink);
  font-size: 13px;
  font-weight: 500;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  width: 100%;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--color-body);
  transition: background-color 0.1s;

  &:hover {
    background: var(--color-surface-soft);
  }

  &--danger {
    color: var(--color-error);
  }
}

.top-nav__hamburger {
  display: none;
  margin-left: auto;
  color: var(--color-ink);
  padding: 8px;
  border-radius: var(--radius-md);

  @media (max-width: 767px) {
    display: flex;
  }

  &:hover {
    background: var(--color-surface-soft);
  }
}

.mobile-menu {
  display: flex;
  flex-direction: column;
  padding: var(--space-md) var(--space-lg);
  border-top: 1px solid var(--color-hairline-soft);

  @media (min-width: 768px) {
    display: none;
  }
}

.mobile-menu__link {
  display: block;
  padding: 12px 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--color-body);
  border-bottom: 1px solid var(--color-hairline-soft);

  &--danger {
    color: var(--color-error);
    border-bottom: none;
    text-align: left;
    width: 100%;
  }
}

.slide-enter-active,
.slide-leave-active {
  transition: max-height 0.2s ease, opacity 0.2s ease;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
}

.slide-enter-to,
.slide-leave-from {
  max-height: 300px;
  opacity: 1;
}
</style>
