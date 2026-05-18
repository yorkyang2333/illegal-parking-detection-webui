<template>
  <div ref="viewerRef" class="markdown-renderer" v-html="sanitizedHtml"></div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps<{
  content: string
}>()

const viewerRef = ref<HTMLDivElement>()

const sanitizedHtml = computed(() => {
  if (!props.content) return ''
  const rawHtml = marked(props.content)
  return DOMPurify.sanitize(rawHtml as string)
})

watch(() => props.content, async () => {
  await nextTick()
  if (viewerRef.value) {
    viewerRef.value.scrollTop = viewerRef.value.scrollHeight
  }
})
</script>

<style scoped lang="scss">
.markdown-renderer {
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-body);
  word-wrap: break-word;

  :deep(p) {
    margin-bottom: 0.6em;
  }

  :deep(h1),
  :deep(h2),
  :deep(h3),
  :deep(h4) {
    font-family: var(--font-display);
    font-weight: 400;
    color: var(--color-ink);
    margin-top: 1.2em;
    margin-bottom: 0.4em;
    letter-spacing: -0.3px;
  }

  :deep(h1) { font-size: 24px; }
  :deep(h2) { font-size: 20px; }
  :deep(h3) { font-size: 17px; }

  :deep(ul),
  :deep(ol) {
    margin-left: 20px;
    margin-bottom: 0.6em;
    padding-left: 0;
    list-style: disc;
  }

  :deep(ol) {
    list-style: decimal;
  }

  :deep(li) {
    margin-bottom: 0.3em;
  }

  :deep(code) {
    font-family: var(--font-mono);
    font-size: 13px;
    background: var(--color-surface-soft);
    padding: 2px 6px;
    border-radius: var(--radius-xs);
  }

  :deep(pre) {
    background: var(--color-surface-dark);
    color: var(--color-on-dark);
    padding: var(--space-md);
    border-radius: var(--radius-md);
    overflow-x: auto;
    margin-bottom: 0.8em;

    code {
      background: none;
      padding: 0;
      color: inherit;
    }
  }

  :deep(table) {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 0.8em;
    font-size: 13px;

    th, td {
      border: 1px solid var(--color-hairline);
      padding: 8px 12px;
      text-align: left;
    }

    th {
      background: var(--color-surface-soft);
      font-weight: 500;
      color: var(--color-ink);
    }
  }

  :deep(blockquote) {
    border-left: 3px solid var(--color-primary);
    padding-left: var(--space-md);
    margin: 0.8em 0;
    color: var(--color-muted);
  }

  :deep(strong) {
    font-weight: 500;
    color: var(--color-ink);
  }

  :deep(hr) {
    border: none;
    border-top: 1px solid var(--color-hairline);
    margin: 1.2em 0;
  }
}
</style>
