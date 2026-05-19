<template>
  <div class="progress-bar">
    <div
      v-for="(phase, index) in phases"
      :key="phase.id"
      class="progress-bar__step"
    >
      <!-- Connector line (before each step except the first) -->
      <div
        v-if="index > 0"
        class="progress-bar__line"
        :class="{ 'progress-bar__line--done': phases[index - 1].status === 'done' }"
      />

      <div class="progress-bar__node-wrap">
        <div
          class="progress-bar__node"
          :class="`progress-bar__node--${phase.status}`"
        >
          <!-- Running: spinner -->
          <svg
            v-if="phase.status === 'running'"
            class="progress-bar__spinner"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
          </svg>
          <!-- Done: check -->
          <svg
            v-else-if="phase.status === 'done'"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
          <!-- Error: X -->
          <svg
            v-else-if="phase.status === 'error'"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
          <!-- Pending: icon -->
          <component v-else :is="phaseIcons[index]" :size="16" />
        </div>
        <span class="progress-bar__label">{{ phase.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ScanSearch, Car, BrainCircuit, FileText } from 'lucide-vue-next'
import type { AgentPhase } from '@/stores/useAgentStore'

defineProps<{ phases: AgentPhase[] }>()

const phaseIcons = [ScanSearch, Car, BrainCircuit, FileText]
</script>

<style scoped lang="scss">
.progress-bar {
  display: flex;
  align-items: flex-start;
  background: var(--color-surface-card, #efe9de);
  border-radius: var(--radius-lg, 12px);
  padding: var(--space-md, 12px) var(--space-lg, 24px);

  &__step {
    display: flex;
    align-items: flex-start;
    flex: 1;
    position: relative;
  }

  &__line {
    position: absolute;
    top: 18px;
    right: calc(50% + 18px);
    left: calc(-50% + 18px);
    height: 2px;
    background: var(--color-hairline, #d9d3c8);
    transition: background 0.3s;

    &--done {
      background: var(--color-success, #5aac73);
    }
  }

  &__node-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    flex: 1;
    position: relative;
    z-index: 1;
  }

  &__node {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.3s, border-color 0.3s, color 0.3s;
    flex-shrink: 0;

    svg {
      width: 16px;
      height: 16px;
    }

    &--pending {
      border: 1.5px solid var(--color-hairline, #d9d3c8);
      background: transparent;
      color: var(--color-muted, #a09a8e);
    }

    &--running {
      background: var(--color-primary, #cc785c);
      border: none;
      color: #fff;

      .progress-bar__spinner {
        animation: spin 1s linear infinite;
      }
    }

    &--done {
      background: var(--color-success, #5aac73);
      border: none;
      color: #fff;
    }

    &--error {
      background: var(--color-error, #d94f4f);
      border: none;
      color: #fff;
    }
  }

  &__label {
    font-size: 11px;
    color: var(--color-muted, #a09a8e);
    text-align: center;
    white-space: nowrap;
    transition: color 0.3s;
  }

  &__step:has(.progress-bar__node--running) .progress-bar__label {
    color: var(--color-primary, #cc785c);
    font-weight: 500;
  }

  &__step:has(.progress-bar__node--done) .progress-bar__label {
    color: var(--color-success, #5aac73);
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
