<template>
  <div class="flex flex-col h-full max-h-[calc(100vh-200px)] w-80 bg-white rounded-lg shadow">
    <!-- Column Header -->
    <div class="p-3 font-semibold border-b">
      <div class="flex items-center gap-3">
        <div class="w-3 h-3 rounded-full bg-green-500"></div>
        <h3 class="font-medium text-ink-gray-9">Final Approved</h3>
        <span class="px-2 py-1 text-xs bg-surface-white rounded-full text-ink-gray-6">
          {{ tasks.length }}
        </span>
      </div>
    </div>

    <!-- Scrollable Task Area -->
    <div class="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-200 hover:scrollbar-thumb-gray-500 pr-1">
      <div class="p-3 space-y-3">
        <!-- Tasks in this column -->
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
          class="h-12 border-2 border-dashed border-green-400 bg-green-50 rounded-lg flex items-center justify-center"
        >
          <p class="text-sm text-green-700">Drop here to approve</p>
        </div>
      </div>
    </div>

    <!-- Bucket Section -->
    <div class="p-3 border-t border-outline-gray-1">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <LucidePackage class="size-4 text-orange-600" />
          <span class="text-sm font-medium text-ink-gray-7">Procurement Bucket</span>
        </div>
        <span class="px-2 py-1 text-xs font-medium rounded-full bg-orange-100 text-orange-800">
          {{ bucketTasksCount }}
        </span>
      </div>
      
      <!-- Bucket Animation Area -->
      <div class="relative h-16 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg border border-orange-200 flex items-center justify-center cursor-pointer hover:from-orange-100 hover:to-orange-200 transition-all duration-300"
           :class="{ 'animate-pulse': bucketBounce }"
           @click="showBucketModal = true">
        
        <!-- Bucket Icon -->
        <div class="relative">
          <LucidePackage 
            class="size-8 text-orange-600 transition-transform duration-300"
            :class="{ 'scale-110': bucketBounce }"
          />
          
          <!-- Document Drop Animation -->
          <Transition
            enter-active-class="transform ease-out duration-500 transition"
            enter-from-class="opacity-0 scale-50 translate-y-8"
            enter-to-class="opacity-100 scale-100 translate-y-0"
            leave-active-class="transition ease-in duration-200"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-50"
          >
            <div 
              v-if="showDropAnimation"
              class="absolute -top-2 -right-2 w-4 h-6 bg-white border border-orange-300 rounded-sm shadow-lg"
            >
              <div class="p-1 h-full flex flex-col justify-between">
                <div class="w-full h-0.5 bg-orange-400 rounded"></div>
                <div class="w-full h-0.5 bg-orange-400 rounded"></div>
                <div class="w-full h-0.5 bg-orange-400 rounded"></div>
              </div>
            </div>
          </Transition>
        </div>
        
        <!-- Stacked Documents -->
        <div class="absolute -bottom-1 -right-1 w-12 h-8">
          <div 
            v-for="(task, index) in visibleBucketTasks"
            :key="task.name"
            :class="[
              'absolute w-8 h-6 bg-white border border-orange-200 rounded-sm shadow-sm transform transition-all duration-500',
              getDocumentStackClasses(index)
            ]"
            :style="{ 
              zIndex: 10 - index,
              transform: `translateX(${index * 1}px) translateY(${index * 1}px) rotate(${index * 1}deg)`
            }"
          >
            <div class="p-1 h-full flex flex-col justify-between">
              <div class="w-full h-0.5 bg-orange-300 rounded"></div>
              <div class="w-full h-0.5 bg-orange-300 rounded"></div>
              <div class="w-full h-0.5 bg-orange-300 rounded"></div>
            </div>
          </div>
          
          <!-- Overflow Indicator -->
          <div 
            v-if="bucketTasksCount > 3"
            class="absolute w-8 h-6 bg-orange-200 border border-orange-300 rounded-sm shadow-sm flex items-center justify-center text-xs font-medium text-orange-600"
            :style="{ 
              zIndex: 7,
              transform: `translateX(3px) translateY(3px) rotate(3deg)`
            }"
          >
            +{{ bucketTasksCount - 3 }}
          </div>
        </div>
      </div>
      
      <!-- View Bucket Button -->
      <button 
        @click="viewBucket"
        class="w-full mt-2 px-3 py-2 text-xs font-medium text-orange-700 bg-orange-50 border border-orange-200 rounded-md hover:bg-orange-100 transition-colors"
      >
        View All Tasks
      </button>
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
          
          <div v-if="bucketTasksCount === 0" class="text-center py-8">
            <LucidePackage class="size-12 mx-auto mb-4 text-gray-400" />
            <p class="text-gray-500">No approved tasks in bucket yet</p>
          </div>
          
          <div v-else class="space-y-3 max-h-96 overflow-y-auto">
            <div 
              v-for="task in bucketTasks"
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
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Dialog } from 'frappe-ui'
import { useBucketTasks } from '@/data/artworkTasks'
import { formatDistanceToNow } from 'date-fns'
import KanbanTaskCard from './KanbanTaskCard.vue'
import LucidePackage from '~icons/lucide/package'
import LucideInbox from '~icons/lucide/inbox'
import LucideX from '~icons/lucide/x'
import LucideCheckCircle from '~icons/lucide/check-circle'

interface Task {
  name: string
  title: string
  status: string
  project: string
  priority: string
  assigned_to?: string
  created_by_sales: string
  modified: string
  customer_title?: string
}

interface Props {
  tasks: Task[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'task-moved': [payload: { task: Task, newStatus: string }]
  'task-clicked': [task: Task]
}>()

const router = useRouter()
const { bucketTasks, fetchBucketTasks } = useBucketTasks()

// State
const isDragOver = ref(false)
const draggedTask = ref<Task | null>(null)
const showBucketModal = ref(false)
const showToast = ref(false)
const toastMessage = ref('')
const bucketBounce = ref(false)
const showDropAnimation = ref(false)
const previousBucketCount = ref(0)

// Computed properties
const bucketTasksCount = computed(() => bucketTasks.value.length)
const visibleBucketTasks = computed(() => bucketTasks.value.slice(0, 3))

// Methods
const getDocumentStackClasses = (index) => {
  const colors = ['bg-white', 'bg-orange-50', 'bg-orange-100']
  return colors[index % colors.length]
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

const handleTaskDragStart = (task: Task) => {
  draggedTask.value = task
}

const handleTaskDragEnd = () => {
  isDragOver.value = false
  draggedTask.value = null
}

const handleTaskClick = (task) => {
  emit('task-clicked', task)
  showBucketModal.value = false
}

const viewBucket = () => {
  showToast.value = false
  router.push({ name: 'ArtworkBucket' })
}

// Method to trigger animation when task is moved to bucket
const triggerBucketAnimation = () => {
  bucketBounce.value = true
  showDropAnimation.value = true
  showToast.value = true
  toastMessage.value = '✅ Task moved to Procurement Bucket'
  
  // Reset animations
  setTimeout(() => {
    bucketBounce.value = false
    showDropAnimation.value = false
  }, 1000)
  
  // Hide toast after 5 seconds
  setTimeout(() => {
    showToast.value = false
  }, 5000)
}

// Expose method to parent component
defineExpose({
  triggerBucketAnimation
})

// Watch for changes in bucket tasks count to trigger animations
watch(bucketTasksCount, (newCount, oldCount) => {
  if (newCount > oldCount && oldCount >= 0) {
    // Task was moved to bucket - trigger animations
    bucketBounce.value = true
    showDropAnimation.value = true
    showToast.value = true
    toastMessage.value = '✅ Task moved to Procurement Bucket'
    
    // Reset animations
    setTimeout(() => {
      bucketBounce.value = false
      showDropAnimation.value = false
    }, 1000)
    
    // Hide toast after 5 seconds
    setTimeout(() => {
      showToast.value = false
    }, 5000)
  }
  
  previousBucketCount.value = newCount
}, { immediate: true })

// Watch for changes in tasks prop to trigger animations when tasks are moved
watch(() => props.tasks, (newTasks, oldTasks) => {
  if (oldTasks && newTasks.length < oldTasks.length) {
    // A task was removed from this column (moved to bucket)
    bucketBounce.value = true
    showDropAnimation.value = true
    showToast.value = true
    toastMessage.value = '✅ Task moved to Procurement Bucket'
    
    // Reset animations
    setTimeout(() => {
      bucketBounce.value = false
      showDropAnimation.value = false
    }, 1000)
    
    // Hide toast after 5 seconds
    setTimeout(() => {
      showToast.value = false
    }, 5000)
  }
}, { deep: true })

// Load bucket tasks on mount
watch(() => bucketTasks.value, () => {
  if (bucketTasks.value.length > 0) {
    previousBucketCount.value = bucketTasks.value.length
  }
}, { immediate: true })
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

/* Custom scrollbar */
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
