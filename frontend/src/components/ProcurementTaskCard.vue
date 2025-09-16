<template>
  <div
    :class="[
      'p-3 rounded-lg border transition-all duration-300 cursor-pointer hover:shadow-md group',
      getTaskCardClasses(task, stageKey),
      { 'animate-drop-to-bucket': isDroppingToBucket }
    ]"
    @click="handleTaskClick"
  >
    <div class="flex items-start justify-between">
      <div class="flex-1 min-w-0">
        <h4 class="text-sm font-medium text-gray-900 truncate">{{ task.title }}</h4>
        <p class="text-xs text-gray-500 mt-1">{{ task.customer_title }}</p>
        <div class="flex items-center gap-2 mt-2 flex-wrap">
          <span 
            :class="[
              'px-2 py-1 text-xs rounded-full',
              getPriorityClasses(task.priority)
            ]"
          >
            {{ task.priority }}
          </span>
          <span class="text-xs text-gray-400">{{ formatDate(task.modified) }}</span>
          <span v-if="task.cycle_count && task.cycle_count > 0" class="text-xs text-gray-400">
            • Cycle #{{ task.cycle_count }}
          </span>
        </div>
      </div>
      <div class="ml-2 flex-shrink-0">
        <LucideChevronRight class="size-4 text-gray-400 group-hover:text-gray-600 transition-colors" />
      </div>
    </div>
    
    <!-- Drop Animation Overlay -->
    <Transition
      enter-active-class="transform ease-out duration-500 transition"
      enter-from-class="opacity-0 scale-50 translate-y-4"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-50"
    >
      <div 
        v-if="showDropAnimation"
        class="absolute inset-0 bg-green-100 border-2 border-green-300 rounded-lg flex items-center justify-center"
      >
        <div class="text-center">
          <LucideCheckCircle class="size-6 text-green-600 mx-auto mb-2" />
          <p class="text-sm font-medium text-green-800">Moving to Bucket...</p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { formatDistanceToNow } from 'date-fns'
import LucideChevronRight from '~icons/lucide/chevron-right'
import LucideCheckCircle from '~icons/lucide/check-circle'

interface Task {
  name: string
  title: string
  customer_title: string
  priority: string
  modified: string
  cycle_count?: number
  status: string
}

interface Props {
  task: Task
  stageKey: string
  isDroppingToBucket?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: [task: Task]
}>()

// State
const showDropAnimation = ref(false)

// Computed properties
const getTaskCardClasses = (task, stageKey) => {
  const baseClasses = 'bg-white border-gray-200 hover:border-gray-300 relative'
  
  if (stageKey === 'final_approved') {
    return baseClasses + ' border-green-200 bg-green-50 hover:bg-green-100'
  }
  
  if (stageKey === 'procurement_rework') {
    return baseClasses + ' border-orange-200 bg-orange-50 hover:bg-orange-100'
  }
  
  if (stageKey === 'procurement_review') {
    return baseClasses + ' border-blue-200 bg-blue-50 hover:bg-blue-100'
  }
  
  return baseClasses
}

const getPriorityClasses = (priority) => {
  const classes = {
    'Low': 'bg-gray-100 text-gray-800',
    'Medium': 'bg-blue-100 text-blue-800',
    'High': 'bg-orange-100 text-orange-800',
    'Urgent': 'bg-red-100 text-red-800'
  }
  return classes[priority] || 'bg-gray-100 text-gray-800'
}

const formatDate = (dateString) => {
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true })
  } catch {
    return dateString
  }
}

const handleTaskClick = () => {
  emit('click', props.task)
}

// Watch for drop animation trigger
watch(() => props.isDroppingToBucket, (newValue) => {
  if (newValue) {
    showDropAnimation.value = true
    
    // Hide animation after it completes
    setTimeout(() => {
      showDropAnimation.value = false
    }, 1000)
  }
})
</script>

<style scoped>
/* Drop to bucket animation */
@keyframes dropToBucket {
  0% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
  50% {
    transform: translateY(-20px) scale(1.05);
    opacity: 0.8;
  }
  100% {
    transform: translateY(40px) scale(0.8);
    opacity: 0;
  }
}

.animate-drop-to-bucket {
  animation: dropToBucket 0.6s ease-in-out forwards;
}

/* Smooth transitions */
.transition-all {
  transition: all 0.3s ease-out;
}
</style>
