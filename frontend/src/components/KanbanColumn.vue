<template>
  <div class="flex flex-col h-full max-h-[calc(100vh-200px)] w-80 bg-white rounded-lg shadow">
    <!-- Column Header -->
    <div class="p-3 font-semibold border-b">
      <div class="flex items-center gap-3">
        <div 
          :class="[
            'w-3 h-3 rounded-full',
            color || 'bg-ink-gray-3'
          ]"
        ></div>
        <h3 class="font-medium text-ink-gray-9">{{ title }}</h3>
        <span class="px-2 py-1 text-xs bg-surface-white rounded-full text-ink-gray-6">
          {{ tasks.length }}
        </span>
      </div>
    </div>

    <!-- Scrollable Task Area -->
    <div 
      class="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-200 hover:scrollbar-thumb-gray-500 pr-1"
      @drop="handleDrop"
      @dragover="handleDragOver"
      @dragenter="handleDragEnter"
      @dragleave="handleDragLeave"
      :class="{ 'bg-surface-gray-2': isDragOver }"
    >
      <div class="p-3 space-y-3">
        <KanbanTaskCard
          v-for="task in tasks"
          :key="task.name"
          :task="task"
          @click="$emit('task-clicked', task)"
          @drag-start="handleTaskDragStart"
          @drag-end="handleTaskDragEnd"
        />
        
        
        <!-- Empty State -->
        <div 
          v-if="tasks.length === 0" 
          class="flex items-center justify-center h-32 text-ink-gray-5 border-2 border-dashed border-outline-gray-2 rounded-lg"
        >
          <div class="text-center">
            <LucideInbox class="size-6 mx-auto mb-2" />
            <p class="text-sm">No tasks</p>
          </div>
        </div>

        <!-- Drop Zone Indicator -->
        <div 
          v-if="isDragOver && draggedTask"
          class="h-12 border-2 border-dashed border-blue-400 bg-blue-50 rounded-lg flex items-center justify-center"
        >
          <p class="text-sm text-blue-700">Drop here to move to {{ title }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import KanbanTaskCard from './KanbanTaskCard.vue'
import LucideInbox from '~icons/lucide/inbox'

interface Task {
  name: string
  title: string
  status: string
  project: string
  priority: string
  assigned_to?: string
  created_by_sales: string
  modified: string
}

interface Props {
  title: string
  tasks: Task[]
  color?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'task-moved': [payload: { task: Task, newStatus: string }]
  'task-clicked': [task: Task]
}>()

const isDragOver = ref(false)
const draggedTask = ref<Task | null>(null)

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = true
}

const handleDragEnter = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (e: DragEvent) => {
  // Only set to false if we're leaving the column entirely
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  const x = e.clientX
  const y = e.clientY
  
  if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
    isDragOver.value = false
  }
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = false
  
  if (draggedTask.value) {
    emit('task-moved', {
      task: draggedTask.value,
      newStatus: props.title
    })
    draggedTask.value = null
  }
}

const handleTaskDragStart = (task: Task) => {
  draggedTask.value = task
}

const handleTaskDragEnd = () => {
  isDragOver.value = false
  draggedTask.value = null
}
</script>

