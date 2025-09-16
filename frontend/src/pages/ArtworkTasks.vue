<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-4 border-b border-outline-gray-2">
      <div class="flex items-center gap-3">
        <LucidePalette class="size-5" />
        <h1 class="text-xl font-semibold text-ink-gray-9">Artwork Tasks</h1>
      </div>
      <div class="flex items-center gap-3">
        <Button @click="$router.push({ name: 'ArtworkKanban' })" class="bg-surface-white border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1">
          <template #prefix>
            <LucideKanbanSquare class="size-4" />
          </template>
          Kanban View
        </Button>
        <Button @click="showCreateDialog = true" class="bg-blue-600 text-white hover:bg-blue-700">
          <template #prefix>
            <LucidePlus class="size-4" />
          </template>
          New Task
        </Button>
      </div>
    </div>

    <!-- Task List -->
    <div class="flex-1 overflow-hidden">
      <div class="h-full overflow-auto p-6 artwork-tasks-scroll">
        <div class="grid gap-4">
          <div 
            v-for="task in artworkTasks.data"
            :key="task.name"
            class="bg-surface-white border border-outline-gray-2 rounded-lg p-4 hover:shadow-sm cursor-pointer"
            @click="$router.push({ name: 'ArtworkTask', params: { taskId: task.name } })"
          >
            <div class="flex items-start justify-between mb-3">
              <h3 class="font-semibold text-ink-gray-9">{{ task.title }}</h3>
              <span 
                :class="[
                  'px-2 py-1 text-xs font-medium rounded-full',
                  STATUS_COLORS[task.status],
                  STATUS_TEXT_COLORS[task.status]
                ]"
              >
                {{ task.status }}
              </span>
            </div>
            
            <div class="flex items-center gap-4 text-sm text-ink-gray-6">
              <span>{{ task.project }}</span>
              <span>{{ task.priority }}</span>
              <span>{{ formatDate(task.modified) }}</span>
            </div>
          </div>
        </div>
        
        <!-- Loading state -->
        <div v-if="artworkTasks.loading" class="flex items-center justify-center py-8">
          <LucideLoader2 class="size-6 animate-spin text-ink-gray-6" />
        </div>
        
        <!-- Empty state -->
        <div v-if="!artworkTasks.loading && !artworkTasks.data?.length" class="text-center py-12">
          <LucidePalette class="size-12 mx-auto mb-4 text-ink-gray-4" />
          <h3 class="text-lg font-medium text-ink-gray-7 mb-2">No artwork tasks yet</h3>
          <p class="text-ink-gray-6 mb-4">Get started by creating your first artwork task.</p>
          <Button @click="showCreateDialog = true" class="bg-blue-600 text-white hover:bg-blue-700">
            Create Task
          </Button>
        </div>
      </div>
    </div>

    <!-- Create Task Dialog -->
    <Dialog v-model="showCreateDialog">
      <template #body>
        <CreateArtworkTaskDialog 
          @created="handleTaskCreated" 
          @cancel="showCreateDialog = false" 
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Dialog } from 'frappe-ui'
import { formatDistanceToNow } from 'date-fns'
import { artworkTasks, STATUS_COLORS, STATUS_TEXT_COLORS } from '@/data/artworkTasks'
import CreateArtworkTaskDialog from '@/components/CreateArtworkTaskDialog.vue'

const router = useRouter()
const showCreateDialog = ref(false)

onMounted(() => {
  artworkTasks.reload()
})

const formatDate = (dateString: string) => {
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true })
  } catch {
    return dateString
  }
}

const handleTaskCreated = () => {
  showCreateDialog.value = false
  artworkTasks.reload()
}
</script>

<style scoped>
/* Custom scrollbar styling for ArtworkTasks page */
.artwork-tasks-scroll {
  /* Webkit browsers (Chrome, Safari, Edge) */
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
}

.artwork-tasks-scroll::-webkit-scrollbar {
  width: 8px;
}

.artwork-tasks-scroll::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.artwork-tasks-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
  border: 1px solid #f1f5f9;
}

.artwork-tasks-scroll::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.artwork-tasks-scroll::-webkit-scrollbar-thumb:active {
  background: #64748b;
}

/* Firefox scrollbar styling */
.artwork-tasks-scroll {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
}

/* Ensure smooth scrolling */
.artwork-tasks-scroll {
  scroll-behavior: smooth;
}
</style>
