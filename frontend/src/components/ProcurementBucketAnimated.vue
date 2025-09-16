<template>
  <div class="relative">
    <!-- Bucket Container -->
    <div 
      :class="[
        'relative w-20 h-20 rounded-full flex items-center justify-center cursor-pointer transition-all duration-300 transform',
        bucketClasses
      ]"
      :style="{ 
        transform: bucketBounce ? 'scale(1.1)' : 'scale(1)',
        transition: 'transform 0.3s ease-out'
      }"
      @click="showBucketModal = true"
    >
      <!-- Bucket Icon -->
      <LucidePackage class="size-8 text-white" />
      
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
          class="absolute -top-2 -right-2 w-6 h-8 bg-white border-2 border-gray-300 rounded-sm shadow-lg"
        >
          <div class="p-1 h-full flex flex-col justify-between">
            <div class="w-full h-0.5 bg-gray-400 rounded"></div>
            <div class="w-full h-0.5 bg-gray-400 rounded"></div>
            <div class="w-full h-0.5 bg-gray-400 rounded"></div>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Stacked Documents -->
    <div class="absolute -bottom-2 -right-2 w-16 h-20">
      <div 
        v-for="(task, index) in visibleTasks"
        :key="task.name"
        :class="[
          'absolute w-12 h-16 bg-white border-2 border-gray-200 rounded-lg shadow-sm transform transition-all duration-500',
          getDocumentStackClasses(index)
        ]"
        :style="{ 
          zIndex: 10 - index,
          transform: `translateX(${index * 2}px) translateY(${index * 2}px) rotate(${index * 2}deg)`,
          animationDelay: `${index * 100}ms`
        }"
        @click.stop="handleDocumentClick(task)"
      >
        <div class="p-2 h-full flex flex-col justify-between">
          <div class="w-full h-1 bg-gray-300 rounded"></div>
          <div class="w-full h-1 bg-gray-300 rounded"></div>
          <div class="w-full h-1 bg-gray-300 rounded"></div>
          <div class="w-full h-1 bg-gray-300 rounded"></div>
        </div>
      </div>
      
      <!-- Overflow Indicator -->
      <div 
        v-if="tasks.length > 3"
        :class="[
          'absolute w-12 h-16 bg-gray-100 border-2 border-gray-200 rounded-lg shadow-sm flex items-center justify-center text-xs font-medium text-gray-500 cursor-pointer hover:bg-gray-200 transition-colors',
          getDocumentStackClasses(3)
        ]"
        :style="{ 
          zIndex: 7,
          transform: `translateX(6px) translateY(6px) rotate(6deg)`
        }"
        @click.stop="showBucketModal = true"
      >
        +{{ tasks.length - 3 }}
      </div>
    </div>

    <!-- Bucket Modal -->
    <Dialog v-model="showBucketModal">
      <template #body>
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-3">
              <div class="p-2 bg-green-100 rounded-lg">
                <LucidePackage class="size-6 text-green-600" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900">Procurement Bucket</h3>
                <p class="text-sm text-gray-600">{{ tasks.length }} approved tasks</p>
              </div>
            </div>
            <Button 
              @click="showBucketModal = false"
              class="bg-gray-100 text-gray-700 hover:bg-gray-200"
            >
              <LucideX class="size-4" />
            </Button>
          </div>
          
          <div v-if="tasks.length === 0" class="text-center py-12">
            <div class="relative mx-auto w-24 h-24 mb-4">
              <div class="absolute inset-0 bg-gray-100 rounded-full flex items-center justify-center">
                <LucidePackage class="size-8 text-gray-400" />
              </div>
            </div>
            <h4 class="text-lg font-medium text-gray-900 mb-2">Empty Bucket</h4>
            <p class="text-gray-500">No approved tasks in bucket yet</p>
          </div>
          
          <div v-else class="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
            <div 
              v-for="(task, index) in tasks"
              :key="task.name"
              :class="[
                'p-4 bg-white rounded-lg border border-gray-200 hover:bg-gray-50 transition-all duration-200 cursor-pointer group',
                index === 0 ? 'ring-2 ring-green-200 bg-green-50' : ''
              ]"
              @click="handleTaskClick(task)"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-2">
                    <h4 class="font-medium text-gray-900 truncate">{{ task.title }}</h4>
                    <span 
                      v-if="index === 0"
                      class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full"
                    >
                      Latest
                    </span>
                  </div>
                  <p class="text-sm text-gray-600 mb-2">{{ task.customer_title }}</p>
                  <div class="flex items-center gap-2 flex-wrap">
                    <span 
                      :class="[
                        'px-2 py-1 text-xs rounded-full',
                        getPriorityClasses(task.priority)
                      ]"
                    >
                      {{ task.priority }}
                    </span>
                    <span class="text-xs text-gray-400">{{ formatDate(task.modified) }}</span>
                    <span class="text-xs text-gray-400">•</span>
                    <span class="text-xs text-gray-400">Cycle #{{ task.cycle_count || 1 }}</span>
                  </div>
                </div>
                <div class="ml-4 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                  <LucideChevronRight class="size-4 text-gray-400" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Button, Dialog } from 'frappe-ui'
import { formatDistanceToNow } from 'date-fns'
import LucidePackage from '~icons/lucide/package'
import LucideX from '~icons/lucide/x'
import LucideChevronRight from '~icons/lucide/chevron-right'

interface Task {
  name: string
  title: string
  customer_title: string
  priority: string
  modified: string
  cycle_count?: number
}

interface Props {
  tasks: Task[]
  bucketBounce?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'task-clicked': [task: Task]
  'bucket-clicked': []
}>()

// State
const showBucketModal = ref(false)
const showDropAnimation = ref(false)
const previousTaskCount = ref(0)

// Computed properties
const visibleTasks = computed(() => props.tasks.slice(0, 3))

const bucketClasses = computed(() => {
  const hasTasks = props.tasks.length > 0
  return hasTasks 
    ? 'bg-green-500 shadow-lg shadow-green-200 hover:bg-green-600' 
    : 'bg-gray-300 hover:bg-gray-400'
})

// Methods
const getDocumentStackClasses = (index) => {
  const colors = ['bg-white', 'bg-gray-50', 'bg-gray-100', 'bg-gray-200']
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

const handleDocumentClick = (task) => {
  emit('task-clicked', task)
}

const handleTaskClick = (task) => {
  emit('task-clicked', task)
  showBucketModal.value = false
}

// Watch for new tasks to trigger drop animation
watch(() => props.tasks.length, (newCount, oldCount) => {
  if (newCount > oldCount && oldCount > 0) {
    // Show drop animation
    showDropAnimation.value = true
    
    // Hide animation after it completes
    setTimeout(() => {
      showDropAnimation.value = false
    }, 1000)
  }
  
  previousTaskCount.value = newCount
}, { immediate: true })
</script>

<style scoped>
/* Custom scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Smooth transitions */
.transition-all {
  transition: all 0.3s ease-out;
}

/* Document stack animation */
@keyframes documentDrop {
  0% {
    transform: translateY(-20px) scale(0.8);
    opacity: 0;
  }
  50% {
    transform: translateY(-10px) scale(0.9);
    opacity: 0.8;
  }
  100% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

.document-drop {
  animation: documentDrop 0.5s ease-out;
}
</style>
