<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-4 border-b border-outline-gray-2">
      <div class="flex items-center gap-3">
        <LucideCheckCircle class="size-5" />
        <h1 class="text-xl font-semibold text-ink-gray-9">Approved Artwork Tasks</h1>
      </div>
      <div class="flex items-center gap-3">
        <Button @click="exportTasks" class="bg-surface-white border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1">
          <template #prefix>
            <LucideDownload class="size-4" />
          </template>
          Export
        </Button>
        <Button @click="refresh" :loading="loading" class="bg-surface-white border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1">
          <template #prefix>
            <LucideRefreshCw class="size-4" />
          </template>
          Refresh
        </Button>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="px-6 py-4 border-b border-outline-gray-2">
      <div class="flex items-center gap-4">
        <div class="flex-1">
          <TextInput
            v-model="searchTerm"
            placeholder="Search approved tasks by title..."
            @input="debouncedSearch"
          >
            <template #prefix>
              <LucideSearch class="size-4" />
            </template>
          </TextInput>
        </div>
        <Select
          v-model="selectedFilter"
          :options="filterOptions"
          @change="handleFilterChange"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !approvedTasks.length" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <LucideLoader2 class="size-8 animate-spin mx-auto mb-4 text-ink-gray-6" />
        <p class="text-ink-gray-6">Loading approved tasks...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <LucideAlertCircle class="size-8 mx-auto mb-4 text-red-500" />
        <p class="text-red-500 font-medium">Error loading tasks</p>
        <p class="text-ink-gray-6 text-sm mt-2">{{ error }}</p>
        <Button @click="refresh" class="mt-4">Try Again</Button>
      </div>
    </div>

    <!-- Tasks Table -->
    <div v-else class="flex-1 overflow-hidden">
      <div class="h-full overflow-auto approved-tasks-scroll">
        <table class="w-full">
          <thead class="bg-surface-gray-1 sticky top-0">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-ink-gray-7 uppercase tracking-wider">
                Task
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-ink-gray-7 uppercase tracking-wider">
                Project
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-ink-gray-7 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-ink-gray-7 uppercase tracking-wider">
                Quality Approval
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-ink-gray-7 uppercase tracking-wider">
                Final Approval
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-ink-gray-7 uppercase tracking-wider">
                Attachments
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-ink-gray-7 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-surface-white divide-y divide-outline-gray-2">
            <tr 
              v-for="task in filteredTasks"
              :key="task.name"
              class="hover:bg-surface-gray-1 cursor-pointer"
              @click="goToTask(task.name)"
            >
              <td class="px-6 py-4">
                <div>
                  <div class="font-medium text-ink-gray-9">{{ task.title }}</div>
                  <div class="text-sm text-ink-gray-6"># {{ task.name }}</div>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-ink-gray-9">{{ getProjectName(task.project) }}</div>
                <div class="text-xs text-ink-gray-6">{{ task.team }}</div>
              </td>
              <td class="px-6 py-4">
                <span 
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded-full',
                    STATUS_COLORS[task.status],
                    STATUS_TEXT_COLORS[task.status]
                  ]"
                >
                  {{ task.status }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div v-if="task.approved_by_quality_at" class="text-sm">
                  <div class="text-ink-gray-9">{{ getUserName(task.approved_by_quality_by) }}</div>
                  <div class="text-xs text-ink-gray-6">{{ formatDate(task.approved_by_quality_at) }}</div>
                </div>
                <div v-else class="text-sm text-ink-gray-5">-</div>
              </td>
              <td class="px-6 py-4">
                <div v-if="task.final_approved_at" class="text-sm">
                  <div class="text-ink-gray-9">{{ getUserName(task.final_approved_by) }}</div>
                  <div class="text-xs text-ink-gray-6">{{ formatDate(task.final_approved_at) }}</div>
                </div>
                <div v-else class="text-sm text-ink-gray-5">-</div>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                  <LucideFile class="size-4 text-ink-gray-6" />
                  <span class="text-sm text-ink-gray-9">
                    {{ task.attachments?.length || 0 }} files
                  </span>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                  <Button 
                    @click.stop="goToTask(task.name)"
                    class="p-1 bg-surface-white border border-outline-gray-2"
                  >
                    <LucideEye class="size-3" />
                  </Button>
                  <Button 
                    v-if="task.attachments?.length"
                    @click.stop="downloadAllAttachments(task)"
                    class="p-1 bg-surface-white border border-outline-gray-2"
                  >
                    <LucideDownload class="size-3" />
                  </Button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-if="!filteredTasks.length && !loading" class="flex items-center justify-center h-64">
          <div class="text-center">
            <LucideFileSearch class="size-12 mx-auto mb-4 text-ink-gray-4" />
            <h3 class="text-lg font-medium text-ink-gray-7">No approved tasks found</h3>
            <p class="text-ink-gray-6 mt-2">
              {{ searchTerm ? 'Try adjusting your search criteria.' : 'No tasks have been approved yet.' }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { TextInput, Button, Select } from 'frappe-ui'
import { formatDistanceToNow } from 'date-fns'
import { debounce } from 'lodash-es'
import { useApprovedArtworkTasks, STATUS_COLORS, STATUS_TEXT_COLORS } from '@/data/artworkTasks'

const router = useRouter()
const { approvedTasks, loading, error, fetchApprovedTasks } = useApprovedArtworkTasks()

const searchTerm = ref('')
const selectedFilter = ref('all')

const filterOptions = [
  { label: 'All Approved', value: 'all' },
  { label: 'Quality Approved', value: 'quality' },
  { label: 'Final Approved', value: 'final' }
]

// Debounced search function
const debouncedSearch = debounce(() => {
  fetchApprovedTasks(searchTerm.value)
}, 300)

const filteredTasks = computed(() => {
  if (!approvedTasks.value) return []
  
  let tasks = [...approvedTasks.value]
  
  // Apply status filter
  if (selectedFilter.value === 'quality') {
    tasks = tasks.filter(task => task.status === 'Approved by Quality')
  } else if (selectedFilter.value === 'final') {
    tasks = tasks.filter(task => task.status === 'Final Approved')
  }
  
  return tasks
})

onMounted(() => {
  fetchApprovedTasks()
})

const refresh = () => {
  fetchApprovedTasks(searchTerm.value)
}

const handleFilterChange = () => {
  // Re-fetch with current search term when filter changes
  fetchApprovedTasks(searchTerm.value)
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

const getProjectName = (project: string) => {
  // This could be enhanced to fetch project names from a store
  return project?.length > 30 ? project.substring(0, 30) + '...' : project
}

const goToTask = (taskId: string) => {
  router.push({ name: 'ArtworkTask', params: { taskId } })
}

const downloadAllAttachments = async (task: any) => {
  if (!task.attachments?.length) return
  
  // Download each attachment
  for (const attachment of task.attachments) {
    const link = document.createElement('a')
    link.href = attachment.file_url
    link.download = attachment.file_name
    link.click()
    
    // Small delay between downloads to avoid browser blocking
    await new Promise(resolve => setTimeout(resolve, 100))
  }
}

const exportTasks = () => {
  // Create CSV export of approved tasks
  const csvData = []
  
  // Header
  csvData.push([
    'Task ID',
    'Title', 
    'Project',
    'Team',
    'Status',
    'Quality Approved By',
    'Quality Approved At',
    'Final Approved By', 
    'Final Approved At',
    'Attachments Count'
  ])
  
  // Data rows
  filteredTasks.value.forEach(task => {
    csvData.push([
      task.name,
      task.title,
      task.project,
      task.team,
      task.status,
      task.approved_by_quality_by || '-',
      task.approved_by_quality_at || '-',
      task.final_approved_by || '-',
      task.final_approved_at || '-',
      task.attachments?.length || 0
    ])
  })
  
  // Convert to CSV string
  const csvContent = csvData.map(row => 
    row.map(field => `"${field}"`).join(',')
  ).join('\n')
  
  // Create download link
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `approved-artwork-tasks-${new Date().toISOString().split('T')[0]}.csv`
  link.click()
  window.URL.revokeObjectURL(url)
}
</script>

<style scoped>
/* Custom scrollbar styling for ApprovedArtworkTasks page */
.approved-tasks-scroll {
  /* Webkit browsers (Chrome, Safari, Edge) */
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
}

.approved-tasks-scroll::-webkit-scrollbar {
  width: 8px;
}

.approved-tasks-scroll::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.approved-tasks-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
  border: 1px solid #f1f5f9;
}

.approved-tasks-scroll::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.approved-tasks-scroll::-webkit-scrollbar-thumb:active {
  background: #64748b;
}

/* Firefox scrollbar styling */
.approved-tasks-scroll {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
}

/* Ensure smooth scrolling */
.approved-tasks-scroll {
  scroll-behavior: smooth;
}
</style>
