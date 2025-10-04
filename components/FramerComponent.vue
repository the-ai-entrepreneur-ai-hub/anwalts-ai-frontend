<template>
  <div ref="containerRef"></div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'

interface Props {
  component: any
  props?: Record<string, any>
}

const props = defineProps<Props>()
const containerRef = ref<HTMLElement>()

onMounted(async () => {
  if (process.client && containerRef.value && props.component) {
    const { createRoot } = await import('react-dom/client')
    const { createElement } = await import('react')
    
    const root = createRoot(containerRef.value)
    root.render(createElement(props.component, props.props || {}))
  }
})
</script>