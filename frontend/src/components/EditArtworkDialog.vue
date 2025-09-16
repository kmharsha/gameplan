<template>
  <div class="p-6 max-w-lg mx-auto">
    <div v-if="!props.artwork" class="text-center text-ink-gray-6">
      <h2 class="text-lg font-semibold text-ink-gray-9 mb-2">No Artwork Selected</h2>
      <p class="text-sm">Please select an artwork to edit.</p>
    </div>
    
    <div v-else>
      <div class="mb-6">
        <h2 class="text-lg font-semibold text-ink-gray-9">Edit Artwork</h2>
        <p class="text-sm text-ink-gray-6 mt-1">Update artwork details</p>
      </div>
      
      <div class="space-y-5">
        <!-- Customer Display (Read-only) -->
        <div class="form-group">
          <label class="block text-sm font-medium text-ink-gray-8 mb-2">Customer</label>
          <div class="px-3 py-2 bg-surface-gray-1 rounded-md text-ink-gray-7 border border-outline-gray-2">
            {{ customerTitle }}
          </div>
        </div>

        <!-- Artwork Title -->
        <div class="form-group">
          <label class="block text-sm font-medium text-ink-gray-8 mb-2">Artwork Title <span class="text-red-500">*</span></label>
          <FormControl
            type="text"
            v-model="form.title"
            placeholder="Enter artwork title"
            :validation="validation"
            class="w-full"
          />
        </div>

        <!-- Description -->
        <div class="form-group">
          <label class="block text-sm font-medium text-ink-gray-8 mb-2">Description</label>
          <FormControl
            type="textarea"
            v-model="form.description"
            placeholder="Brief description of the artwork project"
            :validation="validation"
            class="w-full"
            :rows="3"
          />
        </div>

        <!-- Priority and Due Date Row -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Priority -->
          <div class="form-group">
            <label class="block text-sm font-medium text-ink-gray-8 mb-2">Priority</label>
            <Autocomplete
              v-model="form.priority"
              :options="priorityOptions"
              placeholder="Select priority"
              class="w-full"
            />
          </div>

          <!-- Due Date -->
          <div class="form-group">
            <label class="block text-sm font-medium text-ink-gray-8 mb-2">Due Date (Optional)</label>
            <FormControl
              type="date"
              v-model="form.due_date"
              class="w-full"
            />
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-3 mt-6 pt-4 border-t border-outline-gray-2">
        <Button
          @click="$emit('cancel')"
          class="px-4 py-2 bg-surface-white border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1 rounded-md font-medium"
        >
          Cancel
        </Button>
        <Button
          @click="updateArtwork"
          :loading="loading"
          :disabled="!isValid"
          class="px-6 py-2 bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-md font-medium"
        >
          Update Artwork
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Button, FormControl, Autocomplete } from 'frappe-ui'
import { spaces } from '@/data/spaces'
import { artworkApi } from '@/utils/api'

const props = defineProps<{
  artwork?: {
    name: string
    title: string
    description: string
    priority: string
    customer: string
    customer_title?: string
    due_date?: string
  } | null
}>()

const emit = defineEmits(['updated', 'cancel'])

const loading = ref(false)
const form = reactive({
  title: '',
  description: '',
  priority: 'Medium',
  due_date: ''
})

const validation = reactive({})

const priorityOptions = [
  { label: 'Low', value: 'Low' },
  { label: 'Medium', value: 'Medium' },
  { label: 'High', value: 'High' },
  { label: 'Urgent', value: 'Urgent' }
]

const customerTitle = computed(() => {
  return props.artwork?.customer_title || props.artwork?.customer || 'Unknown Customer'
})

const isValid = computed(() => {
  return form.title.trim()
})

onMounted(() => {
  // Initialize form with artwork data
  if (props.artwork) {
    form.title = props.artwork.title || ''
    form.description = props.artwork.description || ''
    form.priority = props.artwork.priority || 'Medium'
    form.due_date = props.artwork.due_date || ''
    
    console.log('[EditArtworkDialog] Initialized with artwork:', props.artwork)
    console.log('[EditArtworkDialog] Form initialized with:', form)
  }
})

const updateArtwork = async () => {
  console.log('[EditArtworkDialog] Update artwork clicked')
  console.log('[EditArtworkDialog] Form validation:', isValid.value)
  console.log('[EditArtworkDialog] Form data:', form)
  
  if (!isValid.value) {
    console.log('[EditArtworkDialog] Form validation failed, not proceeding')
    return
  }

  loading.value = true
  try {
    const payload = {
      artwork_name: props.artwork.name,
      title: form.title.trim(),
      description: form.description.trim(),
      priority: form.priority,
      due_date: form.due_date || null
    }
    
    console.log('[EditArtworkDialog] Calling API with payload:', payload)
    
    // Extract priority value if it's an object (from Autocomplete)
    const priorityValue = typeof form.priority === 'object' ? form.priority.value : form.priority
    
    const artwork = await artworkApi.updateArtwork(props.artwork.name, {
      title: form.title.trim(),
      description: form.description.trim(),
      priority: String(priorityValue),
      due_date: form.due_date || null
    })
    
    console.log('[EditArtworkDialog] API response:', artwork)
    
    emit('updated', artwork)
    
    console.log('[EditArtworkDialog] Artwork updated successfully')
    
  } catch (error) {
    console.error('[EditArtworkDialog] Error updating artwork:', error)
    console.error('[EditArtworkDialog] Error details:', {
      message: error.message,
      stack: error.stack,
      response: error.response
    })
    // Show user-friendly error message
    alert('Failed to update artwork: ' + (error.message || 'Unknown error'))
  } finally {
    loading.value = false
    console.log('[EditArtworkDialog] Loading state set to false')
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

/* Ensure form controls take full width */
.form-group :deep(.frappe-control) {
  width: 100% !important;
  min-width: 0 !important;
}

.form-group :deep(input),
.form-group :deep(select),
.form-group :deep(textarea),
.form-group :deep(.autocomplete) {
  width: 100% !important;
  box-sizing: border-box !important;
}

/* Dialog container constraints */
:deep(.dialog-container) {
  min-width: 500px !important;
  max-width: 600px !important;
}

/* Customer display field styling */
.form-group div[class*="bg-surface-gray-1"] {
  @apply transition-colors duration-200;
}
</style>
