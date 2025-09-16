<template>
  <div class="p-6 max-w-md">
    <h2 class="text-lg font-semibold text-ink-gray-9 mb-4">Add Attachment</h2>
    
    <form @submit.prevent="handleSubmit">
      <!-- File Upload Area -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-ink-gray-7 mb-2">
          File <span class="text-red-500">*</span>
        </label>
        <div 
          class="border-2 border-dashed border-outline-gray-2 rounded-lg p-6 text-center"
          :class="{ 'border-blue-400 bg-blue-50': isDragOver }"
          @drop="handleDrop"
          @dragover="handleDragOver"
          @dragenter="handleDragEnter"
          @dragleave="handleDragLeave"
        >
          <div v-if="!selectedFile">
            <LucideUpload class="size-8 mx-auto mb-2 text-ink-gray-6" />
            <p class="text-ink-gray-7 mb-2">Drag and drop a file here, or click to select</p>
            <input
              ref="fileInput"
              type="file"
              @change="handleFileSelect"
              class="hidden"
              accept=".jpg,.jpeg,.png,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.rar"
            />
            <Button 
              type="button"
              @click="$refs.fileInput?.click()"
              class="bg-surface-white border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1"
            >
              Choose File
            </Button>
          </div>
          <div v-else class="flex items-center gap-3">
            <LucideFile class="size-6 text-blue-600" />
            <div class="flex-1 text-left">
              <p class="font-medium text-ink-gray-9">{{ selectedFile.name }}</p>
              <p class="text-sm text-ink-gray-6">{{ formatFileSize(selectedFile.size) }}</p>
            </div>
            <Button 
              type="button"
              @click="clearFile"
              class="p-1 bg-surface-white border border-outline-gray-2 text-red-600 hover:bg-red-50"
            >
              <LucideX class="size-4" />
            </Button>
          </div>
        </div>
      </div>
      
      <!-- Version -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-ink-gray-7 mb-2">
          Version
        </label>
        <TextInput
          v-model="form.version"
          placeholder="e.g. 1.0, 2.1"
        />
      </div>
      
      <!-- Description -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-ink-gray-7 mb-2">
          Description
        </label>
        <textarea
          v-model="form.description"
          placeholder="Add a description for this file..."
          class="w-full px-3 py-2 border border-outline-gray-2 rounded-lg resize-none"
          rows="3"
        ></textarea>
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
          :loading="uploading"
          :disabled="!selectedFile"
          class="bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          Upload
        </Button>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive } from 'vue'
import { TextInput, Button } from 'frappe-ui'
import LucideUpload from '~icons/lucide/upload'
import LucideFile from '~icons/lucide/file'
import LucideX from '~icons/lucide/x'

export default defineComponent({
  name: 'AddAttachmentDialog',
  components: {
    TextInput,
    Button,
    LucideUpload,
    LucideFile,
    LucideX
  },
  props: {
    attachedToDoctype: {
      type: String,
      default: 'GP Artwork Task'
    },
    attachedToName: {
      type: String,
      default: ''
    }
  },
  emits: ['uploaded', 'cancel'],
  setup(props, { emit }) {

const selectedFile = ref<File | null>(null)
const isDragOver = ref(false)
const uploading = ref(false)
const fileInput = ref<HTMLInputElement>()

const form = reactive({
  version: '1.0',
  description: ''
})

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = true
}

const handleDragEnter = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  if (!e.relatedTarget || !(e.currentTarget as HTMLElement).contains(e.relatedTarget as Node)) {
    isDragOver.value = false
  }
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = false
  
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    selectedFile.value = files[0]
  }
}

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
  }
}

const clearFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const handleSubmit = async () => {
  if (!selectedFile.value) return
  
  uploading.value = true
  
  try {
    console.log('[AddAttachmentDialog] Starting file upload:', selectedFile.value.name)
    
    // Upload file using Frappe's file upload
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('is_private', '0')
    formData.append('folder', 'Home/Attachments')
    formData.append('doctype', props.attachedToDoctype)
    if (props.attachedToName) {
      formData.append('docname', props.attachedToName)
    }
    
    const response = await fetch('/api/method/upload_file', {
      method: 'POST',
      body: formData,
      headers: {
        'X-Frappe-CSRF-Token': window.csrf_token || ''
      }
    })
    
    console.log('[AddAttachmentDialog] Upload response status:', response.status)
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('[AddAttachmentDialog] Upload error response:', errorText)
      throw new Error(`Upload failed: ${response.status} ${errorText}`)
    }
    
    const result = await response.json()
    console.log('[AddAttachmentDialog] Upload result:', result)
    
    if (result.message) {
      const fileInfo = {
        file_url: result.message.file_url,
        file_name: selectedFile.value.name,
        version: form.version,
        description: form.description,
        file_size: formatFileSize(selectedFile.value.size)
      }
      
      console.log('[AddAttachmentDialog] Emitting uploaded event with:', fileInfo)
      emit('uploaded', fileInfo)
      
      // Reset form
      clearFile()
      form.version = '1.0'
      form.description = ''
    } else {
      throw new Error('No file information in response')
    }
  } catch (error) {
    console.error('[AddAttachmentDialog] Upload error:', error)
    alert(`Failed to upload file: ${error.message}`)
  } finally {
    uploading.value = false
  }
}

return {
  selectedFile,
  isDragOver,
  uploading,
  fileInput,
  form,
  handleDragOver,
  handleDragEnter,
  handleDragLeave,
  handleDrop,
  handleFileSelect,
  clearFile,
  formatFileSize,
  handleSubmit
}
  }
})
</script>
