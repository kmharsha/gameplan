<template>
  <div class="mail-compose-container">
    <!-- Floating Chat Icon -->
    <button
      v-if="!isOpen"
      @click="openCompose"
      class="fixed bottom-6 right-6 z-50 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center group"
    >
      <LucideMail class="w-6 h-6" />
      <span class="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
        ✉
      </span>
    </button>

    <!-- Mail Compose Modal -->
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click="closeCompose"
    >
      <div
        class="bg-white rounded-lg shadow-2xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-hidden"
        @click.stop
      >
        <!-- Header -->
        <div class="bg-blue-600 text-white px-6 py-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <LucideMail class="w-5 h-5" />
            <h3 class="text-lg font-semibold">Compose Email</h3>
          </div>
          <button
            @click="closeCompose"
            class="text-white hover:text-gray-200 transition-colors"
          >
            <LucideX class="w-5 h-5" />
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="sendEmail" class="p-6 space-y-4">
          <!-- To Field -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              To <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.to"
              type="email"
              required
              multiple
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="recipient@example.com"
            />
          </div>

          <!-- CC Field -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              CC
            </label>
            <input
              v-model="form.cc"
              type="email"
              multiple
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="cc@example.com"
            />
          </div>

          <!-- BCC Field -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              BCC
            </label>
            <input
              v-model="form.bcc"
              type="email"
              multiple
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="bcc@example.com"
            />
          </div>

          <!-- Subject Field -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Subject <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.subject"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Email subject"
            />
          </div>

          <!-- Message Body -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Message <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="form.message"
              required
              rows="8"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="Type your message here..."
            ></textarea>
          </div>

          <!-- Attachments -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Attachments
            </label>
            <div class="border-2 border-dashed border-gray-300 rounded-md p-4 text-center">
              <input
                ref="fileInput"
                type="file"
                multiple
                @change="handleFileUpload"
                class="hidden"
                accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif"
              />
              <button
                type="button"
                @click="$refs.fileInput.click()"
                class="text-blue-600 hover:text-blue-700 font-medium"
              >
                <LucidePaperclip class="w-4 h-4 inline mr-2" />
                Choose files or drag and drop
              </button>
              <p class="text-sm text-gray-500 mt-2">
                PDF, DOC, DOCX, TXT, JPG, PNG, GIF up to 10MB
              </p>
            </div>
            
            <!-- Selected Files -->
            <div v-if="attachments.length > 0" class="mt-3 space-y-2">
              <div
                v-for="(file, index) in attachments"
                :key="index"
                class="flex items-center justify-between bg-gray-50 px-3 py-2 rounded-md"
              >
                <div class="flex items-center gap-2">
                  <LucideFile class="w-4 h-4 text-gray-500" />
                  <span class="text-sm text-gray-700">{{ file.name }}</span>
                  <span class="text-xs text-gray-500">({{ formatFileSize(file.size) }})</span>
                </div>
                <button
                  type="button"
                  @click="removeAttachment(index)"
                  class="text-red-500 hover:text-red-700"
                >
                  <LucideX class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              @click="closeCompose"
              class="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              @click="saveDraft"
              :disabled="sending"
              class="px-4 py-2 bg-gray-500 text-white hover:bg-gray-600 disabled:opacity-50 rounded-md font-medium transition-colors"
            >
              Save Draft
            </button>
            <button
              type="submit"
              :disabled="sending || !isFormValid"
              class="px-6 py-2 bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-md font-medium transition-colors flex items-center gap-2"
            >
              <LucideLoader2 v-if="sending" class="w-4 h-4 animate-spin" />
              <LucideSend v-else class="w-4 h-4" />
              {{ sending ? 'Sending...' : 'Send' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { createResource } from 'frappe-ui'
import LucideMail from '~icons/lucide/mail'
import LucideX from '~icons/lucide/x'
import LucidePaperclip from '~icons/lucide/paperclip'
import LucideFile from '~icons/lucide/file'
import LucideLoader2 from '~icons/lucide/loader-2'
import LucideSend from '~icons/lucide/send'

// Reactive data
const isOpen = ref(false)
const sending = ref(false)
const attachments = ref([])

// Form data
const form = ref({
  to: '',
  cc: '',
  bcc: '',
  subject: '',
  message: ''
})

// Computed
const isFormValid = computed(() => {
  return form.value.to.trim() !== '' && 
         form.value.subject.trim() !== '' && 
         form.value.message.trim() !== '' &&
         !sending.value
})

// Methods
const openCompose = () => {
  isOpen.value = true
  // Focus on the first input when opened
  setTimeout(() => {
    const firstInput = document.querySelector('input[type="email"]')
    if (firstInput) firstInput.focus()
  }, 100)
}

const closeCompose = () => {
  isOpen.value = false
  resetForm()
}

const resetForm = () => {
  form.value = {
    to: '',
    cc: '',
    bcc: '',
    subject: '',
    message: ''
  }
  attachments.value = []
  sending.value = false
}

const handleFileUpload = (event) => {
  const files = Array.from(event.target.files)
  files.forEach(file => {
    if (file.size <= 10 * 1024 * 1024) { // 10MB limit
      attachments.value.push(file)
    } else {
      alert(`File ${file.name} is too large. Maximum size is 10MB.`)
    }
  })
  // Reset file input
  event.target.value = ''
}

const removeAttachment = (index) => {
  attachments.value.splice(index, 1)
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const saveDraft = async () => {
  // TODO: Implement save draft functionality
  console.log('Saving draft...', form.value)
}

const sendEmail = async () => {
  if (!isFormValid.value) return
  
  sending.value = true
  
  try {
    // Create FormData for file uploads
    const formData = new FormData()
    formData.append('to', form.value.to)
    formData.append('cc', form.value.cc)
    formData.append('bcc', form.value.bcc)
    formData.append('subject', form.value.subject)
    formData.append('message', form.value.message)
    
    // Add attachments
    attachments.value.forEach((file, index) => {
      formData.append(`attachment_${index}`, file)
    })
    
    // Call backend API
    const response = await fetch('/api/method/gameplan.api.send_email', {
      method: 'POST',
      body: formData,
      headers: {
        'X-Frappe-CSRF-Token': frappe.csrf_token
      }
    })
    
    if (response.ok) {
      const result = await response.json()
      if (result.message) {
        // Show success message
        frappe.show_alert({
          message: 'Email sent successfully!',
          indicator: 'green'
        })
        closeCompose()
      } else {
        throw new Error(result.exc || 'Failed to send email')
      }
    } else {
      throw new Error('Failed to send email')
    }
  } catch (error) {
    console.error('Error sending email:', error)
    frappe.show_alert({
      message: 'Failed to send email. Please try again.',
      indicator: 'red'
    })
  } finally {
    sending.value = false
  }
}

// Keyboard shortcuts
const handleKeydown = (event) => {
  if (event.ctrlKey && event.key === 'Enter' && isOpen.value) {
    sendEmail()
  } else if (event.key === 'Escape' && isOpen.value) {
    closeCompose()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.mail-compose-container {
  font-family: 'Inter', sans-serif;
}

.form-group {
  margin-bottom: 1rem;
}

/* Custom scrollbar for textarea */
textarea::-webkit-scrollbar {
  width: 6px;
}

textarea::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

textarea::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

textarea::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Animation for modal */
.fixed.inset-0 {
  animation: fadeIn 0.2s ease-out;
}

.bg-white.rounded-lg {
  animation: slideUp 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
