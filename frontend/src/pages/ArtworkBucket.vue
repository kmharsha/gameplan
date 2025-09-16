<template>
  <div class="h-full flex flex-col bg-gradient-to-br from-slate-50 to-blue-50">
    <!-- Header -->
    <div class="flex items-center justify-between p-6 bg-white/80 backdrop-blur-sm border-b border-outline-gray-1">
      <div class="flex items-center gap-4">
        <div class="p-2 bg-orange-100 rounded-lg">
          <LucidePackage class="size-6 text-orange-600" />
        </div>
        <div>
          <h1 class="text-2xl font-bold text-ink-gray-9">Procurement Bucket</h1>
          <p class="text-sm text-ink-gray-6">Tasks ready for procurement processing</p>
        </div>
      </div>
      
      <!-- Stats -->
      <div v-if="stats" class="flex items-center gap-6">
        <div class="text-center">
          <div class="text-2xl font-bold text-ink-gray-9">{{ stats.total_tasks }}</div>
          <div class="text-xs text-ink-gray-6">Total Tasks</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-orange-600">{{ getHighCycleCount() }}</div>
          <div class="text-xs text-ink-gray-6">High Cycle</div>
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
            <option value="cycle_count">Cycle Count</option>
            <option value="modified">Last Modified</option>
            <option value="priority">Priority</option>
            <option value="title">Title</option>
          </select>
          <button
            @click="toggleSortOrder"
            class="p-1.5 text-ink-gray-6 hover:text-ink-gray-8 hover:bg-gray-100 rounded-md transition-colors"
          >
            <LucideArrowUpDown class="size-4" />
          </button>
        </div>
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

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <LucideLoader2 class="size-8 text-ink-gray-5 animate-spin mx-auto mb-4" />
        <p class="text-ink-gray-6">Loading bucket tasks...</p>
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
    <div v-else-if="bucketTasks.length === 0" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <LucidePackage class="size-16 text-ink-gray-4 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-ink-gray-7 mb-2">No tasks in bucket</h3>
        <p class="text-ink-gray-6">Tasks from completed sales cycles will appear here</p>
      </div>
    </div>

    <!-- Bucket Tasks Grid -->
    <div v-else class="flex-1 overflow-auto p-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <BucketTaskCard
          v-for="task in bucketTasks"
          :key="task.name"
          :task="task"
          @move-from-bucket="handleMoveFromBucket"
          @view="handleTaskView"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Dialog, Autocomplete } from 'frappe-ui'
import { useBucketTasks } from '@/data/artworkTasks'
import { apiCall } from '@/utils/api'
import BucketTaskCard from '@/components/BucketTaskCard.vue'
import LucidePackage from '~icons/lucide/package'
import LucideRefreshCw from '~icons/lucide/refresh-cw'
import LucideLoader2 from '~icons/lucide/loader-2'
import LucideAlertCircle from '~icons/lucide/alert-circle'
import LucideArrowUpDown from '~icons/lucide/arrow-up-down'

// Composables
const router = useRouter()
const {
  bucketTasks,
  loading,
  error,
  stats,
  fetchBucketTasks,
  fetchBucketStats,
  moveFromBucket
} = useBucketTasks()

// State
const selectedCustomer = ref('')
const customers = ref([])
const sortBy = ref('cycle_count')
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
  await Promise.all([
    fetchBucketTasks(selectedCustomer.value, sortBy.value, sortOrder.value),
    fetchBucketStats()
  ])
}

const onCustomerFilter = () => {
  fetchBucketTasks(selectedCustomer.value, sortBy.value, sortOrder.value)
}

const onSortChange = () => {
  fetchBucketTasks(selectedCustomer.value, sortBy.value, sortOrder.value)
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  fetchBucketTasks(selectedCustomer.value, sortBy.value, sortOrder.value)
}

const handleMoveFromBucket = async (taskName, newStatus) => {
  try {
    await moveFromBucket(taskName, newStatus)
    // Refresh stats after moving a task
    await fetchBucketStats()
  } catch (err) {
    console.error('Error moving task from bucket:', err)
  }
}

const handleTaskView = (task) => {
  // Navigate to the task detail page
  router.push({ name: 'ArtworkTask', params: { taskId: task.name } })
}

const getHighCycleCount = () => {
  if (!stats.value?.cycle_stats) return 0
  return stats.value.cycle_stats
    .filter(stat => stat.cycle_count > 1)
    .reduce((sum, stat) => sum + stat.count, 0)
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadCustomers(),
    refreshData()
  ])
})
</script>

