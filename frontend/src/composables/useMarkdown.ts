import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

export function useMarkdown(content: string | (() => string)) {
  const sanitizedHtml = computed(() => {
    const text = typeof content === 'function' ? content() : content
    if (!text) return ''
    const rawHtml = marked(text)
    return DOMPurify.sanitize(rawHtml as string)
  })

  return { sanitizedHtml }
}
