import { defineStore } from 'pinia'
import { ref } from 'vue'

export type PageType = 'input' | 'output'

export const useUiStore = defineStore('ui', () => {
  const currentPage = ref<PageType>('input')
  const outputNotification = ref(false)

  function navigateToPage(page: PageType) {
    currentPage.value = page
    if (page === 'output') {
      clearOutputNotification()
    }
  }

  function showOutputNotification() {
    if (currentPage.value !== 'output') {
      outputNotification.value = true
    }
  }

  function clearOutputNotification() {
    outputNotification.value = false
  }

  return {
    currentPage,
    outputNotification,
    navigateToPage,
    showOutputNotification,
    clearOutputNotification
  }
})
