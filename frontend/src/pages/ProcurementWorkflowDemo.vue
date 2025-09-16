<template>
  <div class="flex flex-col h-full bg-gradient-to-br from-blue-50 to-indigo-100">
    <!-- Header -->
    <div class="flex flex-col">
      <div class="flex items-center justify-between px-6 py-4 border-b border-outline-gray-2 bg-white/80 backdrop-blur-sm shadow-lg">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-orange-100 rounded-lg">
            <LucidePackage class="size-6 text-orange-600" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Procurement Workflow Demo</h1>
            <p class="text-sm text-gray-600">Interactive demonstration of the procurement workflow system</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <Button 
            @click="resetDemo" 
            class="bg-white border border-gray-300 text-gray-700 hover:bg-gray-50"
          >
            <template #prefix>
              <LucideRefreshCw class="size-4" />
            </template>
            Reset Demo
          </Button>
          <Button 
            @click="simulateTaskMove" 
            class="bg-orange-600 text-white hover:bg-orange-700"
          >
            <template #prefix>
              <LucidePlay class="size-4" />
            </template>
            Simulate Move
          </Button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 overflow-hidden p-6">
      <div class="max-w-7xl mx-auto">
        <!-- Demo Workflow Stepper -->
        <div class="w-full bg-white rounded-xl shadow-lg border border-gray-200 p-6 mb-8">
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
                        getTaskCardClasses(task, stage.key),
                        { 'animate-drop-to-bucket': task.isDropping }
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
        </div>

        <!-- Demo Controls -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Demo Controls</h3>
            <div class="space-y-3">
              <Button 
                @click="addSampleTask" 
                class="w-full bg-blue-600 text-white hover:bg-blue-700"
              >
                <template #prefix>
                  <LucidePlus class="size-4" />
                </template>
                Add Sample Task
              </Button>
              <Button 
                @click="moveRandomTask" 
                class="w-full bg-orange-600 text-white hover:bg-orange-700"
              >
                <template #prefix>
                  <LucideArrowRight class="size-4" />
                </template>
                Move Random Task Forward
              </Button>
              <Button 
                @click="simulateApproval" 
                class="w-full bg-green-600 text-white hover:bg-green-700"
              >
                <template #prefix>
                  <LucideCheck class="size-4" />
                </template>
                Simulate Task Approval
              </Button>
            </div>
          </div>

          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Statistics</h3>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">Total Tasks:</span>
                <span class="font-medium">{{ totalTasks }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">In Progress:</span>
                <span class="font-medium">{{ inProgressTasks }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">Approved:</span>
                <span class="font-medium text-green-600">{{ approvedTasks.length }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">Completion Rate:</span>
                <span class="font-medium">{{ completionRate }}%</span>
              </div>
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
import { ref, computed, onMounted } from 'vue'
import { Button, Dialog } from 'frappe-ui'
import { formatDistanceToNow } from 'date-fns'
import LucidePackage from '~icons/lucide/package'
import LucideRefreshCw from '~icons/lucide/refresh-cw'
import LucidePlay from '~icons/lucide/play'
import LucidePlus from '~icons/lucide/plus'
import LucideArrowRight from '~icons/lucide/arrow-right'
import LucideCheck from '~icons/lucide/check'
import LucideChevronRight from '~icons/lucide/chevron-right'
import LucideX from '~icons/lucide/x'
import LucideCheckCircle from '~icons/lucide/check-circle'
import LucideFileText from '~icons/lucide/file-text'
import LucideEye from '~icons/lucide/eye'
import LucideRotateCcw from '~icons/lucide/rotate-ccw'

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

// Sample data
const sampleTasks = [
  {
    name: 'TASK-001',
    title: 'Design Review for Product Launch',
    customer_title: 'Acme Corp',
    priority: 'High',
    modified: new Date().toISOString(),
    stage: 'procurement_draft',
    isDropping: false
  },
  {
    name: 'TASK-002',
    title: 'Marketing Material Approval',
    customer_title: 'TechStart Inc',
    priority: 'Medium',
    modified: new Date(Date.now() - 86400000).toISOString(),
    stage: 'procurement_review',
    isDropping: false
  },
  {
    name: 'TASK-003',
    title: 'Brand Guidelines Update',
    customer_title: 'Global Brands Ltd',
    priority: 'Low',
    modified: new Date(Date.now() - 172800000).toISOString(),
    stage: 'procurement_rework',
    isDropping: false
  },
  {
    name: 'TASK-004',
    title: 'Website Redesign Assets',
    customer_title: 'Digital Agency Co',
    priority: 'Urgent',
    modified: new Date(Date.now() - 259200000).toISOString(),
    stage: 'final_approved',
    isDropping: false
  }
]

// State
const tasks = ref([...sampleTasks])
const approvedTasks = ref([])
const showBucketModal = ref(false)
const showToast = ref(false)
const toastMessage = ref('')
const bucketBounce = ref(false)

// Computed properties
const totalTasks = computed(() => tasks.value.length + approvedTasks.value.length)

const inProgressTasks = computed(() => {
  return tasks.value.filter(task => task.stage !== 'final_approved').length
})

const completionRate = computed(() => {
  if (totalTasks.value === 0) return 0
  return Math.round((approvedTasks.value.length / totalTasks.value) * 100)
})

const progressPercentage = computed(() => {
  const total = totalTasks.value
  if (total === 0) return 0
  return (approvedTasks.value.length / total) * 100
})

const bucketClasses = computed(() => {
  const hasTasks = approvedTasks.value.length > 0
  return hasTasks 
    ? 'bg-green-500 shadow-lg shadow-green-200 cursor-pointer hover:bg-green-600' 
    : 'bg-gray-300 cursor-pointer hover:bg-gray-400'
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
  
  return tasks.value.filter(task => task.stage === stageKey).length
}

const getTasksInStage = (stageKey) => {
  if (stageKey === 'final_approved') {
    return approvedTasks.value
  }
  
  return tasks.value.filter(task => task.stage === stageKey)
}

const getTaskCardClasses = (task, stageKey) => {
  const baseClasses = 'bg-white border-gray-200 hover:border-gray-300'
  
  if (stageKey === 'final_approved') {
    return baseClasses + ' border-green-200 bg-green-50'
  }
  
  if (stageKey === 'procurement_rework') {
    return baseClasses + ' border-orange-200 bg-orange-50'
  }
  
  if (stageKey === 'procurement_review') {
    return baseClasses + ' border-blue-200 bg-blue-50'
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

const formatDate = (dateString) => {
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true })
  } catch {
    return dateString
  }
}

const handleTaskClick = (task) => {
  console.log('Task clicked:', task)
}

const resetDemo = () => {
  tasks.value = [...sampleTasks]
  approvedTasks.value = []
  showToast.value = false
  bucketBounce.value = false
}

const addSampleTask = () => {
  const newTask = {
    name: `TASK-${String(tasks.value.length + 1).padStart(3, '0')}`,
    title: `Sample Task ${tasks.value.length + 1}`,
    customer_title: 'Demo Customer',
    priority: ['Low', 'Medium', 'High', 'Urgent'][Math.floor(Math.random() * 4)],
    modified: new Date().toISOString(),
    stage: 'procurement_draft',
    isDropping: false
  }
  tasks.value.push(newTask)
}

const moveRandomTask = () => {
  const inProgressTasks = tasks.value.filter(task => task.stage !== 'final_approved')
  if (inProgressTasks.length === 0) return
  
  const randomTask = inProgressTasks[Math.floor(Math.random() * inProgressTasks.length)]
  const currentStageIndex = stages.findIndex(stage => stage.key === randomTask.stage)
  
  if (currentStageIndex < stages.length - 1) {
    randomTask.stage = stages[currentStageIndex + 1].key
  }
}

const simulateApproval = () => {
  const reviewTasks = tasks.value.filter(task => task.stage === 'procurement_review')
  if (reviewTasks.length === 0) return
  
  const randomTask = reviewTasks[Math.floor(Math.random() * reviewTasks.length)]
  
  // Animate task dropping
  randomTask.isDropping = true
  
  setTimeout(() => {
    // Move to approved
    randomTask.stage = 'final_approved'
    approvedTasks.value.push(randomTask)
    
    // Remove from tasks
    const index = tasks.value.findIndex(task => task.name === randomTask.name)
    if (index > -1) {
      tasks.value.splice(index, 1)
    }
    
    // Trigger animations
    bucketBounce.value = true
    showToast.value = true
    toastMessage.value = '✅ Task moved to Procurement Bucket'
    
    // Reset animations
    setTimeout(() => {
      bucketBounce.value = false
      randomTask.isDropping = false
    }, 600)
    
    // Hide toast
    setTimeout(() => {
      showToast.value = false
    }, 5000)
  }, 300)
}

const simulateTaskMove = () => {
  simulateApproval()
}

const viewBucket = () => {
  showToast.value = false
  showBucketModal.value = true
}

// Load demo data on mount
onMounted(() => {
  // Initialize with some approved tasks
  const approvedTask = {
    name: 'TASK-004',
    title: 'Website Redesign Assets',
    customer_title: 'Digital Agency Co',
    priority: 'Urgent',
    modified: new Date(Date.now() - 259200000).toISOString()
  }
  approvedTasks.value.push(approvedTask)
  
  // Remove from tasks
  const index = tasks.value.findIndex(task => task.name === approvedTask.name)
  if (index > -1) {
    tasks.value.splice(index, 1)
  }
})
</script>

<style scoped>
/* Custom animations */
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
