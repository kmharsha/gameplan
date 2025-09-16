<template>
  <PageHeader>
    <Breadcrumbs class="h-7" :items="[{ label: 'Spaces', route: { name: 'Spaces' } }]" />
    <Button
      @click="
        () => {
          categoryForNewSpace = ''
          newSpaceDialog = true
        }
      "
    >
      <template #prefix><LucidePlus class="h-4 w-4" /></template>
      Add new
    </Button>
  </PageHeader>
  <NewSpaceDialog v-model="newSpaceDialog" :category="categoryForNewSpace" />
  <div class="mx-auto max-w-4xl px-2 sm:px-5">
    <div class="mt-6 mb-3 flex px-2.5 items-center justify-between gap-2.5">
      <TextInput
        v-model="query"
        placeholder="Search"
        class="w-full"
        v-focus="!!!$route.query.teamId"
      >
        <template #prefix>
          <LucideSearch class="size-4 text-ink-gray-5" />
        </template>
      </TextInput>
      <TabButtons
        :buttons="[{ label: 'Public' }, { label: 'Private' }, { label: 'Archived' }]"
        v-model="currentTab"
      />
    </div>
    <div class="p-3" v-if="groupedSpaces.length === 0">
      <EmptyStateBox>
        <div class="text-ink-gray-5 text-base">No spaces</div>
      </EmptyStateBox>
    </div>
    <RecycleScroller
      ref="scroller"
      key-field="name"
      :items="groupedSpaces"
      size-field="height"
      @scroll-end="onScrollEnd"
    >
      <template #default="{ item }">
        <SpaceCardGroup
          :ref="(el) => setGroupRefs(el as HTMLElement, item.name)"
          :group="item"
          @new-space="
            (categoryName) => {
              categoryForNewSpace = categoryName
              newSpaceDialog = true
            }
          "
        />
      </template>
    </RecycleScroller>
  </div>
</template>
<script setup lang="ts">
import { ref, nextTick, computed } from 'vue'
import { RecycleScroller } from 'vue-virtual-scroller'
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'
import { useRoute } from 'vue-router'
import { Breadcrumbs, TabButtons, Button } from 'frappe-ui'
import { useWindowSize } from '@vueuse/core'
import NewSpaceDialog from '@/components/NewSpaceDialog.vue'
import PageHeader from '@/components/PageHeader.vue'
import EmptyStateBox from '@/components/EmptyStateBox.vue'
import SpaceCardGroup from './SpaceCardGroup.vue'
import { useGroupedSpaces } from '@/data/groupedSpaces'
import { vFocus } from '@/directives'
import { scrollTo } from '@/utils/scrollContainer'

const currentTab = ref('Public')
const categoryForNewSpace = ref('')
const query = ref('')
const route = useRoute()
const scroller = ref(null)

const groupedSpaces = computed(() => {
  let _groupedSpaces = useGroupedSpaces({
    filterFn: (space) =>
      Boolean(
        {
          Public: !space.archived_at,
          Private: space.is_private,
          Archived: space.archived_at,
        }[currentTab.value],
      ) && (query.value ? space.title.toLowerCase().includes(query.value.toLowerCase()) : true),
  })

  let out = []

  let categoryHeight = 44
  let cardHeight = 66.95
  let gap = 12
  let gapBetweenGroups = 48

  for (const group of _groupedSpaces.value) {
    let rows = Math.ceil(group.spaces.length / columns.value)
    let gapHeight = (rows - 1) * gap
    let groupHeight = categoryHeight + gapHeight + rows * cardHeight + gapBetweenGroups
    out.push({
      ...group,
      height: groupHeight,
    })
  }
  return out
})

const newSpaceDialog = ref(false)
const groupRefs = ref<Record<string, HTMLElement>>({})

async function onScrollEnd() {
  if (route.query.teamId) {
    await nextTick()
    setTimeout(() => {
      scrollToCategory(route.query.teamId as string)
    }, 100)
  }
}

function scrollToCategory(categoryId: string) {
  let groupIndex = groupedSpaces.value.findIndex((group) => group.name === categoryId)
  let heightUntilGroup = 0
  for (let i = 0; i < groupIndex; i++) {
    heightUntilGroup += groupedSpaces.value[i].height
  }
  const scrollPosition = heightUntilGroup
  const searchHeight = 64
  scrollTo({ top: scrollPosition + searchHeight })
}

function setGroupRefs(el: HTMLElement, name: string) {
  groupRefs.value[name] = el
}

const columns = computed(() => {
  const { width } = useWindowSize()
  if (width.value < 768) return 1
  if (width.value < 1024) return 2
  if (width.value < 1280) return 3
  return 4
})
</script>
