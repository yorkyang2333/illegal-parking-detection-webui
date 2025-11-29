<template>
  <div ref="viewerRef" class="markdown-viewer" v-html="sanitizedHtml"></div>
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

// Auto-scroll to bottom when content updates
watch(() => props.content, async () => {
  await nextTick()
  if (viewerRef.value) {
    viewerRef.value.scrollTop = viewerRef.value.scrollHeight
  }
})
</script>

<style scoped lang="scss">
.markdown-viewer {
  background-color: #f0f2f5;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  overflow-y: auto;
  word-wrap: break-word;
  font-size: 14px;
  line-height: 1.6;
  flex-grow: 1;
  max-height: 600px;
  min-height: 200px;

  :deep(p) {
    margin-bottom: 0.5em;
    margin-top: 0;
  }

  :deep(h1),
  :deep(h2),
  :deep(h3) {
    margin-top: 1em;
    margin-bottom: 0.5em;
    color: #1c1e21;
  }

  :deep(ul),
  :deep(ol) {
    margin-left: 20px;
  }

  :deep(code) {
    background-color: #f4f4f4;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    word-break: break-word;
  }

  :deep(pre) {
    background-color: #f4f4f4;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
    max-width: 100%;

    code {
      word-break: normal;
      white-space: pre;
    }
  }

  :deep(table) {
    width: 100%;
    border-collapse: collapse;
    overflow-x: auto;
    display: block;
    max-width: 100%;

    th,
    td {
      border: 1px solid #e0e0e0;
      padding: 8px;
      text-align: left;
    }

    th {
      background-color: #f4f4f4;
      font-weight: 600;
    }
  }

  :deep(img) {
    max-width: 100%;
    height: auto;
  }
}

/* 响应式设计 */

/* 移动端 (<768px) */
@media (max-width: 767px) {
  .markdown-viewer {
    padding: 15px;
    font-size: 13px;
    max-height: 500px;

    :deep(h1) {
      font-size: 1.5em;
    }

    :deep(h2) {
      font-size: 1.3em;
    }

    :deep(h3) {
      font-size: 1.1em;
    }

    :deep(pre) {
      padding: 8px;
      font-size: 12px;
    }

    :deep(table) {
      font-size: 12px;

      th,
      td {
        padding: 6px;
      }
    }

    :deep(ul),
    :deep(ol) {
      margin-left: 15px;
      padding-left: 5px;
    }
  }
}

/* 平板 (768px-1024px) */
@media (min-width: 768px) and (max-width: 1023px) {
  .markdown-viewer {
    padding: 18px;
    font-size: 13px;
  }
}

/* 桌面 (>=1024px) - 保持原有样式 */
@media (min-width: 1024px) {
  .markdown-viewer {
    padding: 20px;
    font-size: 14px;
  }
}
</style>
