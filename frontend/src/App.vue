<template>
  <AppLayout>
    <InputPage v-if="uiStore.currentPage === 'input'" />
    <OutputPage v-if="uiStore.currentPage === 'output'" />
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '@/components/layout/AppLayout.vue'
import InputPage from '@/views/InputPage.vue'
import OutputPage from '@/views/OutputPage.vue'
import { useUiStore } from '@/stores/useUiStore'

const uiStore = useUiStore()
</script>

<style scoped lang="scss">
</style>
