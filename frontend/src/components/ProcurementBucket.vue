<template>
  <div class="bg-white rounded-lg border border-outline-gray-2 p-4 mb-6">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <LucidePackage class="size-5 text-orange-600" />
        <h3 class="text-lg font-semibold text-ink-gray-9">Sales Bucket</h3>
        <span class="text-sm text-ink-gray-6">({{ totalCount }} completed sales tasks)</span>
      </div>
      <Button 
        @click="refreshCompletedSales" 
        :loading="loading"
        class="bg-surface-white border border-outline-gray-2 text-ink-gray-7 hover:bg-surface-gray-1"
      >
        <template #prefix>
          <LucideRefreshCw class="size-4" />
        </template>
        Refresh
      </Button>
    </div>
    
    <!-- Filters -->
    <div class="flex items-center gap-4 mb-4 p-3 bg-gray-50 rounded-lg">
      <!-- Task Title Filter -->
      <div class="flex items-center gap-2">
        <span class="text-sm font-medium text-ink-gray-7">Task Title:</span>
        <input
          v-model="artworkTitleFilter"
          @input="onFilterChange"
          type="text"
          placeholder="Enter task title"
          class="px-3 py-1.5 text-sm border border-outline-gray-2 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 w-48"
        />
        <button
          v-if="artworkTitleFilter"
          @click="clearArtworkTitleFilter"
          class="p-1 text-ink-gray-5 hover:text-ink-gray-7 hover:bg-ink-gray-1 rounded"
          title="Clear task title filter"
        >
          <LucideX class="size-4" />
        </button>
      </div>
      
      <!-- Customer Filter -->
      <div class="flex items-center gap-2">
        <span class="text-sm font-medium text-ink-gray-7">Customer:</span>
        <select
          v-model="selectedCustomer"
          @change="onFilterChange"
          class="px-3 py-1.5 text-sm border border-outline-gray-2 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 w-48"
        >
          <option value="">All customers</option>
          <option v-for="customer in customers" :key="customer.name" :value="customer.name">
            {{ customer.title }}
          </option>
        </select>
        <button
          v-if="selectedCustomer"
          @click="clearCustomerFilter"
          class="p-1 text-ink-gray-5 hover:text-ink-gray-7 hover:bg-ink-gray-1 rounded"
          title="Clear customer filter"
        >
          <LucideX class="size-4" />
        </button>
      </div>
      
      <!-- Artwork Filter -->
      <div class="flex items-center gap-2">
        <span class="text-sm font-medium text-ink-gray-7">Artwork:</span>
        <select
          v-model="selectedArtwork"
          @change="onFilterChange"
          class="px-3 py-1.5 text-sm border border-outline-gray-2 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 w-48"
        >
          <option value="">All artworks</option>
          <option v-for="artwork in artworks" :key="artwork.name" :value="artwork.name">
            {{ artwork.title }}
          </option>
        </select>
        <button
          v-if="selectedArtwork"
          @click="clearArtworkFilter"
          class="p-1 text-ink-gray-5 hover:text-ink-gray-7 hover:bg-ink-gray-1 rounded"
          title="Clear artwork filter"
        >
          <LucideX class="size-4" />
        </button>
      </div>
      
      <!-- Date Range Filter -->
      <div class="flex items-center gap-2">
        <span class="text-sm font-medium text-ink-gray-7">Date Range:</span>
        <input
          v-model="startDate"
          @change="onFilterChange"
          type="date"
          class="px-3 py-1.5 text-sm border border-outline-gray-2 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <span class="text-sm text-ink-gray-5">to</span>
        <input
          v-model="endDate"
          @change="onFilterChange"
          type="date"
          class="px-3 py-1.5 text-sm border border-outline-gray-2 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          v-if="startDate || endDate"
          @click="clearDateFilter"
          class="p-1 text-ink-gray-5 hover:text-ink-gray-7 hover:bg-ink-gray-1 rounded"
          title="Clear date filter"
        >
          <LucideX class="size-4" />
        </button>
      </div>
    </div>
    
    <!-- Completed Sales Tasks List -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <LucideLoader2 class="size-6 animate-spin text-ink-gray-5" />
      <span class="ml-2 text-ink-gray-6">Loading completed sales tasks...</span>
    </div>
    
    <div v-else-if="completedSalesTasks.length === 0" class="text-center py-8">
      <LucidePackage class="size-12 mx-auto mb-4 text-ink-gray-4" />
      <h4 class="text-lg font-medium text-ink-gray-7 mb-2">No completed sales tasks</h4>
      <p class="text-ink-gray-5">Completed sales tasks will appear here for procurement team to pick up.</p>
    </div>
    
    <div v-else class="max-h-80 overflow-y-auto custom-scrollbar">
      <div class="space-y-3 pr-3">
        <div 
          v-for="task in completedSalesTasks" 
          :key="task.name"
          class="task-card flex items-center justify-between p-4 rounded-lg"
        >
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h4 class="font-medium text-ink-gray-9">{{ task.title }}</h4>
              <span class="status-completed px-2 py-1 text-xs font-medium rounded-full">
                {{ task.status }}
              </span>
              <span v-if="task.in_procurement" class="status-procurement px-2 py-1 text-xs font-medium rounded-full">
                In Procurement
              </span>
            </div>
            <div class="flex items-center gap-4 text-sm text-ink-gray-6">
              <span><strong>Artwork:</strong> {{ task.artwork_title }}</span>
              <span><strong>Customer:</strong> {{ task.customer_title }}</span>
              <span><strong>Priority:</strong> {{ task.priority }}</span>
              <span><strong>Completed:</strong> {{ formatDate(task.modified) }}</span>
            </div>
          </div>
          
          <div class="flex items-center gap-2">
            <!-- Create Procurement Task Button -->
            <Button 
              @click="createProcurementTask(task)"
              :loading="creatingProcurement === task.name"
              class="create-cycle-button"
              :style="{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
                color: 'white',
                border: '2px solid #8b5cf6',
                fontWeight: '700',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                boxShadow: '0 8px 25px -5px rgba(102, 126, 234, 0.4), 0 4px 10px -2px rgba(118, 75, 162, 0.3)',
                textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)'
              }"
            >
              <template #prefix>
                <LucidePlus class="size-4" />
              </template>
              {{ task.in_procurement ? `Create Cycle #${(task.cycle_number || 1) + 1}` : 'Create Cycle #1' }}
            </Button>
          </div>
        </div>
      </div>
      
      <!-- Pagination -->
      <div v-if="hasMore || currentPage > 0" class="flex items-center justify-between mt-4 pt-4 border-t border-outline-gray-1">
        <div class="text-sm text-ink-gray-6">
          Showing {{ completedSalesTasks.length }} of {{ totalCount }} tasks
        </div>
        <div class="flex items-center gap-2">
          <Button
            @click="loadPreviousPage"
            :disabled="currentPage === 0"
            class="bg-surface-white border border-outline-gray-2 text-ink-gray-7 hover:bg-surface-gray-1 disabled:opacity-50"
          >
            <template #prefix>
              <LucideChevronLeft class="size-4" />
            </template>
            Previous
          </Button>
          <span class="text-sm text-ink-gray-6 px-2">
            Page {{ currentPage + 1 }}
          </span>
          <Button
            @click="loadNextPage"
            :disabled="!hasMore"
            class="bg-surface-white border border-outline-gray-2 text-ink-gray-7 hover:bg-surface-gray-1 disabled:opacity-50"
          >
            Next
            <template #suffix>
              <LucideChevronRight class="size-4" />
            </template>
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Button } from 'frappe-ui'
import { apiCall } from '@/utils/api'
import LucidePackage from '~icons/lucide/package'
import LucideRefreshCw from '~icons/lucide/refresh-cw'
import LucideLoader2 from '~icons/lucide/loader-2'
import LucidePlus from '~icons/lucide/plus'
import LucideEye from '~icons/lucide/eye'
import LucideX from '~icons/lucide/x'
import LucideChevronLeft from '~icons/lucide/chevron-left'
import LucideChevronRight from '~icons/lucide/chevron-right'

const completedSalesTasks = ref([])
const loading = ref(false)
const creatingProcurement = ref(null)
const totalCount = ref(0)
const hasMore = ref(false)
const currentPage = ref(0)
const pageSize = 20

// Filter states
const artworkTitleFilter = ref('')
const selectedCustomer = ref('')
const selectedArtwork = ref('')
const startDate = ref('')
const endDate = ref('')
const customers = ref([])
const artworks = ref([])

// Debounce timer for artwork title filter
let filterTimeout = null

const fetchCompletedSales = async (resetPage = true) => {
  if (resetPage) {
    currentPage.value = 0
  }
  
  loading.value = true
  try {
    const params = {
      customer_filter: selectedCustomer.value || null,
      artwork_title_filter: artworkTitleFilter.value || null,
      artwork_filter: selectedArtwork.value || null,
      start_date: startDate.value || null,
      end_date: endDate.value || null,
      sort_by: 'modified',
      sort_order: 'desc',
      limit_start: currentPage.value * pageSize,
      limit_page_length: pageSize
    }
    
    console.log('API Call Parameters:', params)
    
    const data = await apiCall('gameplan.api.get_completed_sales_tasks', params)
    
    console.log('API Response Data:', data)
    
    // Handle the API response format - data might be an array or an object with tasks property
    let tasks = []
    if (Array.isArray(data)) {
      tasks = data
    } else if (data && data.tasks) {
      tasks = data.tasks
    } else {
      tasks = []
    }
    
    console.log('Processed Tasks:', tasks)
    console.log('Reset Page:', resetPage)
    
    if (resetPage) {
      completedSalesTasks.value = tasks
    } else {
      completedSalesTasks.value = [...completedSalesTasks.value, ...tasks]
    }
    
    console.log('Updated completedSalesTasks:', completedSalesTasks.value)
    
    // Use total_count from API response if available, otherwise use tasks length
    totalCount.value = (data && data.total_count) ? data.total_count : tasks.length
    hasMore.value = false // For now, no pagination
  } catch (error) {
    console.error('Error fetching completed sales tasks:', error)
  } finally {
    loading.value = false
  }
}

const refreshCompletedSales = () => {
  fetchCompletedSales()
}

// Load data on mount
const loadCustomers = async () => {
  try {
    const data = await apiCall('gameplan.api.get_customers')
    customers.value = data || []
  } catch (error) {
    console.error('Error loading customers:', error)
  }
}

const loadArtworks = async () => {
  try {
    const data = await apiCall('gameplan.api.get_artworks')
    artworks.value = data || []
  } catch (error) {
    console.error('Error loading artworks:', error)
  }
}

// Filter methods
const onFilterChange = () => {
  // Debounce artwork title filter
  if (filterTimeout) {
    clearTimeout(filterTimeout)
  }
  
  filterTimeout = setTimeout(() => {
    fetchCompletedSales()
  }, 300)
}

const clearArtworkTitleFilter = () => {
  artworkTitleFilter.value = ''
  fetchCompletedSales()
}

const clearCustomerFilter = () => {
  selectedCustomer.value = ''
  fetchCompletedSales()
}

const clearArtworkFilter = () => {
  selectedArtwork.value = ''
  fetchCompletedSales()
}

const clearDateFilter = () => {
  startDate.value = ''
  endDate.value = ''
  fetchCompletedSales()
}

// Pagination methods
const loadNextPage = () => {
  if (hasMore.value) {
    currentPage.value++
    fetchCompletedSales(false)
  }
}

const loadPreviousPage = () => {
  if (currentPage.value > 0) {
    currentPage.value--
    fetchCompletedSales()
  }
}

const emit = defineEmits(['procurement-task-created'])

const createProcurementTask = async (salesTask) => {
  creatingProcurement.value = salesTask.name
  try {
    const result = await apiCall('gameplan.api.create_procurement_task_from_sales', {
      sales_task_name: salesTask.name
    })
    
    if (result.success) {
      // Show success message
      console.log('Procurement task created successfully:', result.message)
      console.log('Created task ID:', result.procurement_task_id)
      
      // Force a complete refresh by resetting page and clearing filters
      currentPage.value = 0
      
      // Add a small delay to ensure backend has processed the changes
      setTimeout(async () => {
        await fetchCompletedSales(true) // Force reset
        console.log('Page refreshed after creating procurement task')
      }, 500)
      
      // Emit event to parent to refresh Kanban data
      console.log('Emitting procurement-task-created event with result:', result)
      emit('procurement-task-created', result)
      
      // You could add a toast notification here if you have a notification system
      // toast.success(result.message)
    } else {
      console.error('Failed to create procurement task:', result.message)
      // You could add a toast error notification here
      // toast.error(result.message)
    }
  } catch (error) {
    console.error('Error creating procurement task:', error)
  } finally {
    creatingProcurement.value = null
  }
}


const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return 'N/A'
    
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    console.error('Error formatting date:', error)
    return 'N/A'
  }
}

onMounted(async () => {
  await Promise.all([
    fetchCompletedSales(),
    loadCustomers(),
    loadArtworks()
  ])
})
</script>

<style scoped>
.custom-scrollbar {
  /* Webkit browsers (Chrome, Safari, Edge) */
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
  /* Force scrollbar to always be visible */
  overflow-y: scroll !important;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
  margin: 4px 0;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
  border: 1px solid #f1f5f9;
  transition: all 0.2s ease;
  min-height: 20px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
  transform: scale(1.02);
}

.custom-scrollbar::-webkit-scrollbar-thumb:active {
  background: #64748b;
  transform: scale(0.98);
}

/* Firefox scrollbar styling */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
}

/* Smooth scrolling */
.custom-scrollbar {
  scroll-behavior: smooth;
}

/* Force vibrant button styling for Create Cycle buttons - Maximum specificity */
button.create-cycle-button,
.btn.create-cycle-button,
[class*="btn"].create-cycle-button,
button[class*="create-cycle-button"],
.btn[class*="create-cycle-button"],
div[class*="btn"][class*="create-cycle-button"],
button.btn.create-cycle-button,
.frappe-button.create-cycle-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
  background-color: #667eea !important;
  color: white !important;
  border: 2px solid #8b5cf6 !important;
  box-shadow: 0 8px 25px -5px rgba(102, 126, 234, 0.4), 0 4px 10px -2px rgba(118, 75, 162, 0.3) !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
  font-weight: 700 !important;
  padding: 0.75rem 1.5rem !important;
  border-radius: 0.75rem !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  position: relative !important;
  overflow: hidden !important;
  opacity: 1 !important;
  visibility: visible !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  min-height: 2.5rem !important;
  min-width: 8rem !important;
}

.create-cycle-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

button.create-cycle-button:hover,
.btn.create-cycle-button:hover,
[class*="btn"].create-cycle-button:hover {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 50%, #ec4899 100%) !important;
  background-color: #5a67d8 !important;
  color: white !important;
  border-color: #7c3aed !important;
  box-shadow: 0 15px 35px -5px rgba(102, 126, 234, 0.6), 0 8px 15px -3px rgba(118, 75, 162, 0.5) !important;
  transform: translateY(-2px) scale(1.05) !important;
}

.create-cycle-button:hover::before {
  left: 100%;
}

button.create-cycle-button:active,
.btn.create-cycle-button:active,
[class*="btn"].create-cycle-button:active {
  transform: translateY(0) scale(1.02) !important;
  box-shadow: 0 5px 15px -3px rgba(102, 126, 234, 0.4) !important;
}

button.create-cycle-button:focus,
.btn.create-cycle-button:focus,
[class*="btn"].create-cycle-button:focus {
  outline: none !important;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3), 0 8px 25px -5px rgba(102, 126, 234, 0.4) !important;
}

button.create-cycle-button svg,
.btn.create-cycle-button svg,
[class*="btn"].create-cycle-button svg {
  color: #dc2626 !important;
  stroke-width: 2.5 !important;
}

button.create-cycle-button:hover svg,
.btn.create-cycle-button:hover svg,
[class*="btn"].create-cycle-button:hover svg {
  color: #b91c1c !important;
}

/* Additional overrides for light theme visibility */
@media (prefers-color-scheme: light) {
  button.create-cycle-button,
  .btn.create-cycle-button,
  [class*="btn"].create-cycle-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    background-color: #667eea !important;
    color: #dc2626 !important;
    border: 2px solid #dc2626 !important;
    opacity: 1 !important;
    visibility: visible !important;
  }
}

/* Force visibility in all themes */
.create-cycle-button {
  z-index: 10 !important;
  position: relative !important;
}

/* Enhanced task card styling */
.task-card {
  background: linear-gradient(135deg, #f0f9ff 0%, #faf5ff 100%) !important;
  border: 1px solid #c084fc !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.task-card:hover {
  background: linear-gradient(135deg, #e0f2fe 0%, #f3e8ff 100%) !important;
  border-color: #a855f7 !important;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
  transform: translateY(-2px) !important;
}

/* Status badge enhancements */
.status-completed {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
  color: white !important;
  font-weight: 600 !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
}

.status-procurement {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
  color: white !important;
  font-weight: 600 !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
}

</style>
