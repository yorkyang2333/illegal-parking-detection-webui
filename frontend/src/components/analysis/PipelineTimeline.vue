<template>
  <div class="timeline">
    <div
      v-for="step in steps"
      :key="step.id"
      class="timeline__step"
      :class="`timeline__step--${step.status}`"
    >
      <div class="timeline__indicator">
        <div class="timeline__dot">
          <Check v-if="step.status === 'completed'" :size="14" />
          <X v-else-if="step.status === 'error'" :size="14" />
          <span v-else-if="step.status === 'running'" class="timeline__spinner" />
          <span v-else class="timeline__number">{{ step.id }}</span>
        </div>
        <div v-if="step.id < steps.length" class="timeline__line" />
      </div>

      <div class="timeline__content">
        <h4 class="timeline__title">{{ step.title }}</h4>
        <p class="timeline__desc">{{ step.description }}</p>

        <div v-if="step.status === 'error' && step.error" class="timeline__error">
          {{ step.error }}
        </div>

        <div v-if="step.result && step.status !== 'pending'" class="timeline__result">
          <MarkdownRenderer :content="step.result" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Check, X } from 'lucide-vue-next'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import type { Step } from '@/stores/useAnalysisStore'

defineProps<{
  steps: Step[]
  currentStep: number
}>()
</script>

<style scoped lang="scss">
.timeline {
  display: flex;
  flex-direction: column;
}

.timeline__step {
  display: flex;
  gap: var(--space-md);
  padding-bottom: var(--space-lg);

  &:last-child {
    padding-bottom: 0;
  }
}

.timeline__indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.timeline__dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
  flex-shrink: 0;

  .timeline__step--pending & {
    background: var(--color-surface-card);
    color: var(--color-muted);
    border: 1px solid var(--color-hairline);
  }

  .timeline__step--running & {
    background: var(--color-primary);
    color: var(--color-on-primary);
  }

  .timeline__step--completed & {
    background: var(--color-success);
    color: white;
  }

  .timeline__step--error & {
    background: var(--color-error);
    color: white;
  }
}

.timeline__number {
  font-size: 12px;
}

.timeline__spinner {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.timeline__line {
  width: 2px;
  flex: 1;
  min-height: 16px;
  margin-top: var(--space-xs);
  background: var(--color-hairline);

  .timeline__step--completed & {
    background: var(--color-success);
  }
}

.timeline__content {
  flex: 1;
  min-width: 0;
  padding-top: 2px;
}

.timeline__title {
  font-size: 15px;
  font-weight: 500;
  color: var(--color-ink);
  margin-bottom: 2px;
}

.timeline__desc {
  font-size: 13px;
  color: var(--color-muted);
  margin-bottom: var(--space-sm);
}

.timeline__error {
  font-size: 13px;
  color: var(--color-error);
  padding: var(--space-sm) var(--space-md);
  background: rgba(198, 69, 69, 0.08);
  border-radius: var(--radius-md);
}

.timeline__result {
  background: var(--color-surface-card);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  font-size: 13px;
  max-height: 200px;
  overflow-y: auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
