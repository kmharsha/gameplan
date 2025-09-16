<template>
  <router-link
    class="relative rounded-md flex flex-col focus:outline-none focus-visible:ring-outline-gray-3 focus-visible:ring-2 justify-between border p-3 hover:bg-surface-gray-2 group transition-colors"
    :to="{
      name: 'Space',
      params: {
        spaceId: space.name,
      },
    }"
  >
    <div class="flex items-start w-full space-x-2">
      <div class="inline-flex">
        <span class="text-lg mr-1.5 font-[emoji] leading-5">
          {{ space.icon }}
        </span>
        <span class="text-base leading-5 text-ink-gray-9 font-medium line-clamp-1">
          {{ space.title }}
          <LucideLock v-if="space.is_private" class="h-3 w-3 text-ink-gray-6 inline ml-1 mb-0.5" />
        </span>
      </div>
      <div class="!ml-auto flex">
        <Badge v-if="getSpaceUnreadCount(space.name) > 0" class="group-hover:bg-surface-white">
          {{ getSpaceUnreadCount(space.name) }}
        </Badge>
      </div>
    </div>
    <div class="mt-1.5 flex items-end justify-between">
      <div class="text-ink-gray-5 text-sm" v-if="space.discussions_count ?? 0 > 0">
        {{ space.discussions_count }}
        {{ space.discussions_count == 1 ? 'post' : 'posts' }}
      </div>

      <div class="flex absolute bottom-2 right-2 items-center space-x-1" @click.prevent>
        <template v-if="!space.archived_at">
          <Button
            v-if="hasJoined(space.name)"
            :tooltip="'Leave space'"
            variant="ghost"
            class="group-hover:opacity-100 sm:opacity-0 transition-opacity opacity-100 focus:opacity-100"
            @click="leaveSpace(space)"
            :loading="isDocMethodLoading(space.name, 'leave')"
          >
            <template #icon>
              <LucideUserRoundMinus class="size-4" />
            </template>
          </Button>
          <Button
            :tooltip="'Join space'"
            v-else
            size="sm"
            variant="ghost"
            class="group-hover:opacity-100 sm:opacity-0 transition-opacity opacity-100 focus:opacity-100"
            @click="joinSpace(space)"
            :loading="isDocMethodLoading(space.name, 'join')"
          >
            <template #icon>
              <LucideUserRoundPlus class="h-4 w-4" />
            </template>
          </Button>
          <div
            class="group-hover:opacity-100 sm:opacity-0 transition-opacity opacity-100 has-[[data-state=open]]:opacity-100 focus-within:opacity-100"
          >
            <SpaceOptions placement="right" :spaceId="space.name" />
          </div>
        </template>
        <template v-else>
          <Tooltip :text="'Unarchive space'">
            <Button
              size="sm"
              @click="unarchiveSpace(space)"
              variant="ghost"
              class="group-hover:opacity-100 sm:opacity-0 transition-opacity opacity-100"
            >
              <template #icon>
                <LucideArchiveRestore class="size-4" />
              </template>
            </Button>
          </Tooltip>
        </template>
      </div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import { Badge, Button, Tooltip } from 'frappe-ui'
import {
  hasJoined,
  getSpaceUnreadCount,
  Space,
  joinSpace,
  leaveSpace,
  unarchiveSpace,
  isDocMethodLoading,
} from '@/data/spaces'
import SpaceOptions from '@/components/SpaceOptions.vue'

interface Props {
  space: Space
}

defineProps<Props>()
</script>
