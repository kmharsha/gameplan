<template>
  <div
    class="bg-white/95 backdrop-blur-sm p-4 rounded-xl border transition-all duration-300 group hover:shadow-lg hover:shadow-green-500/10 hover:-translate-y-0.5 hover:bg-white"
    :class="[
      { 'opacity-50 scale-95': isDragging },
      getCustomerBorderClass(task.customer)
    ]"
    draggable="true"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
  >
    <!-- Task Title -->
    <div class="flex items-center justify-between mb-2">
      <h4 class="font-medium text-ink-gray-9 line-clamp-2 flex-1">{{ task.title }}</h4>
      <!-- Source Badge -->
      <div class="ml-2 flex-shrink-0">
        <div class="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full border border-green-200">
          <LucideCheckCircle class="size-3 inline mr-1" />
          Sales Complete
        </div>
      </div>
    </div>
    
    <!-- Task Meta Info -->
    <div class="flex items-center justify-between text-xs text-ink-gray-6 mb-3">
      <span class="bg-surface-gray-1 px-2 py-1 rounded">{{ task.name }}</span>
      <span>{{ formatDate(task.modified) }}</span>
    </div>
    
    <!-- Customer Badge -->
    <div v-if="task.customer_title" class="mb-3">
      <div class="inline-flex items-center gap-1 px-2 py-1 text-xs bg-indigo-50 text-indigo-700 rounded-full border border-indigo-200">
        <LucideBuilding2 class="size-3" />
        <span class="font-medium">{{ task.customer_title }}</span>
      </div>
    </div>

    <!-- Priority and Workflow Badges -->
    <div class="flex items-center gap-2 mb-3 flex-wrap">
      <div 
        :class="[
          'px-2 py-1 text-xs rounded-full',
          PRIORITY_COLORS[task.priority] || 'bg-ink-gray-1',
          getPriorityTextColor(task.priority)
        ]"
      >
        {{ task.priority }}
      </div>
      <div v-if="task.project" class="px-2 py-1 text-xs bg-blue-50 text-blue-700 rounded-full">
        {{ getProjectName(task.project) }}
      </div>
      <!-- Sales Cycle Badge -->
      <div class="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full font-medium flex items-center gap-1">
        <LucideArrowRight class="size-3" />
        Sales Cycle
      </div>
    </div>
    
    <!-- Assignee -->
    <div v-if="task.created_by_sales" class="flex items-center gap-2 text-xs text-ink-gray-6 mb-3">
      <LucideUser class="size-3" />
      <span>{{ getUserName(task.created_by_sales) }}</span>
    </div>
    
    <!-- Action Button -->
    <div class="flex justify-end">
      <button
        @click="handleMoveToBucket"
        :disabled="moving"
        class="px-3 py-1.5 text-xs bg-orange-100 text-orange-700 rounded-md hover:bg-orange-200 transition-colors disabled:opacity-50 flex items-center gap-1"
      >
        <LucidePackage v-if="!moving" class="size-3" />
        <LucideLoader2 v-else class="size-3 animate-spin" />
        {{ moving ? 'Moving...' : 'Move to Procurement' }}
      </button>
    </div>
    
    <!-- Drag Handle -->
    <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
      <LucideGripVertical class="size-4 text-ink-gray-4" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { formatDistanceToNow } from 'date-fns'
import { PRIORITY_COLORS } from '@/data/artworkTasks'
import { useBucketTasks } from '@/data/artworkTasks'
import LucideCheckCircle from '~icons/lucide/check-circle'
import LucideArrowRight from '~icons/lucide/arrow-right'
import LucideUser from '~icons/lucide/user'
import LucideGripVertical from '~icons/lucide/grip-vertical'
import LucideBuilding2 from '~icons/lucide/building-2'
import LucidePackage from '~icons/lucide/package'
import LucideLoader2 from '~icons/lucide/loader-2'

interface Task {
  name: string
  title: string
  status: string
  project: string
  priority: string
  workflow_type: string
  created_by_sales?: string
  modified: string
  customer?: string
  customer_title?: string
  cycle_count?: number
}

interface Props {
  task: Task
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'task-moved': [task: Task]
  'drag-start': [task: Task]
  'drag-end': []
}>()

const isDragging = ref(false)
const moving = ref(false)

// Use the composable
const { moveCompletedSalesToBucket } = useBucketTasks()

const handleDragStart = (e: DragEvent) => {
  isDragging.value = true
  emit('drag-start', props.task)
  
  // Set drag data
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', JSON.stringify(props.task))
  }
}

const handleDragEnd = () => {
  isDragging.value = false
  emit('drag-end')
}

const handleMoveToBucket = async () => {
  moving.value = true
  try {
    await moveCompletedSalesToBucket(props.task.name)
    emit('task-moved', props.task)
  } catch (error) {
    console.error('Error moving task to bucket:', error)
    // You could add a toast notification here
  } finally {
    moving.value = false
  }
}

const formatDate = (dateString: string) => {
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true })
  } catch {
    return dateString
  }
}

const getPriorityTextColor = (priority: string) => {
  const colorMap = {
    'Low': 'text-ink-gray-7',
    'Medium': 'text-blue-700',
    'High': 'text-orange-700',
    'Urgent': 'text-red-700'
  }
  return colorMap[priority] || 'text-ink-gray-7'
}

const getProjectName = (project: string) => {
  return project.length > 20 ? project.substring(0, 20) + '...' : project
}

const getUserName = (userId: string) => {
  return userId.includes('@') ? userId.split('@')[0] : userId
}

const getCustomerBorderClass = (customerId: string) => {
  if (!customerId) return 'border-slate-200/50'
  
  const colors = [
    'border-blue-300/60',
    'border-green-300/60', 
    'border-purple-300/60',
    'border-orange-300/60',
    'border-pink-300/60',
    'border-indigo-300/60',
    'border-cyan-300/60',
    'border-amber-300/60'
  ]
  
  let hash = 0
  for (let i = 0; i < customerId.length; i++) {
    const char = customerId.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  
  const colorIndex = Math.abs(hash) % colors.length
  return colors[colorIndex]
}
</script>

<style scoped>
.group:hover .opacity-0 {
  opacity: 1;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.size-3, .size-4 {
  stroke: currentColor;
  fill: none;
  stroke-width: 1.5;
}

.text-ink-gray-4 svg,
.text-ink-gray-6 svg {
  stroke: currentColor;
}
</style>
