<template>
  <svg 
    :class="[
      'plus-icon',
      sizeClass,
      colorClass
    ]"
    xmlns="http://www.w3.org/2000/svg" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    stroke-width="2" 
    stroke-linecap="round" 
    stroke-linejoin="round"
  >
    <path d="M5 12h14"></path>
    <path d="M12 5v14"></path>
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'blue' | 'white' | 'gray'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  variant: 'default'
})

const sizeClass = computed(() => {
  const sizes = {
    'sm': 'w-3 h-3',
    'md': 'w-4 h-4', 
    'lg': 'w-5 h-5'
  }
  return sizes[props.size]
})

const colorClass = computed(() => {
  const variants = {
    'default': 'text-current',
    'blue': 'text-blue-600',
    'white': 'text-white',
    'gray': 'text-gray-600'
  }
  return variants[props.variant]
})
</script>

<style scoped>
.plus-icon {
  stroke: currentColor !important;
  fill: none !important;
  stroke-width: 2 !important;
  stroke-linecap: round !important;
  stroke-linejoin: round !important;
  flex-shrink: 0;
  display: inline-block;
}

/* Ensure visibility in light mode */
.plus-icon {
  opacity: 1;
  visibility: visible;
}

/* Force stroke color inheritance */
.text-blue-600 .plus-icon,
.bg-blue-50 .plus-icon {
  stroke: #2563eb !important;
}

.text-white .plus-icon,
.bg-blue-600 .plus-icon {
  stroke: white !important;
}

.text-gray-600 .plus-icon {
  stroke: #4b5563 !important;
}
</style>
