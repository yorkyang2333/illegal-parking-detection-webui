<template>
  <div class="violation-card" @click="emit('jump', record.best_frame_index)">
    <div class="violation-card__header">
      <span class="violation-card__id">车辆 #{{ record.track_id }}</span>
      <span class="violation-card__type-badge">{{ record.vehicle_class }}</span>
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

    <div class="violation-card__jump-hint">点击跳转至违停帧</div>
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
  background: var(--color-canvas, #faf9f5);
  border: 1px solid var(--color-hairline, #d9d3c8);
  border-left: 3px solid var(--color-error, #d94f4f);
  border-radius: var(--radius-lg, 12px);
  padding: var(--space-md, 16px) var(--space-lg, 20px);
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  position: relative;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);

    .violation-card__jump-hint {
      opacity: 1;
    }
  }

  &__header {
    display: flex;
    align-items: center;
    gap: var(--space-sm, 8px);
    margin-bottom: var(--space-xs, 6px);
  }

  &__id {
    font-family: var(--font-mono, monospace);
    font-size: 11px;
    color: var(--color-muted, #a09a8e);
    letter-spacing: 0.5px;
  }

  &__type-badge {
    font-size: 11px;
    background: var(--color-surface-card, #efe9de);
    color: var(--color-body, #5c574f);
    padding: 2px 8px;
    border-radius: 20px;
    font-family: var(--font-mono, monospace);
  }

  &__plate {
    font-family: var(--font-mono, monospace);
    font-size: 20px;
    font-weight: 500;
    color: var(--color-ink, #1a1916);
    letter-spacing: 1.5px;
    margin-bottom: var(--space-sm, 8px);
  }

  &__meta {
    display: flex;
    align-items: baseline;
    gap: 6px;
    margin-bottom: var(--space-xs, 6px);
  }

  &__meta-label {
    font-size: 11px;
    color: var(--color-muted, #a09a8e);
  }

  &__duration {
    font-size: 14px;
    font-weight: 500;
    color: var(--color-error, #d94f4f);
    font-family: var(--font-mono, monospace);
  }

  &__reason {
    font-size: 13px;
    color: var(--color-body, #5c574f);
    line-height: 1.5;
    margin: 0 0 var(--space-xs, 6px);
  }

  &__context {
    font-size: 12px;
    color: var(--color-muted, #a09a8e);
    background: var(--color-surface-card, #efe9de);
    border-radius: 6px;
    padding: 6px 10px;
    line-height: 1.5;
    margin-bottom: var(--space-xs, 6px);
  }

  &__jump-hint {
    font-size: 11px;
    color: var(--color-primary, #cc785c);
    opacity: 0;
    transition: opacity 0.18s;
    text-align: right;
    margin-top: 4px;
  }
}
</style>
