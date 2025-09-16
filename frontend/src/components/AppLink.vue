<template>
  <a v-if="isExternalLink" v-bind="$attrs" :href="props.to" target="_blank">
    <slot />
  </a>
  <RouterLink
    v-else-if="hasValidRoute"
    v-bind="$props"
    custom
    :to="props.to"
    v-slot="{ isActive: slotIsActive, href, navigate }"
  >
    <a
      v-bind="$attrs"
      class="focus:outline-none focus-visible:ring focus-visible:ring-gray-400"
      :href="href"
      @click="navigate"
      :class="computedIsActive(slotIsActive) ? activeClass : inactiveClass"
    >
      <slot />
    </a>
  </RouterLink>
  <span
    v-else
    v-bind="$attrs"
    :class="inactiveClass"
  >
    <slot />
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

defineOptions({
  inheritAttrs: false,
})

const props = defineProps({
  // @ts-ignore
  ...RouterLink.props,
  inactiveClass: String,
  isActive: {
    type: Boolean,
    default: undefined,
  },
})

const computedIsActive = (slotIsActive: boolean) => {
  if (props.isActive !== undefined) {
    return props.isActive
  }
  return slotIsActive
}

const isExternalLink = computed(() => {
  return typeof props.to === 'string' && props.to.startsWith('http')
})

const hasValidRoute = computed(() => {
  // If to is undefined, null, or empty, don't render as router link
  if (!props.to) return false
  
  // If to is a string, check if it's a valid route
  if (typeof props.to === 'string') {
    // Allow external links (handled by isExternalLink)
    if (props.to.startsWith('http')) return false
    // Allow internal routes that start with /
    return props.to.startsWith('/')
  }
  
  // If to is an object, it should have a name or path property
  if (typeof props.to === 'object' && props.to !== null) {
    return !!(props.to.name || props.to.path)
  }
  
  return false
})
</script>
