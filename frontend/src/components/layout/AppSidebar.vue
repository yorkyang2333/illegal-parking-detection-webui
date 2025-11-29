<template>
  <aside class="app-sidebar">
    <ul class="sidebar-nav">
      <li>
        <a
          href="https://gemini.google.com"
          target="_blank"
          rel="noopener noreferrer"
          class="sidebar-link"
        >
          <img
            src="/assets/gemini_logo.svg"
            class="sidebar-icon"
            alt="Gemini"
          >
          <span class="sidebar-text">
            Gemini
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="1em"
              height="1em"
              viewBox="0 0 24 24"
              fill="transparent"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="external-icon"
            >
              <path d="M21 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h6"></path>
              <path d="m21 3-9 9"></path>
              <path d="M15 3h6v6"></path>
            </svg>
          </span>
        </a>
      </li>

      <li>
        <a
          href="https://chat.qwen.ai"
          target="_blank"
          rel="noopener noreferrer"
          class="sidebar-link"
        >
          <img
            src="/assets/qwen_logo.svg"
            class="sidebar-icon"
            alt="Qwen"
          >
          <span class="sidebar-text">
            Qwen Chat
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="1em"
              height="1em"
              viewBox="0 0 24 24"
              fill="transparent"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="external-icon"
            >
              <path d="M21 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h6"></path>
              <path d="m21 3-9 9"></path>
              <path d="M15 3h6v6"></path>
            </svg>
          </span>
        </a>
      </li>

      <li>
        <a
          href="#"
          class="sidebar-link"
          :class="{ active: uiStore.currentPage === 'input' }"
          @click.prevent="uiStore.navigateToPage('input')"
        >
          <el-icon class="sidebar-icon"><Edit /></el-icon>
          <span class="sidebar-text">输入页</span>
        </a>
      </li>

      <li>
        <a
          href="#"
          class="sidebar-link"
          :class="{ active: uiStore.currentPage === 'output' }"
          @click.prevent="uiStore.navigateToPage('output')"
        >
          <el-icon class="sidebar-icon">
            <DataAnalysis />
          </el-icon>
          <span class="sidebar-text">输出页</span>
          <span v-if="uiStore.outputNotification" class="notification-badge"></span>
        </a>
      </li>
    </ul>
  </aside>
</template>

<script setup lang="ts">
import { Edit, DataAnalysis } from '@element-plus/icons-vue'
import { useUiStore } from '@/stores/useUiStore'

const uiStore = useUiStore()
</script>

<style scoped lang="scss">
.app-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  width: 60px;
  height: 100vh;
  background-color: #f8f9fa;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  transition: width 0.3s ease;
  overflow-x: hidden;
  z-index: 1000;

  &:hover {
    width: 200px;

    .sidebar-text {
      opacity: 1;
    }
  }
}

.sidebar-nav {
  list-style: none;
  padding: 0;
  margin: 0;

  li {
    display: flex;
    align-items: center;
  }
}

.sidebar-link {
  display: flex;
  align-items: center;
  padding: 15px 18px;
  color: #333;
  text-decoration: none;
  transition: background-color 0.2s ease;
  width: 100%;
  position: relative;

  &:hover {
    background-color: #e4e6eb;
  }

  &.active {
    color: #1877f2;
    border-bottom: 2px solid #1877f2;
  }
}

.sidebar-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.sidebar-text {
  opacity: 0;
  transition: opacity 0.1s ease;
  margin-left: 15px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 4px;
}

.external-icon {
  width: 1em;
  height: 1em;
}

.notification-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 10px;
  height: 10px;
  background-color: red;
  border-radius: 50%;
  z-index: 10;
}
</style>
