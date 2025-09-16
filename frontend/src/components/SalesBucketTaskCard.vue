<template>
  <div class="bg-white rounded-lg border border-outline-gray-2 shadow-sm hover:shadow-md transition-shadow duration-200">
    <div class="p-6">
      <!-- Header -->
      <div class="flex items-start justify-between mb-4">
        <div class="flex-1">
          <h3 class="text-lg font-medium text-ink-gray-9 mb-1">{{ task.title }}</h3>
          <div class="flex items-center gap-2 text-sm text-ink-gray-6">
            <span>{{ task.customer_title }}</span>
            <span>•</span>
            <span>{{ task.artwork_title }}</span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span 
            :class="getPriorityClass(task.priority)"
            class="px-2 py-1 text-xs font-medium rounded-full"
          >
            {{ task.priority }}
          </span>
          <span 
            class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800"
          >
            Sales Complete
          </span>
        </div>
      </div>

      <!-- Description -->
      <div v-if="task.description" class="mb-4">
        <p class="text-sm text-ink-gray-7 line-clamp-3">{{ task.description }}</p>
      </div>

      <!-- Metadata -->
      <div class="flex items-center justify-between text-xs text-ink-gray-5 mb-4">
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-1">
            <LucideUser class="size-3" />
            <span>{{ task.created_by_sales_name || 'Unknown' }}</span>
          </div>
          <div class="flex items-center gap-1">
            <LucideClock class="size-3" />
            <span>{{ formatDate(task.modified) }}</span>
          </div>
        </div>
        <div v-if="task.last_status_change" class="flex items-center gap-1">
          <LucideHistory class="size-3" />
          <span>Last changed {{ formatDate(task.last_status_change) }}</span>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Button 
            @click="$emit('view', task)"
            class="bg-surface-white border border-outline-gray-2 text-ink-gray-7 hover:bg-surface-gray-1 text-sm"
          >
            <template #prefix>
              <LucideEye class="size-4" />
            </template>
            View Details
          </Button>
        </div>
        <div class="text-xs text-ink-gray-5">
          Task #{{ task.name }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Button } from 'frappe-ui'
import LucideUser from '~icons/lucide/user'
import LucideClock from '~icons/lucide/clock'
import LucideHistory from '~icons/lucide/history'
import LucideEye from '~icons/lucide/eye'

interface Task {
  name: string
  title: string
  status: string
  priority: string
  created_by_sales_name?: string
  modified: string
  last_status_change?: string
  customer_title?: string
  artwork_title?: string
  description?: string
}

interface Props {
  task: Task
}

const props = defineProps<Props>()

defineEmits(['view'])

const getPriorityClass = (priority: string) => {
  const classes = {
    'Low': 'bg-ink-gray-1 text-ink-gray-7',
    'Medium': 'bg-blue-50 text-blue-700',
    'High': 'bg-orange-50 text-orange-700',
    'Urgent': 'bg-red-50 text-red-700'
  }
  return classes[priority] || classes['Medium']
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'Unknown'
  
  const date = new Date(dateString)
  const now = new Date()
  const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
  
  if (diffInHours < 1) {
    return 'Just now'
  } else if (diffInHours < 24) {
    return `${diffInHours}h ago`
  } else if (diffInHours < 168) { // 7 days
    const days = Math.floor(diffInHours / 24)
    return `${days}d ago`
  } else {
    return date.toLocaleDateString()
  }
}
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
