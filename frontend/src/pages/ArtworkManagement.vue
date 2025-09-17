<template>
  <div class="flex flex-col h-full bg-mesh-1 bg-pattern-dots">
    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-4 border-b border-outline-gray-2 bg-white/70 backdrop-blur-sm shadow-lg">
      <div>
        <h1 class="text-2xl font-semibold text-ink-gray-9">Artwork Management</h1>
        <p class="text-sm text-ink-gray-6 mt-1">Manage artworks for your customers</p>
      </div>
      <Button @click="openCreateDialog" class="!bg-blue-600 !text-white hover:!bg-blue-700 inline-flex items-center">
        <PlusIcon size="md" variant="white" class="mr-2" />
        Create Artwork
      </Button>
    </div>

    <!-- Customer Filter -->
    <div class="px-6 py-4 border-b border-outline-gray-2 bg-white/50 backdrop-blur-sm">
      <div class="flex items-center gap-4">
        <div class="w-64">
          <label class="block text-sm font-medium text-ink-gray-7 mb-2">Filter by Customer</label>
          <Autocomplete
            v-model="selectedCustomer"
            :options="customerOptions"
            placeholder="All customers"
            @change="onCustomerFilter"
          />
        </div>
        <div class="flex-1"></div>
        <div class="text-sm text-ink-gray-6">
          {{ artworks.length }} artwork{{ artworks.length !== 1 ? 's' : '' }}
        </div>
      </div>
    </div>

    <!-- Artworks Grid -->
    <div class="flex-1 overflow-auto p-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div 
          v-for="artwork in filteredArtworks" 
          :key="artwork.name"
          class="bg-white/75 backdrop-blur-sm rounded-xl border border-white/30 p-5 hover:shadow-xl hover:shadow-purple-500/20 transition-all duration-300 cursor-pointer relative overflow-hidden hover:bg-white/85 hover:-translate-y-1"
          @click="selectArtwork(artwork)"
        >
          <!-- Artwork Header -->
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1 min-w-0">
              <h3 class="text-lg font-medium text-ink-gray-9 truncate">{{ artwork.title }}</h3>
              <p class="text-sm text-ink-gray-6 mt-1">{{ artwork.customer_title || artwork.customer }}</p>
            </div>
            <div 
              :class="[
                'px-2 py-1 text-xs rounded-full',
                getStatusColor(artwork.status)
              ]"
            >
              {{ artwork.status }}
            </div>
          </div>

          <!-- Artwork Info -->
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-ink-gray-6">Priority:</span>
              <span 
                :class="[
                  'px-2 py-1 text-xs rounded-full',
                  getPriorityColor(artwork.priority)
                ]"
              >
                {{ artwork.priority }}
              </span>
            </div>
            
            <div v-if="artwork.project_type" class="flex justify-between">
              <span class="text-ink-gray-6">Type:</span>
              <span class="text-ink-gray-9">{{ artwork.project_type }}</span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-ink-gray-6">Tasks:</span>
              <span class="text-ink-gray-9">{{ artwork.task_count || 0 }}</span>
            </div>

            <div v-if="artwork.due_date" class="flex justify-between">
              <span class="text-ink-gray-6">Due:</span>
              <span class="text-ink-gray-9">{{ formatDate(artwork.due_date) }}</span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center justify-end gap-2 mt-4 pt-3 border-t border-outline-gray-1 w-full">
            <Button 
              @click.stop="editArtwork(artwork)"
              class="text-xs px-3 py-1.5 bg-surface-white border border-outline-gray-2 text-ink-gray-7 hover:bg-surface-gray-1 rounded-md whitespace-nowrap"
            >
              Edit
            </Button>
            <Button 
              @click.stop="createTaskForArtwork(artwork)"
              class="text-xs px-3 py-1.5 bg-blue-50 border border-blue-200 text-blue-600 hover:bg-blue-100 inline-flex items-center rounded-md whitespace-nowrap"
            >
              <PlusIcon size="sm" variant="blue" class="mr-1" />
              <span>Task</span>
            </Button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!artworks.length" class="flex flex-col items-center justify-center py-12">
        <!-- Decorative background elements -->
        <div class="absolute inset-0 overflow-hidden pointer-events-none">
          <div class="absolute top-1/4 left-1/4 w-32 h-32 bg-blue-200/20 rounded-full blur-xl"></div>
          <div class="absolute bottom-1/3 right-1/3 w-40 h-40 bg-purple-200/20 rounded-full blur-xl"></div>
          <div class="absolute top-1/2 right-1/4 w-24 h-24 bg-indigo-200/20 rounded-full blur-xl"></div>
        </div>
        <div class="w-24 h-24 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mb-4 shadow-lg">
          <LucidePaintbrush2 class="size-10 text-ink-gray-5" />
        </div>
        <h3 class="text-lg font-medium text-ink-gray-9 mb-2">No artworks yet</h3>
        <p class="text-ink-gray-6 text-center max-w-md mb-6">
          Create your first artwork project to get started with managing tasks and workflows.
        </p>
        <Button @click="showCreateArtworkDialog = true" class="!bg-blue-600 !text-white hover:!bg-blue-700 inline-flex items-center">
          <PlusIcon size="md" variant="white" class="mr-2" />
          Create First Artwork
        </Button>
      </div>
    </div>

    <!-- Create Artwork Dialog -->
    <Dialog v-model="showCreateArtworkDialog" :options="{ title: 'Create New Artwork' }">
      <template #body>
        <CreateArtworkDialog 
          @created="onArtworkCreated"
          @cancel="showCreateArtworkDialog = false"
        />
      </template>
    </Dialog>

    <!-- Edit Artwork Dialog -->
    <Dialog v-model="showEditArtworkDialog" :options="{ title: 'Edit Artwork' }">
      <template #body>
        <EditArtworkDialog 
          v-if="selectedArtworkForEdit"
          :artwork="selectedArtworkForEdit"
          @updated="onArtworkUpdated"
          @cancel="showEditArtworkDialog = false; selectedArtworkForEdit = null"
        />
        <div v-else class="p-4 text-center text-ink-gray-6">
          Loading artwork details...
        </div>
      </template>
    </Dialog>

    <!-- Create Task Dialog -->
    <Dialog v-model="showCreateTaskDialog" :options="{ title: 'Create Task' }">
      <template #body>
        <CreateArtworkTaskDialog 
          :preset-artwork="selectedArtworkForTask"
          @created="onTaskCreated"
          @cancel="showCreateTaskDialog = false; selectedArtworkForTask = null"
        />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
/* Ensure cards maintain proper layout */
.grid > div {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* Fix button container width */
.grid > div > div:last-child {
  margin-top: auto;
}

/* Ensure buttons stay within card boundaries */
button {
  max-width: 100%;
  box-sizing: border-box;
}

/* Icon styling for better visibility */
svg {
  stroke: currentColor;
  fill: none;
  stroke-width: 1.5;
  flex-shrink: 0;
}
</style>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Button, Dialog, Autocomplete } from 'frappe-ui'
import LucidePaintbrush2 from '~icons/lucide/paintbrush-2'
import PlusIcon from '@/components/icons/PlusIcon.vue'
import { spaces } from '@/data/spaces'
import { artworkApi, apiCall } from '@/utils/api'
import CreateArtworkDialog from '@/components/CreateArtworkDialog.vue'
import EditArtworkDialog from '@/components/EditArtworkDialog.vue'
import CreateArtworkTaskDialog from '@/components/CreateArtworkTaskDialog.vue'

const artworks = ref([])
const selectedCustomer = ref('')
const showCreateArtworkDialog = ref(false)
const showEditArtworkDialog = ref(false)
const showCreateTaskDialog = ref(false)
const selectedArtworkForEdit = ref(null)
const selectedArtworkForTask = ref(null)
const loading = ref(false)

const customerOptions = computed(() => {
  const options = [{ label: 'All customers', value: '' }]
  if (spaces.data) {
    options.push(...spaces.data.map(space => ({
      label: space.title,
      value: space.name
    })))
  }
  return options
})

const filteredArtworks = computed(() => {
  if (!selectedCustomer.value) return artworks.value
  
  const customerValue = typeof selectedCustomer.value === 'object' 
    ? selectedCustomer.value.value 
    : selectedCustomer.value

  return artworks.value.filter(artwork => 
    artwork.customer === customerValue
  )
})

onMounted(async () => {
  console.log('[ArtworkManagement] Component mounted, starting initialization')
  
  await Promise.all([
    loadSpaces(),
    loadArtworks()
  ])
})

const loadSpaces = async () => {
  if (!spaces.data?.length) {
    await spaces.fetch()
  }
}

const loadArtworks = async () => {
  console.log('[ArtworkManagement] Loading artworks...')
  loading.value = true
  try {
    console.log('[ArtworkManagement] Fetching customers...')
    const customers = await apiCall('gameplan.api.get_customers')
    console.log('[ArtworkManagement] Customers response:', customers)
    
    let allArtworks = []
    
    for (const customer of customers) {
      try {
        console.log(`[ArtworkManagement] Fetching artworks for customer: ${customer.name} (${customer.title})`)
        const customerArtworks = await artworkApi.getCustomerArtworks(customer.name)
        console.log(`[ArtworkManagement] Customer ${customer.name} artworks:`, customerArtworks)
        
        allArtworks.push(...customerArtworks.map(artwork => ({
          ...artwork,
          customer_title: customer.title
        })))
      } catch (err) {
        console.error(`[ArtworkManagement] Error loading artworks for ${customer.name}:`, err)
        console.error(`[ArtworkManagement] Error details:`, {
          message: err.message,
          stack: err.stack,
          response: err.response
        })
      }
    }
    
    console.log('[ArtworkManagement] All artworks loaded:', allArtworks)
    artworks.value = allArtworks
  } catch (err) {
    console.error('[ArtworkManagement] Error loading artworks:', err)
    console.error('[ArtworkManagement] Error details:', {
      message: err.message,
      stack: err.stack,
      response: err.response
    })
    alert('Failed to load artworks: ' + (err.message || 'Unknown error'))
  } finally {
    loading.value = false
    console.log('[ArtworkManagement] Loading complete')
  }
}

const onCustomerFilter = () => {
  // Filter will be applied automatically by computed property
}

const selectArtwork = (artwork) => {
  // Navigate to artwork detail or show tasks
  console.log('Selected artwork:', artwork)
}

const editArtwork = (artwork) => {
  console.log('[ArtworkManagement] Edit artwork clicked:', artwork)
  selectedArtworkForEdit.value = artwork
  showEditArtworkDialog.value = true
}

const createTaskForArtwork = (artwork) => {
  console.log('[ArtworkManagement] Create task for artwork clicked:', artwork)
  selectedArtworkForTask.value = artwork
  showCreateTaskDialog.value = true
  console.log('[ArtworkManagement] Task creation dialog should now be open')
}

const onArtworkCreated = (newArtwork) => {
  console.log('[ArtworkManagement] Artwork created:', newArtwork)
  showCreateArtworkDialog.value = false
  loadArtworks() // Reload to get updated list
}

const onArtworkUpdated = (updatedArtwork) => {
  console.log('[ArtworkManagement] Artwork updated:', updatedArtwork)
  showEditArtworkDialog.value = false
  selectedArtworkForEdit.value = null
  loadArtworks() // Reload to get updated list
}

const onTaskCreated = (task) => {
  console.log('[ArtworkManagement] Task created:', task)
  showCreateTaskDialog.value = false
  selectedArtworkForTask.value = null
  // Optionally navigate to the task or refresh data
}

const getStatusColor = (status) => {
  const colors = {
    'Draft': 'bg-gray-100 text-gray-800',
    'In Progress': 'bg-blue-100 text-blue-800',
    'Under Review': 'bg-yellow-100 text-yellow-800',
    'Completed': 'bg-green-100 text-green-800',
    'On Hold': 'bg-orange-100 text-orange-800',
    'Cancelled': 'bg-red-100 text-red-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const getPriorityColor = (priority) => {
  const colors = {
    'Low': 'bg-gray-50 text-gray-600',
    'Medium': 'bg-blue-50 text-blue-600',
    'High': 'bg-orange-50 text-orange-600',
    'Urgent': 'bg-red-50 text-red-600'
  }
  return colors[priority] || 'bg-gray-50 text-gray-600'
}

const openCreateDialog = () => {
  console.log('[ArtworkManagement] Create Artwork button clicked')
  console.log('[ArtworkManagement] Dialog states before:', {
    showCreateArtworkDialog: showCreateArtworkDialog.value,
    showEditArtworkDialog: showEditArtworkDialog.value,
    selectedArtworkForEdit: selectedArtworkForEdit.value
  })
  
  // Reset any other dialogs
  showEditArtworkDialog.value = false
  showCreateTaskDialog.value = false
  selectedArtworkForEdit.value = null
  selectedArtworkForTask.value = null
  
  // Open create dialog
  showCreateArtworkDialog.value = true
  
  console.log('[ArtworkManagement] Dialog states after:', {
    showCreateArtworkDialog: showCreateArtworkDialog.value,
    showEditArtworkDialog: showEditArtworkDialog.value,
    selectedArtworkForEdit: selectedArtworkForEdit.value
  })
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}
</script>
