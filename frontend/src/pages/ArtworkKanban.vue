<template>
  <div class="flex flex-col h-full bg-mesh-2 bg-pattern-grid">
    <!-- Header -->
    <div class="flex flex-col">
      <div class="flex items-center justify-between px-6 py-4 border-b border-outline-gray-2 bg-white/70 backdrop-blur-sm shadow-lg">
        <div class="flex items-center gap-3">
          <LucideKanbanSquare class="size-5" />
          <h1 class="text-xl font-semibold text-ink-gray-9">Artwork Tasks Kanban</h1>
        </div>
        <div class="flex items-center gap-3">
          <Button 
            @click="showCreateTaskDialog = true" 
            class="bg-surface-white border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1 inline-flex items-center"
          >
            <template #prefix>
              <LucidePlus class="size-4 stroke-current" />
            </template>
            New Task
          </Button>
          <Button 
            @click="refreshKanban" 
            :loading="loading"
            class="bg-surface-white border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1 inline-flex items-center"
          >
            <template #prefix>
              <LucideRefreshCw class="size-4 stroke-current" />
            </template>
            Refresh
          </Button>
          <Button 
            @click="forceRefresh" 
            :loading="loading"
            class="!bg-blue-600 !text-white hover:!bg-blue-700 inline-flex items-center"
          >
            <template #prefix>
              <LucideRefreshCw class="size-4 stroke-current" />
            </template>
            Force Refresh
          </Button>
        </div>
      </div>
      
      <!-- Filters -->
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
        
        <!-- Workflow Type Filter -->
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-ink-gray-7">View:</span>
          <div class="flex items-center bg-white rounded-lg border border-outline-gray-2 p-1">
            <button
              @click="selectedWorkflowType = 'sales'"
              :class="{
                'bg-green-100 text-green-800 shadow-sm': selectedWorkflowType === 'sales',
                'text-ink-gray-6 hover:text-ink-gray-8 hover:bg-gray-50': selectedWorkflowType !== 'sales'
              }"
              class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors duration-150"
            >
              Sales Cycle
            </button>
            <button
              @click="selectedWorkflowType = 'procurement'"
              :class="{
                'bg-purple-100 text-purple-800 shadow-sm': selectedWorkflowType === 'procurement',
                'text-ink-gray-6 hover:text-ink-gray-8 hover:bg-gray-50': selectedWorkflowType !== 'procurement'
              }"
              class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors duration-150"
            >
              Procurement Cycle
            </button>
          </div>
        </div>
        
        <!-- Task Count and Filter Status -->
        <div class="ml-auto flex items-center gap-3 text-xs text-ink-gray-5">
          <div v-if="selectedCustomer" class="flex items-center gap-1 px-2 py-1 bg-indigo-50 text-indigo-700 rounded-full border border-indigo-200">
            <LucideBuilding2 class="size-3" />
            <span>{{ getSelectedCustomerName() }}</span>
          </div>
          <div>
            {{ filteredTaskCount }} tasks
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !kanbanData || Object.keys(kanbanData).length === 0" class="flex-1 flex items-center justify-center relative">
      <!-- Decorative background elements -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="absolute top-1/4 left-1/4 w-32 h-32 bg-green-200/20 rounded-full blur-xl animate-pulse"></div>
        <div class="absolute bottom-1/3 right-1/3 w-40 h-40 bg-emerald-200/20 rounded-full blur-xl animate-pulse delay-1000"></div>
        <div class="absolute top-1/2 right-1/4 w-24 h-24 bg-teal-200/20 rounded-full blur-xl animate-pulse delay-500"></div>
      </div>
      <div class="text-center bg-white/90 backdrop-blur-sm rounded-xl p-8 shadow-lg border border-slate-200/50">
        <LucideLoader2 class="size-8 animate-spin mx-auto mb-4 text-green-600" />
        <p class="text-ink-gray-6">Loading artwork tasks...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <LucideAlertCircle class="size-8 mx-auto mb-4 text-red-500" />
        <p class="text-red-500 font-medium">Error loading tasks</p>
        <p class="text-ink-gray-6 text-sm mt-2">{{ error }}</p>
        <Button @click="refreshKanban" class="mt-4">Try Again</Button>
      </div>
    </div>

    <!-- Kanban Board -->
    <div v-else class="flex-1 overflow-hidden">
      <!-- Procurement Bucket (only shown for Procurement Cycle) -->
      <div v-if="selectedWorkflowType === 'procurement'" class="px-6 pt-6">
        <ProcurementBucket @procurement-task-created="handleProcurementTaskCreated" />
      </div>
      
      <!-- Empty State for Filtered Results -->
      <div v-if="filteredTaskCount === 0 && !loading" class="flex-1 flex items-center justify-center relative">
        <!-- Decorative background elements -->
        <div class="absolute inset-0 overflow-hidden pointer-events-none">
          <div class="absolute top-1/4 left-1/4 w-32 h-32 bg-blue-200/20 rounded-full blur-xl"></div>
          <div class="absolute bottom-1/3 right-1/3 w-40 h-40 bg-purple-200/20 rounded-full blur-xl"></div>
          <div class="absolute top-1/2 right-1/4 w-24 h-24 bg-indigo-200/20 rounded-full blur-xl"></div>
        </div>
        <div class="text-center bg-white/90 backdrop-blur-sm rounded-xl p-8 shadow-lg border border-slate-200/50">
          <LucideFilter class="size-12 mx-auto mb-4 text-ink-gray-4" />
          <h3 class="text-lg font-medium text-ink-gray-9 mb-2">No tasks found</h3>
          <p class="text-ink-gray-6 text-center max-w-md mb-6">
            <span v-if="selectedCustomer">No tasks found for the selected customer.</span>
            <span v-else>No tasks match the current filters.</span>
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
              @click="refreshKanban" 
              class="bg-surface-white border border-outline-gray-2 text-ink-gray-7 hover:bg-surface-gray-1"
            >
              Refresh
            </Button>
          </div>
        </div>
      </div>
      
      <!-- Kanban Board -->
      <div v-else class="flex-1 overflow-hidden relative">
        <!-- Loading Overlay -->
        <div v-if="loading" class="absolute inset-0 bg-white/80 backdrop-blur-sm z-10 flex items-center justify-center">
          <div class="flex items-center gap-3 bg-white px-6 py-4 rounded-lg shadow-lg border">
            <LucideLoader2 class="size-5 animate-spin text-blue-600" />
            <span class="text-ink-gray-7 font-medium">Refreshing tasks...</span>
          </div>
        </div>
        
        <div class="flex gap-6 p-6 h-full min-w-max overflow-x-auto">
          <template v-for="status in statusOrder" :key="`${status}-${refreshKey}`">
            <!-- Skip Final Approved column for Procurement Cycle - replace with bucket -->
            <template v-if="status === 'Final Approved' && selectedWorkflowType === 'procurement'">
              <!-- Procurement Bucket Section -->
              <div class="flex flex-col h-full max-h-[calc(100vh-200px)] w-80 bg-white rounded-lg shadow">
                <!-- Column Header -->
                <div class="p-3 font-semibold border-b">
                  <div class="flex items-center gap-3">
                    <div class="w-3 h-3 rounded-full bg-orange-500"></div>
                    <h3 class="font-medium text-ink-gray-9">Procurement Bucket</h3>
                    <span class="px-2 py-1 text-xs bg-surface-white rounded-full text-ink-gray-6">
                      {{ bucketTasksCount }}
                    </span>
                  </div>
                </div>

                <!-- Bucket Animation Area -->
                <div class="flex-1 flex items-center justify-center p-6">
                  <div class="relative">
                    <!-- Bucket Icon -->
                    <div 
                      class="relative w-24 h-24 bg-gradient-to-br from-orange-100 to-orange-200 rounded-lg border-2 border-orange-300 flex items-center justify-center cursor-pointer hover:from-orange-200 hover:to-orange-300 transition-all duration-300 shadow-lg"
                      :class="{ 'animate-pulse': bucketBounce }"
                      @click="viewBucket"
                    >
                      <LucidePackage 
                        class="size-12 text-orange-600 transition-transform duration-300"
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
                          class="absolute -top-2 -right-2 w-6 h-8 bg-white border border-orange-300 rounded-sm shadow-lg"
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
                    <div class="absolute -bottom-2 -right-2 w-16 h-10">
                      <div 
                        v-for="(task, index) in visibleBucketTasks"
                        :key="task.name"
                        :class="[
                          'absolute w-10 h-8 bg-white border border-orange-200 rounded-sm shadow-sm transform transition-all duration-500',
                          getDocumentStackClasses(index)
                        ]"
                        :style="{ 
                          zIndex: 10 - index,
                          transform: `translateX(${index * 2}px) translateY(${index * 2}px) rotate(${index * 2}deg)`
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
                        class="absolute w-10 h-8 bg-orange-200 border border-orange-300 rounded-sm shadow-sm flex items-center justify-center text-xs font-medium text-orange-600"
                        :style="{ 
                          zIndex: 7,
                          transform: `translateX(4px) translateY(4px) rotate(4deg)`
                        }"
                      >
                        +{{ bucketTasksCount - 3 }}
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- View All Tasks Button -->
                <div class="p-3 border-t border-outline-gray-1">
                  <button 
                    @click="viewBucket"
                    class="w-full px-4 py-2 text-sm font-medium text-orange-700 bg-orange-50 border border-orange-200 rounded-md hover:bg-orange-100 transition-colors"
                  >
                    View All Tasks
                  </button>
                </div>
              </div>
            </template>
            <!-- Skip Completed column for Sales Cycle - replace with Sales Bucket -->
            <template v-else-if="status === 'Completed' && selectedWorkflowType === 'sales'">
              <!-- Sales Bucket Section -->
              <div class="flex flex-col h-full max-h-[calc(100vh-200px)] w-80 bg-white rounded-lg shadow">
                <!-- Column Header -->
                <div class="p-3 font-semibold border-b">
                  <div class="flex items-center gap-3">
                    <div class="w-3 h-3 rounded-full bg-green-500"></div>
                    <h3 class="font-medium text-ink-gray-9">Sales Bucket</h3>
                    <span class="px-2 py-1 text-xs bg-surface-white rounded-full text-ink-gray-6">
                      {{ salesBucketTasksCount }}
                    </span>
                  </div>
                </div>

                <!-- Bucket Animation Area -->
                <div class="flex-1 flex items-center justify-center p-6">
                  <div class="relative">
                    <!-- Bucket Icon -->
                    <div 
                      class="relative w-24 h-24 bg-gradient-to-br from-green-100 to-green-200 rounded-lg border-2 border-green-300 flex items-center justify-center cursor-pointer hover:from-green-200 hover:to-green-300 transition-all duration-300 shadow-lg"
                      :class="{ 'animate-pulse': salesBucketBounce }"
                      @click="viewSalesBucket"
                    >
                      <LucidePackage 
                        class="size-12 text-green-600 transition-transform duration-300"
                        :class="{ 'scale-110': salesBucketBounce }"
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
                          v-if="showSalesDropAnimation"
                          class="absolute -top-2 -right-2 w-6 h-8 bg-white border border-green-300 rounded-sm shadow-lg"
                        >
                          <div class="p-1 h-full flex flex-col justify-between">
                            <div class="w-full h-0.5 bg-green-400 rounded"></div>
                            <div class="w-full h-0.5 bg-green-400 rounded"></div>
                            <div class="w-full h-0.5 bg-green-400 rounded"></div>
                          </div>
                        </div>
                      </Transition>
                    </div>
                    
                    <!-- Stacked Documents -->
                    <div class="absolute -bottom-2 -right-2 w-16 h-10">
                      <div 
                        v-for="(task, index) in visibleSalesBucketTasks"
                        :key="task.name"
                        :class="[
                          'absolute w-10 h-8 bg-white border border-green-200 rounded-sm shadow-sm transform transition-all duration-500',
                          getDocumentStackClasses(index)
                        ]"
                        :style="{ 
                          zIndex: 10 - index,
                          transform: `translateX(${index * 2}px) translateY(${index * 2}px) rotate(${index * 2}deg)`
                        }"
                      >
                        <div class="p-1 h-full flex flex-col justify-between">
                          <div class="w-full h-0.5 bg-green-300 rounded"></div>
                          <div class="w-full h-0.5 bg-green-300 rounded"></div>
                          <div class="w-full h-0.5 bg-green-300 rounded"></div>
                        </div>
                      </div>
                      
                      <!-- Overflow Indicator -->
                      <div 
                        v-if="salesBucketTasksCount > 3"
                        class="absolute w-10 h-8 bg-green-200 border border-green-300 rounded-sm shadow-sm flex items-center justify-center text-xs font-medium text-green-600"
                        :style="{ 
                          zIndex: 7,
                          transform: `translateX(4px) translateY(4px) rotate(4deg)`
                        }"
                      >
                        +{{ salesBucketTasksCount - 3 }}
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- View All Tasks Button -->
                <div class="p-3 border-t border-outline-gray-1">
                  <button 
                    @click="viewSalesBucket"
                    class="w-full px-4 py-2 text-sm font-medium text-green-700 bg-green-50 border border-green-200 rounded-md hover:bg-green-100 transition-colors"
                  >
                    View All Tasks
                  </button>
                </div>
              </div>
            </template>
            <!-- Regular column for all other statuses -->
            <KanbanColumn
              v-else
              :title="status"
              :tasks="getFilteredTasksForStatus(status)"
              :color="STATUS_COLORS[status]"
              @task-moved="handleTaskMoved"
              @task-clicked="handleTaskClicked"
            />
          </template>
        </div>
      </div>
    </div>

    <!-- Create Task Dialog -->
    <Dialog v-model="showCreateTaskDialog">
      <template #body>
        <CreateArtworkTaskDialog 
          @created="handleTaskCreated" 
          @cancel="showCreateTaskDialog = false" 
        />
      </template>
    </Dialog>

    <!-- Status Change Dialog -->
    <Dialog v-model="showStatusDialog">
      <template #body>
        <StatusChangeDialog 
          v-if="selectedTask"
          :task="selectedTask"
          :new-status="newStatus"
          @confirmed="handleStatusChangeConfirmed"
          @cancel="showStatusDialog = false"
        />
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

    <!-- Sales Bucket Toast Notification -->
    <Transition
      enter-active-class="transform ease-out duration-300 transition"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition ease-in duration-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showSalesToast"
        class="fixed top-4 right-4 z-50 max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden"
      >
        <div class="p-4">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <LucideCheckCircle class="size-5 text-green-400" />
            </div>
            <div class="ml-3 w-0 flex-1">
              <p class="text-sm font-medium text-gray-900">{{ salesToastMessage }}</p>
              <div class="mt-2">
                <Button 
                  @click="viewSalesBucket"
                  class="text-sm bg-green-600 text-white hover:bg-green-700"
                >
                  View Sales Bucket
                </Button>
              </div>
            </div>
            <div class="ml-4 flex-shrink-0 flex">
              <button 
                @click="showSalesToast = false"
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Dialog, Autocomplete } from 'frappe-ui'
import { 
  useArtworkKanban, 
  STATUS_COLORS, 
  WORKFLOW_TYPES, 
  SALES_STATUSES, 
  PROCUREMENT_STATUSES,
  getWorkflowStatuses 
} from '@/data/artworkTasks'
import { spaces } from '@/data/spaces'
import { apiCall } from '@/utils/api'
import KanbanColumn from '@/components/KanbanColumn.vue'
import CreateArtworkTaskDialog from '@/components/CreateArtworkTaskDialog.vue'
import StatusChangeDialog from '@/components/StatusChangeDialog.vue'
import ProcurementBucket from '@/components/ProcurementBucket.vue'
import ProcurementBucketColumn from '@/components/ProcurementBucketColumn.vue'
import LucidePlus from '~icons/lucide/plus'
import LucideRefreshCw from '~icons/lucide/refresh-cw'
import LucideKanbanSquare from '~icons/lucide/kanban-square'
import LucideLoader2 from '~icons/lucide/loader-2'
import LucideAlertCircle from '~icons/lucide/alert-circle'
import LucideX from '~icons/lucide/x'
import LucideBuilding2 from '~icons/lucide/building-2'
import LucideFilter from '~icons/lucide/filter'
import LucidePackage from '~icons/lucide/package'
import LucideCheckCircle from '~icons/lucide/check-circle'

const router = useRouter()
const { kanbanData, loading, error, fetchKanbanData, moveTask } = useArtworkKanban()

const showCreateTaskDialog = ref(false)
const showStatusDialog = ref(false)
const selectedTask = ref(null)
const newStatus = ref('')
const selectedWorkflowType = ref('sales') // 'sales' or 'procurement'
const selectedCustomer = ref('')
const customers = ref([])
const refreshKey = ref(0) // Force refresh key
const procurementBucketColumn = ref(null)

// Bucket animation state
const bucketBounce = ref(false)
const showDropAnimation = ref(false)
const showToast = ref(false)
const toastMessage = ref('')

// Sales Bucket animation state
const salesBucketBounce = ref(false)
const showSalesDropAnimation = ref(false)
const showSalesToast = ref(false)
const salesToastMessage = ref('')

// Dynamic status order based on selected workflow type
const statusOrder = computed(() => {
  if (selectedWorkflowType.value === 'sales') {
    return SALES_STATUSES
  } else if (selectedWorkflowType.value === 'procurement') {
    return PROCUREMENT_STATUSES
  } else {
    // Default to sales if no valid selection
    return SALES_STATUSES
  }
})

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

// Filtered task count
const filteredTaskCount = computed(() => {
  let count = 0
  statusOrder.value.forEach(status => {
    count += getFilteredTasksForStatus(status).length
  })
  return count
})

// Bucket tasks count - count Final Approved tasks in Procurement Cycle
const bucketTasksCount = computed(() => {
  if (selectedWorkflowType.value !== 'procurement') return 0
  
  const procurementTasks = kanbanData.value['Final Approved'] || []
  return procurementTasks.filter(task => task.workflow_type === 'Procurement Cycle').length
})

// Visible bucket tasks for stacking animation - Final Approved tasks
const visibleBucketTasks = computed(() => {
  if (selectedWorkflowType.value !== 'procurement') return []
  
  const procurementTasks = kanbanData.value['Final Approved'] || []
  return procurementTasks
    .filter(task => task.workflow_type === 'Procurement Cycle')
    .slice(0, 3)
})

// Sales Bucket tasks count - count both Completed and Bucket status tasks in Sales Cycle
const salesBucketTasksCount = computed(() => {
  if (selectedWorkflowType.value !== 'sales') return 0
  
  const completedTasks = kanbanData.value['Completed'] || []
  const bucketTasks = kanbanData.value['Bucket'] || []
  const allSalesTasks = [...completedTasks, ...bucketTasks]
  return allSalesTasks.filter(task => task.workflow_type === 'Sales Cycle').length
})

// Visible sales bucket tasks for stacking animation - both Completed and Bucket status tasks
const visibleSalesBucketTasks = computed(() => {
  if (selectedWorkflowType.value !== 'sales') return []
  
  const completedTasks = kanbanData.value['Completed'] || []
  const bucketTasks = kanbanData.value['Bucket'] || []
  const allSalesTasks = [...completedTasks, ...bucketTasks]
  return allSalesTasks
    .filter(task => task.workflow_type === 'Sales Cycle')
    .slice(0, 3)
})

// Document stack classes for animation
const getDocumentStackClasses = (index) => {
  const colors = ['bg-white', 'bg-orange-50', 'bg-orange-100']
  return colors[index % colors.length]
}

// Filter tasks by workflow type and customer
const getFilteredTasksForStatus = (status: string) => {
  const tasks = kanbanData.value[status] || []
  console.log(`[ArtworkKanban] getFilteredTasksForStatus(${status}):`, tasks.length, 'tasks')
  
  let filteredTasks = tasks
  
  // Filter by workflow type
  const workflowTypeFilter = selectedWorkflowType.value === 'sales' ? 'Sales Cycle' : 'Procurement Cycle'
  filteredTasks = filteredTasks.filter(task => task.workflow_type === workflowTypeFilter)
  console.log(`[ArtworkKanban] After workflow filter (${workflowTypeFilter}):`, filteredTasks.length, 'tasks')
  
  // Filter by customer
  if (selectedCustomer.value) {
    const customerValue = typeof selectedCustomer.value === 'object' 
      ? selectedCustomer.value.value 
      : selectedCustomer.value
    
    console.log(`[ArtworkKanban] Filtering by customer: ${customerValue}`)
    console.log(`[ArtworkKanban] Tasks before customer filter:`, filteredTasks.length)
    console.log(`[ArtworkKanban] Task customers:`, filteredTasks.map(t => ({ name: t.name, customer: t.customer, customer_title: t.customer_title })))
    
    filteredTasks = filteredTasks.filter(task => task.customer === customerValue)
    
    console.log(`[ArtworkKanban] Tasks after customer filter:`, filteredTasks.length)
  }
  
  console.log(`[ArtworkKanban] Final filtered tasks for ${status}:`, filteredTasks.length)
  return filteredTasks
}

onMounted(async () => {
  await Promise.all([
    fetchKanbanData(),
    loadCustomers()
  ])
})

const loadCustomers = async () => {
  try {
    const customerData = await apiCall('gameplan.api.get_customers')
    customers.value = customerData || []
    console.log('[ArtworkKanban] Loaded customers:', customers.value)
  } catch (err) {
    console.error('Error loading customers:', err)
  }
}

const onCustomerFilter = () => {
  // Filter will be applied automatically by computed property
}

const clearCustomerFilter = () => {
  selectedCustomer.value = ''
}

const getSelectedCustomerName = () => {
  if (!selectedCustomer.value) return ''
  
  const customerValue = typeof selectedCustomer.value === 'object' 
    ? selectedCustomer.value.value 
    : selectedCustomer.value
  
  const customer = customers.value.find(c => c.name === customerValue)
  return customer ? customer.title : customerValue
}

const refreshKanban = async () => {
  console.log('[ArtworkKanban] refreshKanban called')
  refreshKey.value++ // Force component refresh
  await fetchKanbanData()
  console.log('[ArtworkKanban] fetchKanbanData completed, kanbanData:', kanbanData.value)
}

const forceRefresh = async () => {
  console.log('[ArtworkKanban] Force refresh called')
  // Clear all data first
  kanbanData.value = {}
  refreshKey.value++
  
  // Wait a bit
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // Fetch fresh data
  await fetchKanbanData()
  console.log('[ArtworkKanban] Force refresh completed, kanbanData:', kanbanData.value)
}

const handleTaskMoved = (payload) => {
  selectedTask.value = payload.task
  newStatus.value = payload.newStatus
  
  // If it's the same status, do nothing
  if (payload.task.status === payload.newStatus) {
    return
  }
  
  // Show confirmation dialog for status changes
  showStatusDialog.value = true
}

const handleTaskClicked = (task) => {
  // Don't navigate if task is completed in sales cycle (it's now in procurement bucket)
  if (task.status === 'Completed' && task.workflow_type === 'Sales Cycle') {
    // Task is completed and should remain in Sales Cycle - don't navigate
    return
  }
  
  // For all other cases, navigate to task detail
  router.push({ name: 'ArtworkTask', params: { taskId: task.name } })
}

const handleTaskCreated = async () => {
  console.log('[ArtworkKanban] Task created, refreshing kanban...')
  showCreateTaskDialog.value = false
  
  // Add a small delay to ensure the backend has processed the task creation
  await new Promise(resolve => setTimeout(resolve, 500))
  
  console.log('[ArtworkKanban] Calling refreshKanban...')
  await refreshKanban()
  console.log('[ArtworkKanban] Refresh completed')
  
  // Show success message
  console.log('[ArtworkKanban] Task created successfully and kanban refreshed!')
}

const handleStatusChangeConfirmed = async (reason, comments) => {
  try {
    console.log('[ArtworkKanban] Status change confirmed:', {
      taskName: selectedTask.value.name,
      newStatus: newStatus.value,
      workflowType: selectedTask.value.workflow_type,
      reason,
      comments
    })
    
    await moveTask(selectedTask.value.name, newStatus.value, reason, comments)
    
    // If task is moved to Final Approved in Procurement Cycle, trigger bucket animation
    if (newStatus.value === 'Final Approved' && selectedTask.value.workflow_type === 'Procurement Cycle') {
      console.log('[ArtworkKanban] Task moved to Final Approved (Procurement Bucket):', selectedTask.value.name)
      
      // Trigger bucket animation
      triggerBucketAnimation()
      
      // Refresh the kanban data
      await refreshKanban()
    }
    
    // If task is moved to Completed in Sales Cycle, move it to sales bucket
    if (newStatus.value === 'Completed' && selectedTask.value.workflow_type === 'Sales Cycle') {
      console.log('[ArtworkKanban] Task moved to Completed (Sales Bucket):', selectedTask.value.name)
      
      try {
        await apiCall('gameplan.api.move_sales_task_to_bucket', {
          task_name: selectedTask.value.name
        })
        console.log('[ArtworkKanban] Task moved to sales bucket successfully')
        
        // Trigger sales bucket animation
        triggerSalesBucketAnimation()
        
        // Refresh the kanban data
        await refreshKanban()
      } catch (bucketError) {
        console.error('Failed to move task to sales bucket:', bucketError)
        // Don't fail the entire operation if bucket move fails
      }
    }
    
    showStatusDialog.value = false
    selectedTask.value = null
    newStatus.value = ''
  } catch (error) {
    console.error('[ArtworkKanban] Failed to update task status:', error)
    console.error('[ArtworkKanban] Error details:', {
      message: error.message,
      response: error.response,
      stack: error.stack
    })
    // You might want to show a toast notification here
  }
}

const viewBucket = () => {
  router.push({ name: 'ArtworkBucket' })
}

const viewSalesBucket = () => {
  router.push({ name: 'SalesBucket' })
}

const triggerBucketAnimation = () => {
  bucketBounce.value = true
  showDropAnimation.value = true
  showToast.value = true
  toastMessage.value = '✅ Task Final Approved - Added to Procurement Bucket'
  
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

const triggerSalesBucketAnimation = () => {
  salesBucketBounce.value = true
  showSalesDropAnimation.value = true
  showSalesToast.value = true
  salesToastMessage.value = '✅ Task Completed - Added to Sales Bucket'
  
  // Reset animations
  setTimeout(() => {
    salesBucketBounce.value = false
    showSalesDropAnimation.value = false
  }, 1000)
  
  // Hide toast after 5 seconds
  setTimeout(() => {
    showSalesToast.value = false
  }, 5000)
}

const handleProcurementTaskCreated = async (result) => {
  console.log('[ArtworkKanban] Procurement task created, refreshing kanban...')
  console.log('[ArtworkKanban] Task creation result:', result)
  
  // Add a small delay to ensure backend has processed the changes
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  console.log('[ArtworkKanban] About to refresh kanban...')
  await refreshKanban()
  console.log('[ArtworkKanban] Kanban refreshed after procurement task creation')
  console.log('[ArtworkKanban] Current kanban data:', kanbanData.value)
}
</script>

