<template>
  <div class="h-full flex flex-col bg-gradient-to-br from-green-50 to-blue-50">
    <!-- Header -->
    <div class="flex items-center justify-between p-6 bg-white/80 backdrop-blur-sm border-b border-outline-gray-1">
      <div class="flex items-center gap-4">
        <div class="p-2 bg-green-100 rounded-lg">
          <LucidePackage class="size-6 text-green-600" />
        </div>
        <div>
          <h1 class="text-2xl font-bold text-ink-gray-9">Sales Bucket</h1>
          <p class="text-sm text-ink-gray-6">Completed sales tasks ready for procurement processing</p>
        </div>
      </div>
      
      <!-- Stats -->
      <div v-if="stats" class="flex items-center gap-6">
        <div class="text-center">
          <div class="text-2xl font-bold text-ink-gray-9">{{ stats.total_tasks }}</div>
          <div class="text-xs text-ink-gray-6">Total Tasks</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-green-600">{{ getHighPriorityCount() }}</div>
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
        <!-- View-only indicator -->
        <div class="flex items-center gap-2 px-3 py-1.5 text-sm text-ink-gray-6 bg-gray-100 rounded-md">
          <LucideEye class="size-4" />
          View Only
        </div>
        
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
        <p class="text-ink-gray-6">Loading sales bucket tasks...</p>
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
    <div v-else-if="salesTasks.length === 0" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <LucidePackage class="size-16 text-ink-gray-4 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-ink-gray-7 mb-2">No tasks in sales bucket</h3>
        <p class="text-ink-gray-6">Completed sales tasks will appear here for procurement processing</p>
      </div>
    </div>

    <!-- Sales Tasks Grid -->
    <div v-else class="flex-1 overflow-auto p-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <SalesBucketTaskCard
          v-for="task in salesTasks"
          :key="task.name"
          :task="task"
          @view="handleTaskView"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Dialog, Autocomplete } from 'frappe-ui'
import { useBucketTasks } from '@/data/artworkTasks'
import { apiCall } from '@/utils/api'
import SalesBucketTaskCard from '@/components/SalesBucketTaskCard.vue'
import LucidePackage from '~icons/lucide/package'
import LucideRefreshCw from '~icons/lucide/refresh-cw'
import LucideLoader2 from '~icons/lucide/loader-2'
import LucideAlertCircle from '~icons/lucide/alert-circle'
import LucideArrowUpDown from '~icons/lucide/arrow-up-down'
import LucideEye from '~icons/lucide/eye'

// Composables
const router = useRouter()
const {
  loading,
  error,
  fetchCompletedSalesTasks
} = useBucketTasks()

// State
const salesTasks = ref([])
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

// Debug computed property for salesTasks
const debugSalesTasks = computed(() => {
  console.log('[SalesBucket] salesTasks.value:', salesTasks.value)
  console.log('[SalesBucket] salesTasks.length:', salesTasks.value?.length || 0)
  return salesTasks.value
})

// Watch for changes in salesTasks
watch(salesTasks, (newValue, oldValue) => {
  console.log('[SalesBucket] salesTasks changed from:', oldValue?.length || 0, 'to:', newValue?.length || 0)
  console.log('[SalesBucket] New salesTasks:', newValue)
}, { deep: true })

// Methods
const loadCustomers = async () => {
  try {
    console.log('[SalesBucket] Loading customers...')
    const customerData = await apiCall('gameplan.api.get_customers')
    console.log('[SalesBucket] Customers loaded:', customerData)
    customers.value = customerData || []
  } catch (err) {
    console.error('[SalesBucket] Error loading customers:', err)
  }
}

const refreshData = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log('[SalesBucket] Fetching completed sales tasks...')
    const response = await fetchCompletedSalesTasks(selectedCustomer.value, null, null, sortBy.value, sortOrder.value)
    console.log('[SalesBucket] Raw API response:', response)
    
    salesTasks.value = response.tasks || []
    console.log('[SalesBucket] Processed salesTasks:', salesTasks.value)
    
    // Calculate stats
    stats.value = {
      total_tasks: salesTasks.value.length,
      high_priority: salesTasks.value.filter(task => task.priority === 'High' || task.priority === 'Urgent').length
    }
    console.log('[SalesBucket] Stats:', stats.value)
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


const handleTaskView = (task) => {
  // Navigate to the task detail page
  router.push({ name: 'ArtworkTask', params: { taskId: task.name } })
}


const getHighPriorityCount = () => {
  if (!stats.value) return 0
  return stats.value.high_priority
}

// Lifecycle
onMounted(async () => {
  console.log('[SalesBucket] Component mounted, starting data load...')
  await Promise.all([
    loadCustomers(),
    refreshData()
  ])
  console.log('[SalesBucket] Initial data load completed')
})
</script>
