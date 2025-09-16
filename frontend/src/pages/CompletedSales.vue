<template>
  <div class="h-full flex flex-col bg-gradient-to-br from-green-50 to-blue-50">
    <!-- Header -->
    <div class="flex items-center justify-between p-6 bg-white/80 backdrop-blur-sm border-b border-outline-gray-1">
      <div class="flex items-center gap-4">
        <div class="p-2 bg-green-100 rounded-lg">
          <LucideCheckCircle class="size-6 text-green-600" />
        </div>
        <div>
          <h1 class="text-2xl font-bold text-ink-gray-9">Completed Sales Tasks</h1>
          <p class="text-sm text-ink-gray-6">Sales tasks ready to be moved to procurement</p>
        </div>
      </div>
      
      <!-- Stats -->
      <div v-if="stats" class="flex items-center gap-6">
        <div class="text-center">
          <div class="text-2xl font-bold text-ink-gray-9">{{ stats.total_tasks }}</div>
          <div class="text-xs text-ink-gray-6">Completed Sales</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-green-600">{{ stats.high_priority }}</div>
          <div class="text-xs text-ink-gray-6">High Priority</div>
        </div>
      </div>
    </div>

    <!-- Filters and Controls -->
    <div class="flex items-center justify-between px-6 py-4 bg-white/50 border-b border-outline-gray-1">
      <div class="flex items-center gap-4">
        <!-- Customer Filter -->
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-ink-gray-7">Customer:</span>
          <Autocomplete
            v-model="selectedCustomer"
            :options="customerOptions"
            placeholder="All customers"
            @change="onCustomerFilter"
            class="w-64"
          />
        </div>

        <!-- Sort Options -->
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-ink-gray-7">Sort by:</span>
          <select
            v-model="sortBy"
            @change="onSortChange"
            class="px-3 py-1.5 text-sm border border-outline-gray-2 rounded-md bg-white"
          >
            <option value="modified">Last Modified</option>
            <option value="priority">Priority</option>
            <option value="title">Title</option>
            <option value="created_by_sales">Created By</option>
          </select>
          <button
            @click="toggleSortOrder"
            class="p-1.5 text-ink-gray-6 hover:text-ink-gray-8 hover:bg-gray-100 rounded-md transition-colors"
          >
            <LucideArrowUpDown class="size-4" />
          </button>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-2">
        <!-- Move All to Bucket Button -->
        <button
          @click="moveAllToBucket"
          :disabled="loading || completedSalesTasks.length === 0"
          class="flex items-center gap-2 px-3 py-1.5 text-sm bg-orange-100 text-orange-700 rounded-md hover:bg-orange-200 transition-colors disabled:opacity-50"
        >
          <LucidePackage class="size-4" />
          Move All to Procurement
        </button>
        
        <!-- Refresh Button -->
        <button
          @click="refreshData"
          :disabled="loading"
          class="flex items-center gap-2 px-3 py-1.5 text-sm text-ink-gray-6 hover:text-ink-gray-8 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
        >
          <LucideRefreshCw :class="['size-4', { 'animate-spin': loading }]" />
          Refresh
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <LucideLoader2 class="size-8 text-ink-gray-5 animate-spin mx-auto mb-4" />
        <p class="text-ink-gray-6">Loading completed sales tasks...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <LucideAlertCircle class="size-8 text-red-500 mx-auto mb-4" />
        <p class="text-red-600 mb-4">{{ error }}</p>
        <button
          @click="refreshData"
          class="px-4 py-2 bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
        >
          Try Again
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="completedSalesTasks.length === 0" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <LucideCheckCircle class="size-16 text-ink-gray-4 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-ink-gray-7 mb-2">No completed sales tasks</h3>
        <p class="text-ink-gray-6">Completed sales tasks will appear here for procurement processing</p>
      </div>
    </div>

    <!-- Completed Sales Tasks Grid -->
    <div v-else class="flex-1 overflow-auto p-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <CompletedSalesCard
          v-for="task in completedSalesTasks"
          :key="task.name"
          :task="task"
          @task-moved="handleTaskMoved"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { Button, Dialog, Autocomplete } from 'frappe-ui'
import { useBucketTasks } from '@/data/artworkTasks'
import { apiCall } from '@/utils/api'
import CompletedSalesCard from '@/components/CompletedSalesCard.vue'
import LucideCheckCircle from '~icons/lucide/check-circle'
import LucideRefreshCw from '~icons/lucide/refresh-cw'
import LucideLoader2 from '~icons/lucide/loader-2'
import LucideAlertCircle from '~icons/lucide/alert-circle'
import LucideArrowUpDown from '~icons/lucide/arrow-up-down'
import LucidePackage from '~icons/lucide/package'

// Composables
const {
  fetchCompletedSalesTasks,
  moveCompletedSalesToBucket
} = useBucketTasks()

// State
const completedSalesTasks = ref([])
const loading = ref(false)
const error = ref(null)
const stats = ref(null)
const selectedCustomer = ref('')
const customers = ref([])
const sortBy = ref('modified')
const sortOrder = ref('desc')

// Computed
const customerOptions = computed(() => {
  const options = [{ label: 'All customers', value: '' }]
  if (customers.value.length > 0) {
    options.push(...customers.value.map(customer => ({
      label: customer.title,
      value: customer.name
    })))
  }
  return options
})

// Methods
const loadCustomers = async () => {
  try {
    const customerData = await apiCall('gameplan.api.get_customers')
    customers.value = customerData || []
  } catch (err) {
    console.error('Error loading customers:', err)
  }
}

const refreshData = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await fetchCompletedSalesTasks(selectedCustomer.value, sortBy.value, sortOrder.value)
    // Extract tasks from the response object
    completedSalesTasks.value = response.tasks || response || []
    
    // Calculate stats
    stats.value = {
      total_tasks: completedSalesTasks.value.length,
      high_priority: completedSalesTasks.value.filter(task => task.priority === 'High' || task.priority === 'Urgent').length
    }
  } catch (err) {
    error.value = err.message
    console.error('Error refreshing data:', err)
  } finally {
    loading.value = false
  }
}

const onCustomerFilter = () => {
  refreshData()
}

const onSortChange = () => {
  refreshData()
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  refreshData()
}

const handleTaskMoved = (task) => {
  // Remove the task from the list
  const index = completedSalesTasks.value.findIndex(t => t.name === task.name)
  if (index > -1) {
    completedSalesTasks.value.splice(index, 1)
  }
  
  // Update stats
  if (stats.value) {
    stats.value.total_tasks = completedSalesTasks.value.length
    stats.value.high_priority = completedSalesTasks.value.filter(t => t.priority === 'High' || t.priority === 'Urgent').length
  }
}

const moveAllToBucket = async () => {
  if (completedSalesTasks.value.length === 0) return
  
  const confirmed = confirm(`Are you sure you want to move all ${completedSalesTasks.value.length} tasks to the procurement bucket?`)
  if (!confirmed) return
  
  loading.value = true
  
  try {
    const promises = completedSalesTasks.value.map(task => 
      moveCompletedSalesToBucket(task.name)
    )
    
    await Promise.all(promises)
    
    // Clear the list
    completedSalesTasks.value = []
    stats.value = { total_tasks: 0, high_priority: 0 }
    
  } catch (err) {
    error.value = err.message
    console.error('Error moving all tasks to bucket:', err)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadCustomers(),
    refreshData()
  ])
})
</script>
