<template>
  <div class="violation-card" @click="emit('jump', record.best_frame_index)">
    <div class="violation-card__header">
      <span class="violation-card__id">Vehicle #{{ record.track_id }}</span>
      <span class="badge-pill">{{ record.vehicle_class }}</span>
      <span class="badge-coral">VIOLATION</span>
    </div>

    <div class="violation-card__plate">{{ record.license_plate || '未识别' }}</div>

    <div class="violation-card__meta">
      <span class="violation-card__meta-label">停留时长</span>
      <span class="violation-card__duration">{{ formatDuration(record.stationary_duration_sec) }}</span>
    </div>

    <p class="violation-card__reason">{{ record.violation_reason }}</p>

    <div v-if="record.scene_context" class="violation-card__context">
      {{ record.scene_context }}
    </div>

    <div class="violation-card__jump-hint">点击跳转至违停帧 →</div>
  </div>
</template>

<script setup lang="ts">
import type { ViolationRecord } from '@/stores/useAgentStore'

defineProps<{ record: ViolationRecord }>()
const emit = defineEmits<{ jump: [frameIndex: number] }>()

function formatDuration(sec: number): string {
  if (sec < 60) return `${Math.round(sec)} 秒`
  const m = Math.floor(sec / 60)
  const s = Math.round(sec % 60)
  return s > 0 ? `${m} 分 ${s} 秒` : `${m} 分钟`
}
</script>

<style scoped lang="scss">
.violation-card {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  cursor: pointer;
  transition: transform 0.15s ease, background-color 0.15s ease;
  position: relative;

  &:hover {
    background: var(--color-surface-soft);
    .violation-card__jump-hint {
      opacity: 1;
    }
  }

  &__header {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--space-xs);
    margin-bottom: var(--space-sm);
  }

  &__id {
    font-family: var(--font-mono);
    font-size: 13px;
    color: var(--color-muted);
    letter-spacing: 0.5px;
    margin-right: auto;
  }

  .badge-pill {
    font-size: 11px;
    background: var(--color-surface-card);
    color: var(--color-ink);
    padding: 2px 10px;
    border-radius: var(--radius-pill);
    font-family: var(--font-mono);
  }

  .badge-coral {
    font-size: 11px;
    background: var(--color-primary);
    color: var(--color-on-primary);
    padding: 2px 10px;
    border-radius: var(--radius-pill);
    font-family: var(--font-mono);
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  &__plate {
    font-family: var(--font-display);
    font-size: 28px;
    font-weight: 400;
    color: var(--color-ink);
    letter-spacing: -0.3px;
    margin-bottom: var(--space-md);
  }

  &__meta {
    display: flex;
    align-items: baseline;
    gap: var(--space-xs);
    margin-bottom: var(--space-sm);
  }

  &__meta-label {
    font-size: 13px;
    color: var(--color-muted);
  }

  &__duration {
    font-size: 16px;
    font-weight: 500;
    color: var(--color-error);
    font-family: var(--font-mono);
  }

  &__reason {
    font-size: 14px;
    color: var(--color-body);
    line-height: 1.55;
    margin: 0 0 var(--space-sm);
  }

  &__context {
    font-size: 13px;
    color: var(--color-muted-soft);
    background: transparent;
    border-left: 2px solid var(--color-hairline);
    padding-left: var(--space-sm);
    line-height: 1.55;
    margin-bottom: var(--space-md);
  }

  &__jump-hint {
    font-size: 13px;
    font-weight: 500;
    color: var(--color-primary);
    opacity: 0;
    transition: opacity 0.15s;
    text-align: right;
    margin-top: var(--space-sm);
  }
}
</style>
