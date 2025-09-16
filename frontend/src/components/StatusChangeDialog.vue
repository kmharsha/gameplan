<template>
  <div class="p-6 max-w-md">
    <h2 class="text-lg font-semibold text-ink-gray-9 mb-4">Change Status</h2>
    
    <div class="mb-4">
      <p class="text-ink-gray-7">
        Change status of <strong>{{ task.title }}</strong> from 
        <span class="font-medium">{{ task.status }}</span> to 
        <span class="font-medium">{{ newStatus }}</span>?
      </p>
    </div>
    
    <form @submit.prevent="handleSubmit">
      <!-- Reason -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-ink-gray-7 mb-2">
          Reason (Optional)
        </label>
        <TextInput
          v-model="form.reason"
          placeholder="Enter reason for status change"
        />
      </div>
      
      <!-- Comments -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-ink-gray-7 mb-2">
          Comments (Optional)
        </label>
        <TextEditor
          v-model="form.comments"
          placeholder="Add any additional comments..."
          :max-height="120"
        />
      </div>
      
      <!-- Status Change Info -->
      <div class="mb-6 p-3 bg-surface-gray-1 rounded-lg">
        <h4 class="font-medium text-ink-gray-8 mb-2">Status Change Details</h4>
        <div class="flex items-center gap-2 text-sm">
          <span 
            :class="[
              'px-2 py-1 rounded text-xs',
              STATUS_COLORS[task.status],
              STATUS_TEXT_COLORS[task.status]
            ]"
          >
            {{ task.status }}
          </span>
          <LucideArrowRight class="size-4 text-ink-gray-6" />
          <span 
            :class="[
              'px-2 py-1 rounded text-xs',
              STATUS_COLORS[newStatus],
              STATUS_TEXT_COLORS[newStatus]
            ]"
          >
            {{ newStatus }}
          </span>
        </div>
        <p class="text-xs text-ink-gray-6 mt-2">
          {{ getStatusChangeDescription() }}
        </p>
      </div>
      
      <!-- Actions -->
      <div class="flex items-center justify-end gap-3">
        <Button
          type="button"
          @click="$emit('cancel')"
          class="bg-surface-white border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1"
        >
          Cancel
        </Button>
        <Button
          type="submit"
          :loading="submitting"
          class="bg-blue-600 text-white hover:bg-blue-700"
        >
          Change Status
        </Button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { TextInput, TextEditor, Button } from 'frappe-ui'
import { STATUS_COLORS, STATUS_TEXT_COLORS } from '@/data/artworkTasks'
import LucideArrowRight from '~icons/lucide/arrow-right'

interface Task {
  name: string
  title: string
  status: string
}

interface Props {
  task: Task
  newStatus: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  confirmed: [reason: string, comments: string]
  cancel: []
}>()

const submitting = ref(false)

const form = reactive({
  reason: '',
  comments: ''
})

const getStatusChangeDescription = () => {
  const descriptions = {
    // Common statuses
    'Draft': 'Initial task state',
    'Approved': 'Task has been approved and is ready for next steps',
    'Completed': 'Task is fully complete',
    'Rework': 'Task needs changes and corrections',
    
    // Sales Cycle specific
    'Design': 'Task is in design phase',
    'Approval': 'Task is awaiting approval from stakeholders',
    
    // Procurement Cycle specific
    'Procurement Draft': 'Task is in draft stage for procurement review',
    'Procurement Review': 'Task is being reviewed by procurement team',
    'Procurement Rework': 'Task needs rework based on procurement feedback',
    'Final Approved': 'Task has been finally approved by procurement team'
  }
  
  return descriptions[props.newStatus] || 'Status change in progress'
}

const handleSubmit = async () => {
  submitting.value = true
  
  try {
    emit('confirmed', form.reason, form.comments)
  } finally {
    submitting.value = false
  }
}
</script>
