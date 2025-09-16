<template>
  <div class="flex flex-col h-full bg-mesh-2 bg-pattern-grid">
    <!-- Header -->
    <div class="flex flex-col">
      <div class="flex items-center justify-between px-6 py-4 border-b border-outline-gray-2 bg-white/70 backdrop-blur-sm shadow-lg">
        <div class="flex items-center gap-3">
          <LucidePackage class="size-5" />
          <h1 class="text-xl font-semibold text-ink-gray-9">Sales Bucket</h1>
        </div>
        <div class="flex items-center gap-3">
          <Button 
            @click="refreshBucket" 
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
      
      <!-- Filters and Stats -->
      <div class="flex items-center gap-4 px-6 py-3 bg-white/50 border-b border-outline-gray-1">
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
          <!-- Clear filter button -->
          <button
            v-if="selectedCustomer"
            @click="clearCustomerFilter"
            class="p-1 text-ink-gray-5 hover:text-ink-gray-7 hover:bg-ink-gray-1 rounded"
            title="Clear customer filter"
          >
            <LucideX class="size-4" />
          </button>
        </div>
        
        <!-- Sort Options -->
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-ink-gray-7">Sort by:</span>
          <select 
            v-model="sortBy" 
            @change="onSortChange"
            class="px-3 py-1.5 text-sm border border-outline-gray-2 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="cycle_count">Cycle Count</option>
            <option value="modified">Last Modified</option>
            <option value="priority">Priority</option>
            <option value="title">Title</option>
          </select>
          <button
            @click="toggleSortOrder"
            class="p-1 text-ink-gray-5 hover:text-ink-gray-7 hover:bg-ink-gray-1 rounded"
            :title="`Sort ${sortOrder === 'desc' ? 'Descending' : 'Ascending'}`"
          >
            <LucideArrowUpDown class="size-4" />
          </button>
        </div>
        
        <!-- Task Count and Filter Status -->
        <div class="ml-auto flex items-center gap-3 text-xs text-ink-gray-5">
          <div v-if="selectedCustomer" class="flex items-center gap-1 px-2 py-1 bg-indigo-50 text-indigo-700 rounded-full border border-indigo-200">
            <LucideBuilding2 class="size-3" />
            <span>{{ getSelectedCustomerName() }}</span>
          </div>
          <div>
            {{ filteredTasks.length }} completed sales tasks
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !bucketTasks.length" class="flex-1 flex items-center justify-center relative">
      <!-- Decorative background elements -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="absolute top-1/4 left-1/4 w-32 h-32 bg-orange-200/20 rounded-full blur-xl animate-pulse"></div>
        <div class="absolute bottom-1/3 right-1/3 w-40 h-40 bg-amber-200/20 rounded-full blur-xl animate-pulse delay-1000"></div>
        <div class="absolute top-1/2 right-1/4 w-24 h-24 bg-yellow-200/20 rounded-full blur-xl animate-pulse delay-500"></div>
      </div>
      <div class="text-center bg-white/90 backdrop-blur-sm rounded-xl p-8 shadow-lg border border-slate-200/50">
        <LucideLoader2 class="size-8 animate-spin mx-auto mb-4 text-orange-600" />
        <p class="text-ink-gray-6">Loading bucket tasks...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <LucideAlertCircle class="size-8 mx-auto mb-4 text-red-500" />
        <p class="text-red-500 font-medium">Error loading bucket tasks</p>
        <p class="text-ink-gray-6 text-sm mt-2">{{ error }}</p>
        <Button @click="refreshBucket" class="mt-4">Try Again</Button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredTasks.length === 0 && !loading" class="flex-1 flex items-center justify-center relative">
      <!-- Decorative background elements -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="absolute top-1/4 left-1/4 w-32 h-32 bg-orange-200/20 rounded-full blur-xl"></div>
        <div class="absolute bottom-1/3 right-1/3 w-40 h-40 bg-amber-200/20 rounded-full blur-xl"></div>
        <div class="absolute top-1/2 right-1/4 w-24 h-24 bg-yellow-200/20 rounded-full blur-xl"></div>
      </div>
      <div class="text-center bg-white/90 backdrop-blur-sm rounded-xl p-8 shadow-lg border border-slate-200/50">
        <LucidePackage class="size-12 mx-auto mb-4 text-ink-gray-4" />
        <h3 class="text-lg font-medium text-ink-gray-9 mb-2">No completed sales tasks</h3>
        <p class="text-ink-gray-6 text-center max-w-md mb-6">
          <span v-if="selectedCustomer">No completed sales tasks found for the selected customer.</span>
          <span v-else>No completed sales tasks are currently available. Completed sales tasks will appear here for procurement team to pick up.</span>
        </p>
        <div class="flex items-center justify-center gap-3">
          <Button 
            v-if="selectedCustomer"
            @click="clearCustomerFilter" 
            class="bg-blue-600 text-white hover:bg-blue-700"
          >
            Clear Customer Filter
          </Button>
          <Button 
            @click="refreshBucket" 
            class="bg-surface-white border border-outline-gray-2 text-ink-gray-7 hover:bg-surface-gray-1"
          >
            Refresh
          </Button>
        </div>
      </div>
    </div>

    <!-- Bucket Tasks List -->
    <div v-else class="flex-1 overflow-hidden">
      <div class="h-full overflow-y-auto p-6">
        <div class="grid gap-4">
          <SalesBucketTaskCard
            v-for="task in filteredTasks"
            :key="task.name"
            :task="task"
            @view="handleTaskView"
          />
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
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
import LucideX from '~icons/lucide/x'
import LucideBuilding2 from '~icons/lucide/building-2'
import LucideArrowUpDown from '~icons/lucide/arrow-up-down'

const router = useRouter()
const { loading, error, fetchCompletedSalesTasks, moveCompletedSalesToBucket } = useBucketTasks()

// State for sales tasks
const salesTasks = ref([])

// Watch for changes in salesTasks
watch(salesTasks, (newValue, oldValue) => {
  console.log('[ProcurementBucket] salesTasks changed from:', oldValue?.length || 0, 'to:', newValue?.length || 0)
  console.log('[ProcurementBucket] New salesTasks:', newValue)
}, { deep: true })

const selectedCustomer = ref('')
const customers = ref([])
const sortBy = ref('modified')
const sortOrder = ref('desc')

// Customer options for filter
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

// Filtered and sorted tasks
const filteredTasks = computed(() => {
  console.log('[ProcurementBucket] Computing filteredTasks...')
  console.log('[ProcurementBucket] salesTasks.value:', salesTasks.value)
  console.log('[ProcurementBucket] selectedCustomer.value:', selectedCustomer.value)
  
  let tasks = salesTasks.value || []
  console.log('[ProcurementBucket] Initial tasks count:', tasks.length)
  
  // Filter by customer
  if (selectedCustomer.value) {
    const customerValue = typeof selectedCustomer.value === 'object' 
      ? selectedCustomer.value.value 
      : selectedCustomer.value
    
    tasks = tasks.filter(task => task.customer === customerValue)
    console.log('[ProcurementBucket] After customer filter:', tasks.length)
  }
  
  // Sort tasks
  tasks.sort((a, b) => {
    let aValue = a[sortBy.value]
    let bValue = b[sortBy.value]
    
    // Handle different data types
    if (sortBy.value === 'modified' || sortBy.value === 'last_status_change') {
      aValue = new Date(aValue).getTime()
      bValue = new Date(bValue).getTime()
    } else if (sortBy.value === 'cycle_count') {
      aValue = parseInt(aValue) || 0
      bValue = parseInt(bValue) || 0
    } else {
      aValue = String(aValue).toLowerCase()
      bValue = String(bValue).toLowerCase()
    }
    
    if (sortOrder.value === 'desc') {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0
    } else {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0
    }
  })
  
  console.log('[ProcurementBucket] Final filtered tasks:', tasks)
  return tasks
})

onMounted(async () => {
  console.log('[ProcurementBucket] Component mounted, starting data load...')
  await Promise.all([
    refreshSalesData(),
    loadCustomers()
  ])
  console.log('[ProcurementBucket] Initial data load completed')
})

const loadCustomers = async () => {
  try {
    console.log('[ProcurementBucket] Loading customers...')
    const customerData = await apiCall('gameplan.api.get_customers')
    console.log('[ProcurementBucket] Customers loaded:', customerData)
    customers.value = customerData || []
  } catch (err) {
    console.error('[ProcurementBucket] Error loading customers:', err)
  }
}

const onCustomerFilter = () => {
  console.log('[ProcurementBucket] Customer filter changed, refreshing data...')
  refreshSalesData()
}

const clearCustomerFilter = () => {
  selectedCustomer.value = ''
  console.log('[ProcurementBucket] Customer filter cleared, refreshing data...')
  refreshSalesData()
}

const onSortChange = () => {
  console.log('[ProcurementBucket] Sort changed, refreshing data...')
  refreshSalesData()
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc'
  console.log('[ProcurementBucket] Sort order changed, refreshing data...')
  refreshSalesData()
}

const getSelectedCustomerName = () => {
  if (!selectedCustomer.value) return ''
  
  const customerValue = typeof selectedCustomer.value === 'object' 
    ? selectedCustomer.value.value 
    : selectedCustomer.value
  
  const customer = customers.value.find(c => c.name === customerValue)
  return customer ? customer.title : customerValue
}

const refreshSalesData = async () => {
  console.log('[ProcurementBucket] Refreshing sales data...')
  loading.value = true
  error.value = null
  
  try {
    const response = await fetchCompletedSalesTasks(selectedCustomer.value, null, null, sortBy.value, sortOrder.value)
    console.log('[ProcurementBucket] Sales data response:', response)
    salesTasks.value = response.tasks || []
    console.log('[ProcurementBucket] Sales tasks loaded:', salesTasks.value)
  } catch (err) {
    error.value = err.message
    console.error('[ProcurementBucket] Error refreshing sales data:', err)
  } finally {
    loading.value = false
  }
}

const refreshBucket = () => {
  console.log('[ProcurementBucket] Refreshing sales data...')
  refreshSalesData()
}

const handleTaskView = (task) => {
  router.push({ name: 'ArtworkTask', params: { taskId: task.name } })
}
</script>
