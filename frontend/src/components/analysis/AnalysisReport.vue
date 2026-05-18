<template>
  <div class="report">
    <div class="report__header">
      <h3 class="report__title">分析报告</h3>
      <BaseBadge variant="success">已完成</BaseBadge>
    </div>
    <div class="report__body">
      <MarkdownRenderer :content="content" />
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseBadge from '@/components/ui/BaseBadge.vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'

defineProps<{
  content: string
}>()
</script>

<style scoped lang="scss">
.report {
  background: var(--color-surface-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.report__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-lg) var(--space-xl);
  border-bottom: 1px solid var(--color-hairline-soft);
}

.report__title {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 400;
  letter-spacing: -0.3px;
  color: var(--color-ink);
}

.report__body {
  padding: var(--space-xl);
  max-height: 500px;
  overflow-y: auto;
}
</style>
