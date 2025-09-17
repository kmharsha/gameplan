<template>
  <div class="p-6 max-w-2xl mx-auto">
    <div class="mb-6">
      <h2 class="text-xl font-semibold text-ink-gray-9">Create Artwork Task</h2>
      <p class="text-sm text-ink-gray-6 mt-1">Fill in the details to create a new artwork task</p>
    </div>
    
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Title -->
      <div class="form-group">
        <label class="block text-sm font-medium text-ink-gray-8 mb-2">
          Artwork Title <span class="text-red-500">*</span>
        </label>
        <TextInput
          v-model="form.title"
          placeholder="Enter artwork title"
          :error="errors.title"
          class="w-full"
        />
        <p v-if="errors.title" class="text-red-500 text-xs mt-1">{{ errors.title }}</p>
      </div>
      
      <!-- Customer -->
      <div class="form-group">
        <label class="block text-sm font-medium text-ink-gray-8 mb-2">
          Customer <span class="text-red-500">*</span>
        </label>
        <Autocomplete
          v-model="form.customer"
          :options="customerOptions"
          placeholder="Select or search customer"
          :error="errors.customer"
          @change="onCustomerChange"
          class="w-full"
        />
        <p v-if="errors.customer" class="text-red-500 text-xs mt-1">{{ errors.customer }}</p>
      </div>
      
      <!-- Artwork -->
      <div class="form-group" v-if="form.customer">
        <label class="block text-sm font-medium text-ink-gray-8 mb-2">
          Artwork <span class="text-red-500">*</span>
        </label>
        <div class="space-y-2">
          <Autocomplete
            v-model="form.artwork"
            :options="artworkOptions"
            placeholder="Select or search artwork"
            :error="errors.artwork"
            class="w-full"
          />
          <button
            type="button"
            @click="showCreateArtworkDialog = true"
            class="w-full flex items-center justify-center text-sm px-4 py-2.5 bg-surface-white border border-outline-gray-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-20"
          >
            <LucidePlus class="w-4 h-4 mr-2 stroke-current" />
            Create New Artwork
          </button>
        </div>
        <p v-if="errors.artwork" class="text-red-500 text-xs mt-1">{{ errors.artwork }}</p>
      </div>
      
      <!-- Workflow Type -->
      <div class="form-group">
        <label class="block text-sm font-medium text-ink-gray-8 mb-2">
          Workflow Type
        </label>
        <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-green-100 rounded-lg">
              <LucideArrowRight class="size-4 text-green-700" />
            </div>
            <div>
              <h4 class="font-medium text-sm text-green-800">Sales Cycle</h4>
              <p class="text-xs text-green-600 mt-0.5">Draft → Design → Approval → Completed</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Priority and Due Date Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Priority -->
        <div class="form-group">
          <label class="block text-sm font-medium text-ink-gray-8 mb-2">
            Priority
          </label>
          <Select
            v-model="form.priority"
            :options="priorityOptions"
            class="w-full"
          />
        </div>
        
        <!-- Due Date (Optional) -->
        <div class="form-group">
          <label class="block text-sm font-medium text-ink-gray-8 mb-2">
            Due Date (Optional)
          </label>
          <input
            type="date"
            v-model="form.due_date"
            class="w-full px-3 py-2 border border-outline-gray-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            placeholder="dd/mm/yyyy"
          />
        </div>
      </div>
      
      <!-- Description -->
      <div class="form-group">
        <label class="block text-sm font-medium text-ink-gray-8 mb-2">
          Description
        </label>
        <div class="border border-outline-gray-2 rounded-md overflow-hidden">
          <TextEditor
            v-model="form.description"
            placeholder="Add task description..."
            :max-height="150"
            class="prose prose-sm max-w-none"
          />
        </div>
      </div>
      
      <!-- Actions -->
      <div class="flex items-center justify-end gap-4 pt-6 border-t border-outline-gray-2">
        <Button
          type="button"
          @click="$emit('cancel')"
          class="px-6 py-2.5 bg-surface-white border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1 rounded-lg font-medium transition-colors"
        >
          Cancel
        </Button>
        <Button
          type="submit"
          :loading="creating"
          :disabled="!isFormValid"
          class="px-8 py-2.5 !bg-blue-600 !text-white hover:!bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-medium transition-colors shadow-sm"
        >
          Create Task
        </Button>
      </div>
    </form>
    
    <!-- Create Artwork Dialog -->
    <Dialog v-model="showCreateArtworkDialog">
      <template #body>
        <CreateArtworkDialog
          @created="handleArtworkCreated"
          @cancel="showCreateArtworkDialog = false"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { TextInput, TextEditor, Button, Select, Autocomplete, Dialog } from 'frappe-ui'
import { spaces } from '@/data/spaces'
import { artworkApi } from '@/utils/api'
import CreateArtworkDialog from './CreateArtworkDialog.vue'
import LucidePlus from '~icons/lucide/plus'
import LucideArrowRight from '~icons/lucide/arrow-right'

const props = defineProps<{
  presetArtwork?: {
    name: string
    title: string
    customer: string
    customer_title?: string
  }
}>()

const emit = defineEmits<{
  created: [task: any]
  cancel: []
}>()

const creating = ref(false)

const form = reactive({
  title: '',
  customer: '',
  artwork: '',
  workflow_type: 'Sales Cycle',
  priority: 'Medium',
  description: '',
  due_date: ''
})

const errors = reactive({
  title: '',
  customer: '',
  artwork: '',
  workflow_type: ''
})

const artworks = ref([])
const showCreateArtworkDialog = ref(false)

const priorityOptions = [
  { label: 'Low', value: 'Low' },
  { label: 'Medium', value: 'Medium' },
  { label: 'High', value: 'High' },
  { label: 'Urgent', value: 'Urgent' }
]

const customerOptions = computed(() => {
  if (!spaces.data) return []
  
  return spaces.data.map(space => ({
    label: space.title,
    value: space.name
  }))
})

const artworkOptions = computed(() => {
  return artworks.value.map(artwork => ({
    label: artwork.title,
    value: artwork.name
  }))
})

const isFormValid = computed(() => {
  const titleValid = form.title.trim() !== ''
  const customerValue = typeof form.customer === 'object' ? form.customer.value : form.customer
  const artworkValue = typeof form.artwork === 'object' ? form.artwork.value : form.artwork
  const customerValid = !!customerValue
  const artworkValid = !!artworkValue
  
  return titleValid && customerValid && artworkValid && !creating.value
})

onMounted(async () => {
  console.log('[CreateArtworkTaskDialog] Component mounted with preset artwork:', props.presetArtwork)
  console.log('[CreateArtworkTaskDialog] Spaces data available:', spaces.data?.length || 0, 'spaces')
  
  // Ensure spaces are loaded
  if (!spaces.data?.length) {
    await spaces.fetch()
    console.log('[CreateArtworkTaskDialog] Spaces loaded:', spaces.data?.length || 0, 'spaces')
  }
  
  // Initialize form with preset artwork if provided
  if (props.presetArtwork) {
    console.log('[CreateArtworkTaskDialog] Initializing form with preset artwork')
    form.customer = props.presetArtwork.customer
    
    // Load artworks for the customer
    try {
      console.log('[CreateArtworkTaskDialog] Loading artworks for customer:', props.presetArtwork.customer)
      const customerArtworks = await artworkApi.getCustomerArtworks(props.presetArtwork.customer)
      console.log('[CreateArtworkTaskDialog] Received artworks:', customerArtworks)
      artworks.value = customerArtworks
      
      // Set the preset artwork
      form.artwork = props.presetArtwork.name
      
      console.log('[CreateArtworkTaskDialog] Form initialized:', {
        customer: form.customer,
        artwork: form.artwork,
        availableArtworks: artworks.value
      })
    } catch (err) {
      console.error('[CreateArtworkTaskDialog] Error loading preset artwork:', err)
      console.error('[CreateArtworkTaskDialog] Error details:', {
        message: err.message,
        stack: err.stack,
        response: err.response
      })
    }
  } else {
    // If no preset artwork, still initialize with first available customer
    console.log('[CreateArtworkTaskDialog] No preset artwork, checking if we should auto-select customer')
    if (spaces.data && spaces.data.length > 0) {
      form.customer = spaces.data[0].name
      console.log('[CreateArtworkTaskDialog] Auto-selected first customer:', form.customer)
      // Load artworks for the first customer
      await loadArtworksForCustomer(form.customer)
    }
  }
})

// Watch for customer changes to load artworks
watch(() => form.customer, async (newCustomer, oldCustomer) => {
  console.log('[CreateArtworkTaskDialog] Customer changed from', oldCustomer, 'to', newCustomer)
  if (newCustomer !== oldCustomer) {
    const customerValue = typeof newCustomer === 'object' ? newCustomer.value : newCustomer
    if (customerValue) {
      await loadArtworksForCustomer(customerValue)
    } else {
      artworks.value = []
    }
  }
})

const loadArtworksForCustomer = async (customer) => {
  console.log('[CreateArtworkTaskDialog] loadArtworksForCustomer called with:', customer)
  if (!customer) {
    console.log('[CreateArtworkTaskDialog] No customer provided, clearing artworks')
    artworks.value = []
    return
  }
  
  try {
    console.log('[CreateArtworkTaskDialog] Calling artworkApi.getCustomerArtworks for:', customer)
    const customerArtworks = await artworkApi.getCustomerArtworks(customer)
    console.log('[CreateArtworkTaskDialog] Received artworks from API:', customerArtworks)
    artworks.value = customerArtworks || []
    console.log('[CreateArtworkTaskDialog] Updated artworks.value:', artworks.value)
  } catch (err) {
    console.error('[CreateArtworkTaskDialog] Error fetching artworks for customer', customer, ':', err)
    console.error('[CreateArtworkTaskDialog] Error details:', {
      message: err.message,
      stack: err.stack,
      response: err.response
    })
    artworks.value = []
  }
}

const onCustomerChange = async () => {
  console.log('[CreateArtworkTaskDialog] onCustomerChange triggered, current form.customer:', form.customer)
  
  // Reset artwork when customer changes
  form.artwork = ''
  artworks.value = []
  
  const customerValue = typeof form.customer === 'object' ? form.customer.value : form.customer
  console.log('[CreateArtworkTaskDialog] Extracted customer value:', customerValue)
  
  if (customerValue) {
    await loadArtworksForCustomer(customerValue)
  }
}

const validateForm = () => {
  let isValid = true
  
  // Reset errors
  errors.title = ''
  errors.customer = ''
  errors.artwork = ''
  
  if (!form.title.trim()) {
    errors.title = 'Title is required'
    isValid = false
  }
  
  const customerValue = typeof form.customer === 'object' ? form.customer.value : form.customer
  if (!customerValue) {
    errors.customer = 'Customer is required'
    isValid = false
  }
  
  const artworkValue = typeof form.artwork === 'object' ? form.artwork.value : form.artwork
  if (!artworkValue) {
    errors.artwork = 'Artwork is required'
    isValid = false
  }
  
  return isValid
}

const handleArtworkCreated = async (artwork) => {
  console.log('[CreateArtworkTaskDialog] Artwork created:', artwork)
  
  // Refresh artworks for the current customer
  const customerValue = typeof form.customer === 'object' ? form.customer.value : form.customer
  if (customerValue) {
    await loadArtworksForCustomer(customerValue)
  }
  
  // Auto-select the newly created artwork
  form.artwork = artwork.name
  
  // Close the dialog
  showCreateArtworkDialog.value = false
  
  console.log('[CreateArtworkTaskDialog] Auto-selected new artwork:', artwork.name)
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  creating.value = true
  
  try {
    // Extract the value from objects if they're objects, otherwise use as-is
    const artworkValue = typeof form.artwork === 'object' ? form.artwork.value : form.artwork
    const priorityValue = typeof form.priority === 'object' ? form.priority.value : form.priority
    
    const task = await artworkApi.createArtworkTask({
      title: form.title.trim(),
      artwork: artworkValue,
      description: form.description,
      priority: String(priorityValue),
      workflow_type: form.workflow_type
    })
    
    emit('created', task)
    
    // Reset form
    form.title = ''
    form.customer = ''
    form.artwork = ''
    form.priority = 'Medium'
    form.description = ''
    form.due_date = ''
    artworks.value = []
    
    // Reset errors
    errors.title = ''
    errors.customer = ''
    errors.artwork = ''
  } catch (err) {
    console.error('Error creating task:', err)
    alert('Failed to create task: ' + (err.message || 'Unknown error'))
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.form-group {
  @apply space-y-1;
}

.form-group label {
  @apply font-medium text-ink-gray-8 text-sm;
}

.form-group input,
.form-group select,
.form-group textarea {
  @apply transition-all duration-200 ease-in-out;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  @apply ring-2 ring-blue-500 ring-opacity-20 border-blue-500;
}

/* Override any potential width constraints from parent components */
.form-group :deep(.frappe-control) {
  width: 100% !important;
  min-width: 0 !important;
}

.form-group :deep(input),
.form-group :deep(select),
.form-group :deep(.autocomplete) {
  width: 100% !important;
  box-sizing: border-box !important;
}

/* Ensure the dialog container doesn't constrain the form */
:deep(.dialog-container) {
  min-width: 600px !important;
  max-width: 800px !important;
}

/* TextEditor styling */
.form-group :deep(.text-editor) {
  border: none !important;
}

.form-group :deep(.text-editor .editor-content) {
  padding: 12px !important;
  min-height: 80px !important;
}

/* Ensure proper button alignment */
.form-group button {
  display: flex !important;
  width: 100% !important;
  align-items: center !important;
  justify-content: center !important;
  box-sizing: border-box !important;
}
</style>
