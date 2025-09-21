<template>
  <div class="flex flex-col h-full bg-vibrant-purple bg-pattern-dots">
    <!-- Loading State -->
    <div v-if="loading && !taskDetails" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <LucideLoader2 class="size-8 animate-spin mx-auto mb-4 text-ink-gray-6" />
        <p class="text-ink-gray-6">Loading task details...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <LucideAlertCircle class="size-8 mx-auto mb-4 text-red-500" />
        <p class="text-red-500 font-medium">Error loading task</p>
        <p class="text-ink-gray-6 text-sm mt-2">{{ error }}</p>
        <Button @click="refresh" class="mt-4">Try Again</Button>
      </div>
    </div>

    <!-- Task Content -->
    <div v-else-if="taskDetails" class="flex-1 overflow-hidden">
      <div class="h-full flex">
        <!-- Main Content -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <!-- Header -->
          <div class="px-6 py-4 border-b border-outline-gray-2 bg-white/70 backdrop-blur-sm shadow-lg">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <Button @click="$router.back()" class="p-1 !bg-blue-600 !text-white hover:!bg-blue-700 border border-outline-gray-2">
                    <LucideArrowLeft class="size-4" />
                  </Button>
                  <h1 class="text-xl font-semibold text-ink-gray-9">{{ task.title }}</h1>
                </div>
                <div class="flex items-center gap-4 text-sm text-ink-gray-6">
                  <span class="flex items-center gap-1">
                    <LucideHash class="size-3" />
                    {{ task.name }}
                  </span>
                  <span class="flex items-center gap-1">
                    <LucideCalendar class="size-3" />
                    {{ formatDate(task.modified) }}
                  </span>
                  <span class="flex items-center gap-1">
                    <LucideUser class="size-3" />
                    {{ getUserName(task.created_by_sales) }}
                  </span>
                </div>
              </div>
              
              <!-- Status Badge -->
              <div 
                :class="[
                  'px-3 py-1 rounded-full text-sm font-medium',
                  STATUS_COLORS[task.status],
                  STATUS_TEXT_COLORS[task.status]
                ]"
              >
                {{ task.status }}
              </div>
            </div>
          </div>

          <!-- Task Details and Discussion -->
          <div class="flex-1 overflow-hidden flex">
            <!-- Left Panel - Task Info -->
            <div class="w-1/3 border-r border-outline-gray-2/50 overflow-y-auto bg-white/50 backdrop-blur-sm">
              <div class="p-6 space-y-6">
                <!-- Task Information -->
                <div>
                  <h3 class="font-medium text-ink-gray-9 mb-3">Task Information</h3>
                  <div class="space-y-3">
                    <div class="flex justify-between">
                      <span class="text-ink-gray-6">Customer:</span>
                      <span class="text-ink-gray-9 font-medium">{{ task.customer_title || task.customer }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-ink-gray-6">Artwork:</span>
                      <span class="text-ink-gray-9 font-medium">{{ task.artwork_title || task.artwork }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-ink-gray-6">Priority:</span>
                      <span 
                        :class="[
                          'px-2 py-1 text-xs rounded-full',
                          PRIORITY_COLORS[task.priority],
                          getPriorityTextColor(task.priority)
                        ]"
                      >
                        {{ task.priority }}
                      </span>
                    </div>
                    <div v-if="task.assigned_to" class="flex justify-between">
                      <span class="text-ink-gray-6">Assigned to:</span>
                      <span class="text-ink-gray-9">{{ getUserName(task.assigned_to) }}</span>
                    </div>
                  </div>
                </div>

                <!-- Related Tasks -->
                <div v-if="relatedTasks?.procurement_task || relatedTasks?.sales_task">
                  <h3 class="font-medium text-ink-gray-9 mb-3">Related Tasks</h3>
                  <div class="space-y-3">
                    <!-- Show Sales Task if this is Procurement -->
                    <div v-if="relatedTasks?.sales_task && task.workflow_type === 'Procurement Cycle'" 
                         class="p-3 bg-green-50 border border-green-200 rounded-lg">
                      <div class="flex items-center justify-between mb-2">
                        <div class="flex items-center gap-2">
                          <LucideArrowRight class="size-4 text-green-700" />
                          <span class="text-sm font-medium text-green-800">Sales Cycle Task</span>
                        </div>
                        <span 
                          :class="[
                            'px-2 py-1 text-xs rounded-full',
                            STATUS_COLORS[relatedTasks.sales_task.status],
                            STATUS_TEXT_COLORS[relatedTasks.sales_task.status]
                          ]"
                        >
                          {{ relatedTasks.sales_task.status }}
                        </span>
                      </div>
                      <p class="text-sm text-green-700 mb-2">{{ relatedTasks.sales_task.title }}</p>
                      <Button
                        @click="$router.push({ name: 'ArtworkTask', params: { taskId: relatedTasks.sales_task.name } })"
                        class="text-xs bg-green-100 text-green-800 border border-green-300 hover:bg-green-200"
                      >
                        View Sales Task
                      </Button>
                    </div>
                    
                    <!-- Show Procurement Task if this is Sales -->
                    <div v-if="relatedTasks?.procurement_task && task.workflow_type === 'Sales Cycle'" 
                         class="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                      <div class="flex items-center justify-between mb-2">
                        <div class="flex items-center gap-2">
                          <LucidePackage class="size-4 text-purple-700" />
                          <span class="text-sm font-medium text-purple-800">Procurement Cycle Task</span>
                        </div>
                        <span 
                          :class="[
                            'px-2 py-1 text-xs rounded-full',
                            STATUS_COLORS[relatedTasks.procurement_task.status],
                            STATUS_TEXT_COLORS[relatedTasks.procurement_task.status]
                          ]"
                        >
                          {{ relatedTasks.procurement_task.status }}
                        </span>
                      </div>
                      <p class="text-sm text-purple-700 mb-2">{{ relatedTasks.procurement_task.title }}</p>
                      <Button
                        @click="$router.push({ name: 'ArtworkTask', params: { taskId: relatedTasks.procurement_task.name } })"
                        class="text-xs bg-purple-100 text-purple-800 border border-purple-300 hover:bg-purple-200"
                      >
                        View Procurement Task
                      </Button>
                    </div>
                    
                    <!-- Show creation status for Sales tasks -->
                    <div v-if="task.workflow_type === 'Sales Cycle' && task.status === 'Completed' && !relatedTasks?.procurement_task" 
                         class="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <div class="flex items-center gap-2 mb-2">
                        <LucideInfo class="size-4 text-blue-700" />
                        <span class="text-sm font-medium text-blue-800">Automatic Procurement Creation</span>
                      </div>
                      <p class="text-xs text-blue-700">A procurement task will be automatically created when this task is marked as completed.</p>
                    </div>
                  </div>
                </div>

                <!-- Description -->
                <div v-if="task.description">
                  <h3 class="font-medium text-ink-gray-9 mb-3">Description</h3>
                  <div class="prose prose-sm" v-html="task.description"></div>
                </div>

                <!-- Status Actions -->
                <div v-if="allowedTransitions?.length">
                  <h3 class="font-medium text-ink-gray-9 mb-3">Actions</h3>
                  <div class="space-y-2">
                    <Button
                      v-for="status in allowedTransitions"
                      :key="status"
                      @click="handleStatusChange(status)"
                      class="w-full justify-start bg-surface-white border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1"
                    >
                      Move to {{ status }}
                    </Button>
                  </div>
                </div>

                <!-- Attachments -->
                <div>
                  <div class="flex items-center justify-between mb-3">
                    <h3 class="font-medium text-ink-gray-9">Attachments</h3>
                    <Button 
                      @click="showAttachmentDialog = true"
                      class="p-1 !bg-blue-600 !text-white hover:!bg-blue-700 border border-outline-gray-2"
                    >
                      <LucidePlus class="size-4" />
                    </Button>
                  </div>
                  <div class="space-y-2">
                    <div 
                      v-for="attachment in sortedAttachments"
                      :key="attachment.name"
                      class="flex items-center gap-3 p-2 bg-surface-gray-1 rounded"
                    >
                      <LucideFile class="size-4 text-ink-gray-6" />
                      <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-ink-gray-9 truncate">
                          {{ attachment.file_name }}
                        </p>
                        <p class="text-xs text-ink-gray-6">
                          v{{ attachment.version }} • {{ attachment.file_size }}
                        </p>
                      </div>
                      <div class="flex items-center gap-1">
                        <Button 
                          v-if="isPreviewableFile(attachment.file_name)"
                          @click="previewAttachment(attachment)"
                          class="p-1 bg-gradient-to-r from-blue-500 to-blue-700 text-white hover:from-blue-600 hover:to-blue-800 border border-blue-500 shadow-md hover:shadow-lg transition-all duration-200"
                        >
                          <LucideEye class="size-3" />
                        </Button>
                        <Button 
                          @click="downloadAttachment(attachment)"
                          class="p-1 bg-gradient-to-r from-red-500 to-red-700 text-white hover:from-red-600 hover:to-red-800 border border-red-500 shadow-md hover:shadow-lg transition-all duration-200"
                        >
                          <LucideDownload class="size-3" />
                        </Button>
                      </div>
                    </div>
                    <div v-if="!task.attachments?.length" class="text-center py-4 text-ink-gray-5">
                      No attachments yet
                    </div>
                  </div>
                </div>

                <!-- Status History -->
                <div>
                  <h3 class="font-medium text-ink-gray-9 mb-3">Status History</h3>
                  <div class="space-y-2">
                    <div 
                      v-for="history in task.status_history"
                      :key="history.name"
                      class="flex items-start gap-2 text-xs"
                    >
                      <div class="w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
                      <div>
                        <p class="font-medium text-ink-gray-9">
                          {{ history.from_status || 'Created' }} → {{ history.to_status }}
                        </p>
                        <p class="text-ink-gray-6">
                          {{ getUserName(history.changed_by) }} • {{ formatDate(history.change_date) }}
                        </p>
                        <p v-if="history.reason" class="text-ink-gray-7 mt-1">{{ history.reason }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Right Panel - Discussion -->
            <div class="flex-1 flex flex-col bg-white/30 backdrop-blur-sm">
              <!-- Discussion Header -->
              <div class="px-6 py-4 border-b border-outline-gray-2/50 bg-white/50 backdrop-blur-sm">
                <h3 class="font-medium text-ink-gray-9">Discussion</h3>
              </div>

              <!-- Comments Area -->
              <div class="flex-1 overflow-y-auto p-6">
                <div class="space-y-4">
                  <div 
                    v-for="comment in comments"
                    :key="comment.name"
                    class="flex gap-3"
                  >
                    <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <LucideUser class="size-4 text-blue-600" />
                    </div>
                    <div class="flex-1">
                      <div class="flex items-center gap-2 mb-1">
                        <span class="font-medium text-ink-gray-9">{{ getUserName(comment.owner) }}</span>
                        <span class="text-xs text-ink-gray-6">{{ formatDate(comment.creation) }}</span>
                      </div>
                      <div class="prose prose-sm" v-html="comment.content"></div>
                      
                      <!-- Comment Attachments -->
                      <div v-if="comment.attachments && comment.attachments.length > 0" class="mt-3">
                        <h5 class="text-xs font-medium text-ink-gray-7 mb-2">Attachments:</h5>
                        <div class="space-y-1">
                          <div 
                            v-for="(attachment, index) in comment.attachments"
                            :key="index"
                            class="flex items-center gap-2 p-2 bg-surface-gray-1 rounded border text-xs"
                          >
                            <LucideFile class="size-3 text-ink-gray-6" />
                            <a 
                              :href="attachment.file_url"
                              target="_blank"
                              class="flex-1 text-blue-600 hover:underline truncate"
                            >
                              {{ attachment.file_name }}
                            </a>
                            <span class="text-ink-gray-5">{{ formatFileSize(attachment.file_size) }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div v-if="!comments?.length" class="text-center py-8 text-ink-gray-5">
                    No comments yet. Start the discussion!
                  </div>
                </div>
              </div>

              <!-- Comment Editor -->
              <div class="border-t border-outline-gray-2 p-6">
                <div class="space-y-3">
                  <TextEditor
                    ref="textEditor"
                    :content="commentContent"
                    placeholder="Add a comment..."
                    :min-height="80"
                    :max-height="200"
                    class="border border-outline-gray-2 rounded-lg"
                    :editor-class="'prose prose-sm max-w-none'"
                    :editable="true"
                    :bubble-menu="true"
                    @change="handleCommentContentUpdate"
                  >
                    <template #editor="{ editor }">
                      <EditorContent
                        class="max-h-[200px] overflow-y-auto p-3"
                        :editor="editor"
                      />
                    </template>
                    <template #bottom>
                      <div class="px-3 py-2 border-t border-outline-gray-2 bg-surface-gray-1">
                        <TextEditorFixedMenu
                          class="-ml-1 overflow-x-auto"
                          :buttons="textEditorMenuButtons"
                        />
                      </div>
                    </template>
                  </TextEditor>
                  
                  <!-- Comment Attachments -->
                  <div v-if="commentAttachments.length > 0" class="mt-3">
                    <h4 class="text-sm font-medium text-ink-gray-9 mb-2">Attachments:</h4>
                    <div class="space-y-2">
                      <div 
                        v-for="(attachment, index) in commentAttachments"
                        :key="index"
                        class="flex items-center gap-2 p-2 bg-surface-gray-1 rounded border"
                      >
                        <LucideFile class="size-4 text-ink-gray-6" />
                        <span class="flex-1 text-sm text-ink-gray-9 truncate">{{ attachment.file_name }}</span>
                        <span class="text-xs text-ink-gray-6">{{ formatFileSize(attachment.file_size) }}</span>
                        <Button 
                          @click="removeCommentAttachment(index)"
                          class="p-1 bg-transparent hover:bg-surface-gray-2"
                        >
                          <LucideX class="size-3 text-ink-gray-6" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div class="flex items-center justify-between gap-2 mt-3">
                    <div class="flex items-center gap-2">
                      <button
                        @click="showFileUploader = true"
                        class="bg-blue-600 text-white hover:bg-blue-700 border border-blue-600 px-2 py-1.5 rounded text-sm font-medium inline-flex items-center gap-1.5 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                      >
                        <LucidePaperclip class="size-3.5" />
                        Attach File
                      </button>
                      <span v-if="commentAttachments.length > 0" class="text-xs text-ink-gray-6">
                        {{ commentAttachments.length }} file{{ commentAttachments.length !== 1 ? 's' : '' }} attached
                      </span>
                    </div>
                    <div class="flex gap-2">
                      <Button
                        @click="handleDiscardComment"
                        class="bg-surface-white border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1"
                      >
                        Discard
                      </Button>
                      <Button
                        @click="handleAddComment"
                        :loading="addingComment"
                        :disabled="isSubmitDisabled"
                        class="!bg-blue-600 !text-white hover:!bg-blue-700 disabled:opacity-50"
                      >
                        Submit
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Fallback when task is loading but we want to show comment editor -->
    <div v-else class="flex-1 overflow-hidden">
      <div class="h-full flex">
        <div class="flex-1 flex flex-col">
          <div class="px-6 py-4 border-b border-outline-gray-2">
            <h3 class="font-medium text-ink-gray-9">Discussion</h3>
          </div>
          
          <div class="flex-1 overflow-y-auto p-6">
            <div class="text-center py-8 text-ink-gray-5">
              {{ loading ? 'Loading comments...' : 'No comments yet. Start the discussion!' }}
            </div>
          </div>
          
          <!-- Comment Editor -->
          <div class="border-t border-outline-gray-2 p-6">
            <div class="space-y-3">
              <TextEditor
                ref="fallbackTextEditor"
                :content="commentContent"
                placeholder="Add a comment..."
                :min-height="80"
                :max-height="200"
                class="border border-outline-gray-2 rounded-lg"
                :editor-class="'prose prose-sm max-w-none'"
                :editable="true"
                :bubble-menu="true"
                @change="handleCommentContentUpdate"
              >
                <template #editor="{ editor }">
                  <EditorContent
                    class="max-h-[200px] overflow-y-auto p-3"
                    :editor="editor"
                  />
                </template>
                <template #bottom>
                  <div class="px-3 py-2 border-t border-outline-gray-2 bg-surface-gray-1">
                    <TextEditorFixedMenu
                      class="-ml-1 overflow-x-auto"
                      :buttons="textEditorMenuButtons"
                    />
                  </div>
                </template>
              </TextEditor>
              
              <!-- Comment Attachments (Fallback) -->
              <div v-if="commentAttachments.length > 0" class="mt-3">
                <h4 class="text-sm font-medium text-ink-gray-9 mb-2">Attachments:</h4>
                <div class="space-y-2">
                  <div 
                    v-for="(attachment, index) in commentAttachments"
                    :key="index"
                    class="flex items-center gap-2 p-2 bg-surface-gray-1 rounded border"
                  >
                    <LucideFile class="size-4 text-ink-gray-6" />
                    <span class="flex-1 text-sm text-ink-gray-9 truncate">{{ attachment.file_name }}</span>
                    <span class="text-xs text-ink-gray-6">{{ formatFileSize(attachment.file_size) }}</span>
                    <Button 
                      @click="removeCommentAttachment(index)"
                      class="p-1 bg-transparent hover:bg-surface-gray-2"
                    >
                      <LucideX class="size-3 text-ink-gray-6" />
                    </Button>
                  </div>
                </div>
              </div>

              <div class="flex items-center justify-between gap-2 mt-3">
                <div class="flex items-center gap-2">
                  <button
                    @click="showFileUploader = true"
                    class="bg-blue-600 text-white hover:bg-blue-700 border border-blue-600 px-2 py-1.5 rounded text-sm font-medium inline-flex items-center gap-1.5 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    <LucidePaperclip class="size-3.5" />
                    Attach File
                  </button>
                  <span v-if="commentAttachments.length > 0" class="text-xs text-ink-gray-6">
                    {{ commentAttachments.length }} file{{ commentAttachments.length !== 1 ? 's' : '' }} attached
                  </span>
                </div>
                <div class="flex gap-2">
                  <Button
                    @click="handleDiscardComment"
                    class="bg-surface-white border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1"
                  >
                    Discard
                  </Button>
                  <Button
                    @click="handleAddComment"
                    :loading="addingComment"
                    :disabled="isSubmitDisabled"
                    class="!bg-blue-600 !text-white hover:!bg-blue-700 disabled:opacity-50"
                  >
                    Submit
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Status Change Dialog -->
    <Dialog v-model="showStatusDialog">
      <template #body>
        <StatusChangeDialog 
          v-if="selectedNewStatus && taskDetails"
          :task="task"
          :new-status="selectedNewStatus"
          @confirmed="handleStatusChangeConfirmed"
          @cancel="showStatusDialog = false"
        />
      </template>
    </Dialog>

    <!-- Add Attachment Dialog -->
    <Dialog v-model="showAttachmentDialog">
      <template #body>
        <AddAttachmentDialog
          :attached-to-doctype="'GP Artwork Task'"
          :attached-to-name="taskId"
          :existing-attachments="taskDetails?.task?.attachments || []"
          @uploaded="handleAttachmentUploaded"
          @cancel="showAttachmentDialog = false"
        />
      </template>
    </Dialog>

    <!-- File Uploader Dialog -->
    <Dialog v-model="showFileUploader">
      <template #body>
        <div class="p-6">
          <h3 class="text-lg font-medium text-ink-gray-9 mb-4">Attach File to Comment</h3>
          <FileUploader
            :attach="false"
            @success="handleCommentFileUploaded"
            @error="handleFileUploadError"
            :allowed-file-types="[
              '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
              '.txt', '.csv', '.zip', '.rar', '.jpg', '.jpeg', '.png', '.gif',
              '.mp4', '.mov', '.avi', '.mp3', '.wav'
            ]"
            :max-file-size="50"
          >
            <template #default="{ openFileSelector, uploading, progress }">
              <div class="border-2 border-dashed border-outline-gray-2 rounded-lg p-8 text-center">
                <LucideFile class="size-12 text-ink-gray-5 mx-auto mb-4" />
                <p class="text-sm text-ink-gray-7 mb-4">
                  Drop files here or 
                  <button @click="openFileSelector" class="text-blue-600 hover:underline">
                    browse to upload
                  </button>
                </p>
                <p class="text-xs text-ink-gray-5">
                  Supports: PDF, DOC, XLS, PPT, Images, Videos, and more (max 50MB)
                </p>
                <div v-if="uploading" class="mt-4">
                  <div class="w-full bg-surface-gray-2 rounded-full h-2">
                    <div 
                      class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      :style="{ width: `${progress}%` }"
                    ></div>
                  </div>
                  <p class="text-sm text-ink-gray-6 mt-2">Uploading... {{ progress }}%</p>
                </div>
              </div>
            </template>
          </FileUploader>
          <div class="flex justify-end gap-2 mt-6">
            <Button
              @click="showFileUploader = false"
              class="bg-surface-white border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1"
            >
              Cancel
            </Button>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, Dialog } from 'frappe-ui'
import { formatDistanceToNow } from 'date-fns'
import { useArtworkTask, STATUS_COLORS, STATUS_TEXT_COLORS, PRIORITY_COLORS } from '@/data/artworkTasks'
import { apiCall } from '@/utils/api'
import StatusChangeDialog from '@/components/StatusChangeDialog.vue'
import AddAttachmentDialog from '@/components/AddAttachmentDialog.vue'
import TextEditor from '@/components/TextEditor.vue'
import { EditorContent } from '@tiptap/vue-3'
import { TextEditorFixedMenu } from 'frappe-ui/src/components/TextEditor'
import { FileUploader } from 'frappe-ui'

// Import Lucide icons
import LucideLoader2 from '~icons/lucide/loader-2'
import LucideAlertCircle from '~icons/lucide/alert-circle'
import LucideArrowLeft from '~icons/lucide/arrow-left'
import LucideHash from '~icons/lucide/hash'
import LucideCalendar from '~icons/lucide/calendar'
import LucideUser from '~icons/lucide/user'
import LucidePlus from '~icons/lucide/plus'
import LucideFile from '~icons/lucide/file'
import LucideDownload from '~icons/lucide/download'
import LucidePaperclip from '~icons/lucide/paperclip'
import LucideEye from '~icons/lucide/eye'
import LucideX from '~icons/lucide/x'
import LucideArrowRight from '~icons/lucide/arrow-right'
import LucidePackage from '~icons/lucide/package'
import LucideInfo from '~icons/lucide/info'

const route = useRoute()
const router = useRouter()

const taskId = computed(() => route.params.taskId as string)
const { taskDetails, loading, error, fetchTaskDetails, updateStatus, addComment } = useArtworkTask(taskId.value)

const showStatusDialog = ref(false)
const showAttachmentDialog = ref(false)
const selectedNewStatus = ref('')
const addingComment = ref(false)
const commentContent = ref('')
const commentAttachments = ref([])
const showFileUploader = ref(false)

const task = computed(() => {
  console.log('[ArtworkTask] Task computed:', taskDetails.value?.task)
  return taskDetails.value?.task
})
const comments = computed(() => {
  console.log('[ArtworkTask] Comments computed:', taskDetails.value?.comments)
  return taskDetails.value?.comments || []
})
const allowedTransitions = computed(() => {
  console.log('[ArtworkTask] Allowed transitions:', taskDetails.value?.allowed_transitions)
  console.log('[ArtworkTask] Task workflow type:', taskDetails.value?.task?.workflow_type)
  console.log('[ArtworkTask] Task status:', taskDetails.value?.task?.status)
  return taskDetails.value?.allowed_transitions || []
})
const relatedTasks = computed(() => {
  console.log('[ArtworkTask] Related tasks:', taskDetails.value?.related_tasks)
  return taskDetails.value?.related_tasks || {}
})

// Sort attachments by upload date (newest first)
const sortedAttachments = computed(() => {
  if (!task.value?.attachments) return []
  
  return [...task.value.attachments].sort((a, b) => {
    // Sort by upload_date if available, otherwise by creation order
    const dateA = a.upload_date || a.creation || new Date(0)
    const dateB = b.upload_date || b.creation || new Date(0)
    
    // Sort in descending order (newest first)
    return new Date(dateB).getTime() - new Date(dateA).getTime()
  })
})

// Enhanced submit button logic
const isSubmitDisabled = computed(() => {
  const content = commentContent.value
  // Remove HTML tags and check if there's actual text content
  const textContent = content ? content.replace(/<[^>]*>/g, '').trim() : ''
  const isEmpty = !textContent || textContent === '' || content === '<p></p>' || content === '<p><br></p>'
  console.log('[ArtworkTask] isSubmitDisabled - content:', JSON.stringify(content), 'textContent:', JSON.stringify(textContent), 'isEmpty:', isEmpty)
  return isEmpty || addingComment.value
})

// Text editor buttons configuration
const textEditorMenuButtons = [
  'Paragraph',
  ['Heading 3', 'Heading 4', 'Heading 5'],
  'Separator',
  'Bold',
  'Italic',
  'Underline',
  'Separator',
  'Bullet List',
  'Numbered List',
  'Separator',
  'Align Left',
  'Align Center',
  'Align Right',
  'FontColor',
  'Separator',
  'Image',
  'Video',
  'Link',
  'Blockquote',
  'Code',
  'Horizontal Rule'
]

onMounted(() => {
  console.log('[ArtworkTask] Component mounted, taskId:', taskId.value)
  fetchTaskDetails()
})

watch(() => route.params.taskId, (newTaskId) => {
  if (newTaskId) {
    fetchTaskDetails()
  }
})

const refresh = () => {
  fetchTaskDetails()
}

const formatDate = (dateString: string) => {
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true })
  } catch {
    return dateString
  }
}

const getUserName = (userId: string) => {
  return userId?.includes('@') ? userId.split('@')[0] : userId
}

const getPriorityTextColor = (priority: string) => {
  const colorMap = {
    'Low': 'text-ink-gray-7',
    'Medium': 'text-blue-700',
    'High': 'text-orange-700',
    'Urgent': 'text-red-700'
  }
  return colorMap[priority] || 'text-ink-gray-7'
}

const handleStatusChange = (newStatus: string) => {
  selectedNewStatus.value = newStatus
  showStatusDialog.value = true
}

const handleStatusChangeConfirmed = async (reason: string, comments: string) => {
  try {
    await updateStatus(selectedNewStatus.value, reason, comments)
    showStatusDialog.value = false
    selectedNewStatus.value = ''
  } catch (error) {
    console.error('Failed to update status:', error)
  }
}

const handleCommentContentUpdate = (value: string) => {
  console.log('[ArtworkTask] Comment content updated:', value)
  commentContent.value = value
}

const handleDiscardComment = () => {
  console.log('[ArtworkTask] Discarding comment')
  commentContent.value = ''
  commentAttachments.value = []
}

const handleAddComment = async () => {
  console.log('[ArtworkTask] handleAddComment called')
  console.log('[ArtworkTask] commentContent.value:', JSON.stringify(commentContent.value))
  
  const content = commentContent.value
  const textContent = content ? content.replace(/<[^>]*>/g, '').trim() : ''
  console.log('[ArtworkTask] HTML content:', JSON.stringify(content))
  console.log('[ArtworkTask] text content:', JSON.stringify(textContent))
  
  if (!textContent) {
    console.log('[ArtworkTask] No text content, returning early')
    return
  }
  
  addingComment.value = true
  try {
    // Prepare comment data with attachments
    let commentData = {
      content: content,
      attachments: commentAttachments.value
    }
    
    console.log('[ArtworkTask] Adding comment with data:', commentData)
    
    // Send both content and attachments to the API
    const result = await addComment(content, JSON.stringify(commentAttachments.value))
    console.log('[ArtworkTask] API result:', result)
    
    // Clear the editor and attachments after successful submission
    commentContent.value = ''
    commentAttachments.value = []
    console.log('[ArtworkTask] Comment added successfully, cleared editor and attachments')
  } catch (error) {
    console.error('[ArtworkTask] Failed to add comment:', error)
    alert('Failed to add comment: ' + (error.message || 'Unknown error'))
  } finally {
    addingComment.value = false
  }
}

const handleAttachmentUploaded = async (fileInfo: any) => {
  console.log('[ArtworkTask] Attachment uploaded:', fileInfo)
  
  try {
    // Save the attachment to the task using the backend API
    await apiCall('gameplan.api.add_artwork_task_attachment', {
      task_name: taskId.value,
      file_url: fileInfo.file_url,
      file_name: fileInfo.file_name,
      version: fileInfo.version || '1.0',
      description: fileInfo.description || '',
      file_size: fileInfo.file_size
    })
    
    console.log('[ArtworkTask] Attachment saved to task')
    showAttachmentDialog.value = false
    refresh()
  } catch (error) {
    console.error('[ArtworkTask] Error saving attachment:', error)
    alert('Failed to save attachment: ' + (error.message || 'Unknown error'))
  }
}

const downloadAttachment = (attachment: any) => {
  // Create a download link
  const link = document.createElement('a')
  link.href = attachment.file_url
  link.download = attachment.file_name
  link.click()
}

const isPreviewableFile = (fileName: string): boolean => {
  const previewableExtensions = [
    // Image files
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
    // Document files
    '.pdf', '.txt', '.md', '.rtf',
    // Office files
    '.xlsx', '.xls', '.docx', '.doc', '.pptx', '.ppt',
    // Other previewable files
    '.csv', '.json', '.xml', '.html', '.htm'
  ]
  const extension = fileName.toLowerCase().substring(fileName.lastIndexOf('.'))
  return previewableExtensions.includes(extension)
}

const previewAttachment = (attachment: any) => {
  // Open the file in a new tab for preview
  window.open(attachment.file_url, '_blank')
}

// Comment file handling functions
const handleCommentFileUploaded = (fileInfo: any) => {
  console.log('[ArtworkTask] Comment file uploaded:', fileInfo)
  
  const attachment = {
    file_url: fileInfo.file_url,
    file_name: fileInfo.file_name || fileInfo.name,
    file_size: fileInfo.file_size || fileInfo.size
  }
  
  commentAttachments.value.push(attachment)
  showFileUploader.value = false
  
  console.log('[ArtworkTask] Added attachment to comment:', attachment)
}

const handleFileUploadError = (error: any) => {
  console.error('[ArtworkTask] File upload error:', error)
  alert('Failed to upload file: ' + (error.message || 'Unknown error'))
}

const removeCommentAttachment = (index: number) => {
  console.log('[ArtworkTask] Removing attachment at index:', index)
  commentAttachments.value.splice(index, 1)
}

const formatFileSize = (bytes: number | string): string => {
  if (!bytes) return 'Unknown size'
  
  const size = typeof bytes === 'string' ? parseInt(bytes) : bytes
  if (isNaN(size)) return 'Unknown size'
  
  const units = ['B', 'KB', 'MB', 'GB']
  let unitIndex = 0
  let fileSize = size
  
  while (fileSize >= 1024 && unitIndex < units.length - 1) {
    fileSize /= 1024
    unitIndex++
  }
  
  return `${fileSize.toFixed(1)} ${units[unitIndex]}`
}
</script>
