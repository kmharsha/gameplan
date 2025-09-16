<template>
  <div class="flex flex-col h-full bg-mesh-2 bg-pattern-grid">
    <!-- Header -->
    <div class="flex flex-col">
      <div class="flex items-center justify-between px-6 py-4 border-b border-outline-gray-2 bg-white/70 backdrop-blur-sm shadow-lg">
        <div class="flex items-center gap-3">
          <LucidePackage class="size-5" />
          <h1 class="text-xl font-semibold text-ink-gray-9">Procurement Workflow</h1>
        </div>
        <div class="flex items-center gap-3">
          <Button 
            @click="refreshData" 
            :loading="loading"
            class="bg-surface-white border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1 inline-flex items-center"
          >
            <template #prefix>
              <LucideRefreshCw class="size-4 stroke-current" />
            </template>
            Refresh
          </Button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 overflow-hidden p-6">
      <div class="max-w-7xl mx-auto">
        <!-- Workflow Stepper -->
        <ProcurementWorkflowStepper 
          @task-clicked="handleTaskClick"
          @task-moved="handleTaskMove"
        />
        
        <!-- Additional Stats or Info -->
        <div class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Stats Cards -->
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="p-2 bg-blue-100 rounded-lg">
                <LucideFileText class="size-6 text-blue-600" />
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Total Tasks</p>
                <p class="text-2xl font-semibold text-gray-900">{{ totalTasks }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="p-2 bg-green-100 rounded-lg">
                <LucideCheckCircle class="size-6 text-green-600" />
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Approved Tasks</p>
                <p class="text-2xl font-semibold text-gray-900">{{ approvedTasksCount }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="p-2 bg-orange-100 rounded-lg">
                <LucideClock class="size-6 text-orange-600" />
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">In Progress</p>
                <p class="text-2xl font-semibold text-gray-900">{{ inProgressTasksCount }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Detail Modal -->
    <Dialog v-model="showTaskModal">
      <template #body>
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Task Details</h3>
            <Button 
              @click="showTaskModal = false"
              class="bg-gray-100 text-gray-700 hover:bg-gray-200"
            >
              <LucideX class="size-4" />
            </Button>
          </div>
          
          <div v-if="selectedTask" class="space-y-4">
            <div>
              <label class="text-sm font-medium text-gray-700">Title</label>
              <p class="mt-1 text-gray-900">{{ selectedTask.title }}</p>
            </div>
            
            <div>
              <label class="text-sm font-medium text-gray-700">Customer</label>
              <p class="mt-1 text-gray-900">{{ selectedTask.customer_title }}</p>
            </div>
            
            <div>
              <label class="text-sm font-medium text-gray-700">Priority</label>
              <span 
                :class="[
                  'inline-flex px-2 py-1 text-xs font-medium rounded-full',
                  getPriorityClasses(selectedTask.priority)
                ]"
              >
                {{ selectedTask.priority }}
              </span>
            </div>
            
            <div>
              <label class="text-sm font-medium text-gray-700">Status</label>
              <p class="mt-1 text-gray-900">{{ selectedTask.status }}</p>
            </div>
            
            <div>
              <label class="text-sm font-medium text-gray-700">Last Modified</label>
              <p class="mt-1 text-gray-900">{{ formatDate(selectedTask.modified) }}</p>
            </div>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Dialog } from 'frappe-ui'
import { useArtworkKanban } from '@/data/artworkTasks'
import { formatDistanceToNow } from 'date-fns'
import ProcurementWorkflowStepper from '@/components/ProcurementWorkflowStepper.vue'
import LucidePackage from '~icons/lucide/package'
import LucideRefreshCw from '~icons/lucide/refresh-cw'
import LucideFileText from '~icons/lucide/file-text'
import LucideCheckCircle from '~icons/lucide/check-circle'
import LucideClock from '~icons/lucide/clock'
import LucideX from '~icons/lucide/x'

const router = useRouter()
const { kanbanData, loading, fetchKanbanData } = useArtworkKanban()

// State
const showTaskModal = ref(false)
const selectedTask = ref(null)

// Computed properties
const totalTasks = computed(() => {
  const data = kanbanData.value || {}
  let count = 0
  
  // Count all procurement cycle tasks
  Object.values(data).forEach(tasks => {
    if (Array.isArray(tasks)) {
      count += tasks.filter(task => task.workflow_type === 'Procurement Cycle').length
    }
  })
  
  return count
})

const approvedTasksCount = computed(() => {
  const data = kanbanData.value || {}
  return data['Final Approved']?.length || 0
})

const inProgressTasksCount = computed(() => {
  const data = kanbanData.value || {}
  const inProgressStages = ['Procurement Draft', 'Procurement Review', 'Procurement Rework']
  let count = 0
  
  inProgressStages.forEach(stage => {
    if (data[stage]) {
      count += data[stage].filter(task => task.workflow_type === 'Procurement Cycle').length
    }
  })
  
  return count
})

// Methods
const handleTaskClick = (task) => {
  selectedTask.value = task
  showTaskModal.value = true
}

const handleTaskMove = (payload) => {
  console.log('Task moved:', payload)
  // Handle task movement logic here
  // This could trigger API calls to update task status
}

const refreshData = () => {
  fetchKanbanData()
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

// Load data on mount
onMounted(() => {
  fetchKanbanData()
})
</script>

<style scoped>
/* Custom background pattern */
.bg-mesh-2 {
  background-image: 
    radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0);
  background-size: 20px 20px;
}

.bg-pattern-grid {
  background-image: 
    linear-gradient(rgba(0,0,0,0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px);
  background-size: 20px 20px;
}
</style>
