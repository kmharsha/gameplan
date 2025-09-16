<template>
  <div class="w-full bg-white rounded-xl shadow-lg border border-gray-200 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-orange-100 rounded-lg">
          <LucidePackage class="size-6 text-orange-600" />
        </div>
        <div>
          <h2 class="text-xl font-semibold text-gray-900">Procurement Workflow</h2>
          <p class="text-sm text-gray-600">Track tasks through procurement stages</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Button 
          @click="refreshTasks" 
          :loading="loading"
          class="bg-white border border-gray-300 text-gray-700 hover:bg-gray-50"
        >
          <template #prefix>
            <LucideRefreshCw class="size-4" />
          </template>
          Refresh
        </Button>
      </div>
    </div>

    <!-- Workflow Stepper -->
    <div class="relative">
      <!-- Progress Line -->
      <div class="absolute top-8 left-0 right-0 h-0.5 bg-gray-200 z-0">
        <div 
          class="h-full bg-gradient-to-r from-orange-400 to-green-400 transition-all duration-500 ease-out"
          :style="{ width: progressPercentage + '%' }"
        ></div>
      </div>

      <!-- Stages -->
      <div class="relative flex justify-between items-start z-10">
        <div 
          v-for="(stage, index) in stages" 
          :key="stage.key"
          class="flex flex-col items-center flex-1"
        >
          <!-- Stage Circle -->
          <div 
            :class="[
              'w-16 h-16 rounded-full flex items-center justify-center text-white font-semibold text-sm transition-all duration-300 transform',
              getStageClasses(stage, index)
            ]"
            :style="{ 
              transform: stage.key === 'final_approved' && bucketBounce ? 'scale(1.1)' : 'scale(1)',
              transition: 'transform 0.3s ease-out'
            }"
          >
            <component :is="stage.icon" class="size-6" />
          </div>

          <!-- Stage Label -->
          <div class="mt-3 text-center">
            <h3 class="text-sm font-medium text-gray-900">{{ stage.label }}</h3>
            <p class="text-xs text-gray-500 mt-1">{{ stage.description }}</p>
          </div>

          <!-- Task Count -->
          <div class="mt-2">
            <span 
              :class="[
                'px-2 py-1 text-xs font-medium rounded-full',
                getStageCountClasses(stage, index)
              ]"
            >
              {{ getTaskCount(stage.key) }}
            </span>
          </div>

          <!-- Tasks in this stage -->
          <div class="mt-4 w-full max-w-xs">
            <div class="space-y-2">
              <div
                v-for="task in getTasksInStage(stage.key)"
                :key="task.name"
                :class="[
                  'p-3 rounded-lg border transition-all duration-300 cursor-pointer hover:shadow-md',
                  getTaskCardClasses(task, stage.key)
                ]"
                @click="handleTaskClick(task)"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1 min-w-0">
                    <h4 class="text-sm font-medium text-gray-900 truncate">{{ task.title }}</h4>
                    <p class="text-xs text-gray-500 mt-1">{{ task.customer_title }}</p>
                    <div class="flex items-center gap-2 mt-2">
                      <span 
                        :class="[
                          'px-2 py-1 text-xs rounded-full',
                          getPriorityClasses(task.priority)
                        ]"
                      >
                        {{ task.priority }}
                      </span>
                      <span class="text-xs text-gray-400">{{ formatDate(task.modified) }}</span>
                    </div>
                  </div>
                  <div class="ml-2 flex-shrink-0">
                    <LucideChevronRight class="size-4 text-gray-400" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Bucket for Final Approved Tasks -->
        <div class="flex flex-col items-center ml-8">
          <!-- Bucket Icon -->
          <div 
            :class="[
              'w-16 h-16 rounded-full flex items-center justify-center text-white font-semibold text-sm transition-all duration-300 transform',
              bucketClasses
            ]"
            :style="{ 
              transform: bucketBounce ? 'scale(1.1)' : 'scale(1)',
              transition: 'transform 0.3s ease-out'
            }"
            @click="showBucketModal = true"
          >
            <LucidePackage class="size-6" />
          </div>

          <!-- Bucket Label -->
          <div class="mt-3 text-center">
            <h3 class="text-sm font-medium text-gray-900">Procurement Bucket</h3>
            <p class="text-xs text-gray-500 mt-1">Approved tasks</p>
          </div>

          <!-- Bucket Count -->
          <div class="mt-2">
            <span class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
              {{ approvedTasks.length }}
            </span>
          </div>

          <!-- Stacked Documents Animation -->
          <div class="mt-4 relative">
            <div 
              v-for="(task, index) in approvedTasks.slice(0, 3)"
              :key="task.name"
              :class="[
                'absolute w-12 h-16 bg-white border-2 border-gray-200 rounded-lg shadow-sm transform transition-all duration-500',
                getDocumentStackClasses(index)
              ]"
              :style="{ 
                zIndex: 10 - index,
                transform: `translateX(${index * 2}px) translateY(${index * 2}px) rotate(${index * 2}deg)`
              }"
            >
              <div class="p-2 h-full flex flex-col justify-between">
                <div class="w-full h-1 bg-gray-300 rounded"></div>
                <div class="w-full h-1 bg-gray-300 rounded"></div>
                <div class="w-full h-1 bg-gray-300 rounded"></div>
              </div>
            </div>
            <div 
              v-if="approvedTasks.length > 3"
              class="absolute w-12 h-16 bg-gray-100 border-2 border-gray-200 rounded-lg shadow-sm flex items-center justify-center text-xs font-medium text-gray-500"
              :style="{ 
                zIndex: 7,
                transform: `translateX(6px) translateY(6px) rotate(6deg)`
              }"
            >
              +{{ approvedTasks.length - 3 }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bucket Modal -->
    <Dialog v-model="showBucketModal">
      <template #body>
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Procurement Bucket</h3>
            <Button 
              @click="showBucketModal = false"
              class="bg-gray-100 text-gray-700 hover:bg-gray-200"
            >
              <LucideX class="size-4" />
            </Button>
          </div>
          
          <div v-if="approvedTasks.length === 0" class="text-center py-8">
            <LucidePackage class="size-12 mx-auto mb-4 text-gray-400" />
            <p class="text-gray-500">No approved tasks in bucket yet</p>
          </div>
          
          <div v-else class="space-y-3 max-h-96 overflow-y-auto">
            <div 
              v-for="task in approvedTasks"
              :key="task.name"
              class="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h4 class="font-medium text-gray-900">{{ task.title }}</h4>
                  <p class="text-sm text-gray-600 mt-1">{{ task.customer_title }}</p>
                  <div class="flex items-center gap-2 mt-2">
                    <span 
                      :class="[
                        'px-2 py-1 text-xs rounded-full',
                        getPriorityClasses(task.priority)
                      ]"
                    >
                      {{ task.priority }}
                    </span>
                    <span class="text-xs text-gray-400">{{ formatDate(task.modified) }}</span>
                  </div>
                </div>
                <Button 
                  @click="handleTaskClick(task)"
                  class="bg-orange-600 text-white hover:bg-orange-700"
                >
                  View Details
                </Button>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Toast Notification -->
    <Transition
      enter-active-class="transform ease-out duration-300 transition"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition ease-in duration-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showToast"
        class="fixed top-4 right-4 z-50 max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden"
      >
        <div class="p-4">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <LucideCheckCircle class="size-5 text-green-400" />
            </div>
            <div class="ml-3 w-0 flex-1">
              <p class="text-sm font-medium text-gray-900">{{ toastMessage }}</p>
              <div class="mt-2">
                <Button 
                  @click="viewBucket"
                  class="text-sm bg-green-600 text-white hover:bg-green-700"
                >
                  View Bucket
                </Button>
              </div>
            </div>
            <div class="ml-4 flex-shrink-0 flex">
              <button 
                @click="showToast = false"
                class="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none"
              >
                <LucideX class="size-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Button, Dialog } from 'frappe-ui'
import { useArtworkKanban } from '@/data/artworkTasks'
import { formatDistanceToNow } from 'date-fns'
import LucidePackage from '~icons/lucide/package'
import LucideRefreshCw from '~icons/lucide/refresh-cw'
import LucideChevronRight from '~icons/lucide/chevron-right'
import LucideX from '~icons/lucide/x'
import LucideCheckCircle from '~icons/lucide/check-circle'
import LucideFileText from '~icons/lucide/file-text'
import LucideEye from '~icons/lucide/eye'
import LucideRotateCcw from '~icons/lucide/rotate-ccw'
import LucideCheck from '~icons/lucide/check'

const { kanbanData, loading, fetchKanbanData, moveTask } = useArtworkKanban()

// Workflow stages
const stages = [
  {
    key: 'procurement_draft',
    label: 'Draft',
    description: 'Initial creation',
    icon: LucideFileText,
    color: 'bg-gray-500'
  },
  {
    key: 'procurement_review',
    label: 'Review',
    description: 'Under review',
    icon: LucideEye,
    color: 'bg-blue-500'
  },
  {
    key: 'procurement_rework',
    label: 'Rework',
    description: 'Needs changes',
    icon: LucideRotateCcw,
    color: 'bg-orange-500'
  },
  {
    key: 'final_approved',
    label: 'Approved',
    description: 'Ready for bucket',
    icon: LucideCheck,
    color: 'bg-green-500'
  }
]

// State
const showBucketModal = ref(false)
const showToast = ref(false)
const toastMessage = ref('')
const bucketBounce = ref(false)
const previousApprovedCount = ref(0)

// Computed properties
const procurementTasks = computed(() => {
  const data = kanbanData.value || {}
  const tasks = []
  
  // Get tasks from all procurement stages
  stages.forEach(stage => {
    const stageTasks = data[stage.label] || []
    stageTasks.forEach(task => {
      if (task.workflow_type === 'Procurement Cycle') {
        tasks.push({ ...task, stage: stage.key })
      }
    })
  })
  
  return tasks
})

const approvedTasks = computed(() => {
  const data = kanbanData.value || {}
  return data['Final Approved'] || []
})

const progressPercentage = computed(() => {
  const totalTasks = procurementTasks.value.length
  if (totalTasks === 0) return 0
  
  const completedTasks = approvedTasks.value.length
  return (completedTasks / (totalTasks + completedTasks)) * 100
})

// Methods
const getStageClasses = (stage, index) => {
  const hasTasks = getTaskCount(stage.key) > 0
  const isActive = hasTasks || index === 0
  
  if (stage.key === 'final_approved') {
    return hasTasks ? 'bg-green-500 shadow-lg shadow-green-200' : 'bg-gray-300'
  }
  
  return isActive ? stage.color + ' shadow-lg' : 'bg-gray-300'
}

const getStageCountClasses = (stage, index) => {
  const hasTasks = getTaskCount(stage.key) > 0
  
  if (stage.key === 'final_approved') {
    return hasTasks ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
  }
  
  return hasTasks ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600'
}

const getTaskCount = (stageKey) => {
  if (stageKey === 'final_approved') {
    return approvedTasks.value.length
  }
  
  return procurementTasks.value.filter(task => task.stage === stageKey).length
}

const getTasksInStage = (stageKey) => {
  if (stageKey === 'final_approved') {
    return approvedTasks.value
  }
  
  return procurementTasks.value.filter(task => task.stage === stageKey)
}

const getTaskCardClasses = (task, stageKey) => {
  const baseClasses = 'bg-white border-gray-200 hover:border-gray-300'
  
  if (stageKey === 'final_approved') {
    return baseClasses + ' border-green-200 bg-green-50'
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

const getDocumentStackClasses = (index) => {
  const colors = ['bg-white', 'bg-gray-50', 'bg-gray-100']
  return colors[index % colors.length]
}

const bucketClasses = computed(() => {
  const hasTasks = approvedTasks.value.length > 0
  return hasTasks 
    ? 'bg-green-500 shadow-lg shadow-green-200 cursor-pointer hover:bg-green-600' 
    : 'bg-gray-300 cursor-pointer hover:bg-gray-400'
})

const formatDate = (dateString) => {
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true })
  } catch {
    return dateString
  }
}

const handleTaskClick = (task) => {
  // Emit event to parent or navigate to task details
  console.log('Task clicked:', task)
}

const refreshTasks = () => {
  fetchKanbanData()
}

const viewBucket = () => {
  showToast.value = false
  showBucketModal.value = true
}

// Watch for changes in approved tasks count to trigger animations
watch(approvedTasks, (newTasks, oldTasks) => {
  const newCount = newTasks.length
  const oldCount = previousApprovedCount.value
  
  if (newCount > oldCount) {
    // Task was moved to approved - trigger animations
    bucketBounce.value = true
    showToast.value = true
    toastMessage.value = '✅ Task moved to Procurement Bucket'
    
    // Reset bounce animation
    setTimeout(() => {
      bucketBounce.value = false
    }, 600)
    
    // Hide toast after 5 seconds
    setTimeout(() => {
      showToast.value = false
    }, 5000)
  }
  
  previousApprovedCount.value = newCount
}, { deep: true })

// Load data on mount
onMounted(() => {
  fetchKanbanData()
  previousApprovedCount.value = approvedTasks.value.length
})
</script>

<style scoped>
/* Custom animations */
@keyframes bounce {
  0%, 20%, 53%, 80%, 100% {
    transform: translate3d(0,0,0);
  }
  40%, 43% {
    transform: translate3d(0, -8px, 0);
  }
  70% {
    transform: translate3d(0, -4px, 0);
  }
  90% {
    transform: translate3d(0, -2px, 0);
  }
}

.bounce {
  animation: bounce 0.6s ease-in-out;
}

/* Smooth transitions */
.transition-all {
  transition: all 0.3s ease-out;
}

/* Custom scrollbar for modal */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
