<template>
  <div
    class="bg-white/95 backdrop-blur-sm p-4 rounded-xl border transition-all duration-300 group"
    :class="[
      { 'opacity-50 scale-95': isDragging },
      { 'cursor-pointer hover:shadow-lg hover:shadow-blue-500/10 hover:-translate-y-0.5 hover:bg-white': isClickable },
      { 'cursor-default opacity-75': !isClickable },
      getCustomerBorderClass(task.customer)
    ]"
    draggable="true"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
    @click="handleClick"
  >
    <!-- Task Title -->
    <div class="flex items-center justify-between mb-2">
      <h4 class="font-medium text-ink-gray-9 line-clamp-2 flex-1">{{ task.title }}</h4>
      <!-- Non-clickable indicator for completed sales tasks -->
      <div v-if="!isClickable" class="ml-2 flex-shrink-0">
        <div class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full border border-gray-200">
          <LucideLock class="size-3 inline mr-1" />
          Moved to Procurement
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

    <!-- Cycle Count Badge (for tasks that have cycled) -->
    <div v-if="task.cycle_count && task.cycle_count > 0" class="mb-3">
      <div class="inline-flex items-center gap-1 px-2 py-1 text-xs bg-orange-100 text-orange-700 rounded-full border border-orange-200">
        <LucideRotateCcw class="size-3" />
        <span class="font-medium">Cycle #{{ task.cycle_count }}</span>
      </div>
    </div>
    
    <!-- Priority and Workflow Source Badges -->
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
      <!-- Workflow Type Badge -->
      <div 
        :class="{
          'bg-green-100 text-green-700 border border-green-200': task.workflow_type === 'Sales Cycle',
          'bg-purple-100 text-purple-700 border border-purple-200': task.workflow_type === 'Procurement Cycle'
        }"
        class="px-2 py-1 text-xs rounded-full font-medium flex items-center gap-1"
      >
        <component 
          :is="task.workflow_type === 'Sales Cycle' ? LucideArrowRight : LucidePackage" 
          class="size-3" 
        />
        {{ task.workflow_type === 'Sales Cycle' ? 'Sales' : 'Procurement' }}
      </div>
      <!-- Workflow Source Indicator -->
      <div v-if="getWorkflowSourceBadge()" 
           :class="getWorkflowSourceBadge().class"
           class="px-2 py-1 text-xs rounded-full font-medium flex items-center gap-1"
      >
        <component :is="getWorkflowSourceBadge().icon" class="size-3" />
        {{ getWorkflowSourceBadge().text }}
      </div>
    </div>
    
    <!-- Assignee -->
    <div v-if="task.assigned_to || task.created_by_sales" class="flex items-center gap-2 text-xs text-ink-gray-6">
      <LucideUser class="size-3" />
      <span>{{ getUserName(task.assigned_to || task.created_by_sales) }}</span>
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
import LucideArrowRight from '~icons/lucide/arrow-right'
import LucideRotateCcw from '~icons/lucide/rotate-ccw'
import LucidePackage from '~icons/lucide/package'
import LucideUser from '~icons/lucide/user'
import LucideGripVertical from '~icons/lucide/grip-vertical'
import LucideBuilding2 from '~icons/lucide/building-2'
import LucideLock from '~icons/lucide/lock'

interface Task {
  name: string
  title: string
  status: string
  project: string
  priority: string
  workflow_type: string
  assigned_to?: string
  created_by_sales?: string
  modified: string
  customer?: string
  customer_title?: string
  cycle_count?: number
  status_history?: Array<{
    from_status: string
    to_status: string
    changed_by: string
    change_date: string
  }>
}

interface Props {
  task: Task
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: []
  'drag-start': [task: Task]
  'drag-end': []
}>()

const isDragging = ref(false)

// Check if task is clickable (not completed sales cycle tasks)
const isClickable = computed(() => {
  // Don't allow clicking on completed sales cycle tasks (they're in procurement bucket)
  if (props.task.status === 'Completed' && props.task.workflow_type === 'Sales Cycle') {
    return false
  }
  return true
})

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

const handleClick = () => {
  // Only emit click if task is clickable
  if (isClickable.value) {
    emit('click')
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
  // This could be enhanced to fetch project names from a store
  // For now, just return the project ID or a shortened version
  return project.length > 20 ? project.substring(0, 20) + '...' : project
}

const getUserName = (userId: string) => {
  // This could be enhanced to fetch user full names from a store
  // For now, just return the user ID or email
  return userId.includes('@') ? userId.split('@')[0] : userId
}

const getCustomerBorderClass = (customerId: string) => {
  if (!customerId) return 'border-slate-200/50'
  
  // Generate a consistent color based on customer ID
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
  
  // Simple hash function to get consistent color for same customer
  let hash = 0
  for (let i = 0; i < customerId.length; i++) {
    const char = customerId.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32-bit integer
  }
  
  const colorIndex = Math.abs(hash) % colors.length
  return colors[colorIndex]
}

const getWorkflowSourceBadge = () => {
  const { task } = props
  
  // Show badges for review statuses in both workflows
  const reviewStatuses = ['Design', 'Approval', 'Quality Review', 'Procurement Review', 'Procurement Draft']
  if (!reviewStatuses.includes(task.status)) {
    return null
  }
  
  if (!task.status_history || task.status_history.length === 0) {
    return null
  }
  
  // Check if task has been reworked
  const hasReworkHistory = task.status_history.some(history => 
    history.from_status === 'Rework' || history.to_status === 'Rework'
  )
  
  // For Sales Cycle tasks in review
  if (task.workflow_type === 'Sales Cycle' && ['Design', 'Approval'].includes(task.status)) {
    if (hasReworkHistory) {
      return {
        text: 'Rework',
        class: 'bg-orange-100 text-orange-700 border border-orange-200',
        icon: LucideRotateCcw
      }
    } else {
      return {
        text: 'New',
        class: 'bg-green-100 text-green-700 border border-green-200',
        icon: LucideArrowRight
      }
    }
  }
  
  // For Procurement Cycle tasks in Procurement Review
  if (task.workflow_type === 'Procurement Cycle' && task.status === 'Procurement Review') {
    if (hasReworkHistory) {
      return {
        text: 'Rework',
        class: 'bg-orange-100 text-orange-700 border border-orange-200',
        icon: LucideRotateCcw
      }
    } else {
      return {
        text: 'From Procurement',
        class: 'bg-blue-100 text-blue-700 border border-blue-200',
        icon: LucidePackage
      }
    }
  }
  
  return null
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

/* Icon styling for better visibility */
.size-3, .size-4 {
  stroke: currentColor;
  fill: none;
  stroke-width: 1.5;
}

/* Ensure icons are visible in both light and dark modes */
.text-ink-gray-4 svg,
.text-ink-gray-6 svg {
  stroke: currentColor;
}
</style>
