<template>
  <div class="p-8 space-y-8">
    <h1 class="text-2xl font-bold text-ink-gray-9">Icon Visibility Test</h1>
    
    <!-- Test different button styles -->
    <div class="space-y-4">
      <h2 class="text-lg font-semibold text-ink-gray-8">Button Icon Tests</h2>
      
      <div class="flex flex-wrap gap-4">
        <!-- Blue background buttons (should have white icons) -->
        <Button class="bg-blue-600 text-white hover:bg-blue-700 inline-flex items-center">
          <PlusIcon size="md" variant="white" class="mr-2" />
          Blue Button
        </Button>
        
        <!-- Light blue background buttons (should have blue icons) -->
        <Button class="bg-blue-50 border border-blue-200 text-blue-600 hover:bg-blue-100 inline-flex items-center">
          <PlusIcon size="sm" variant="blue" class="mr-1" />
          Light Blue Button
        </Button>
        
        <!-- Gray/surface buttons (should inherit text color) -->
        <Button class="bg-surface-white border border-outline-gray-2 text-ink-gray-7 hover:bg-surface-gray-1 inline-flex items-center">
          <PlusIcon size="md" variant="default" class="mr-2" />
          Gray Button
        </Button>
      </div>
    </div>
    
    <!-- Test different icon sizes -->
    <div class="space-y-4">
      <h2 class="text-lg font-semibold text-ink-gray-8">Icon Size Tests</h2>
      
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2">
          <PlusIcon size="sm" variant="default" />
          <span>Small (12px)</span>
        </div>
        <div class="flex items-center gap-2">
          <PlusIcon size="md" variant="default" />
          <span>Medium (16px)</span>
        </div>
        <div class="flex items-center gap-2">
          <PlusIcon size="lg" variant="default" />
          <span>Large (20px)</span>
        </div>
      </div>
    </div>
    
    <!-- Test different background contexts -->
    <div class="space-y-4">
      <h2 class="text-lg font-semibold text-ink-gray-8">Background Context Tests</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Light background -->
        <div class="bg-white p-4 border border-outline-gray-2 rounded-lg">
          <h3 class="font-medium text-ink-gray-9 mb-2">Light Background</h3>
          <div class="flex items-center gap-2">
            <PlusIcon size="md" variant="default" />
            <span class="text-ink-gray-7">Default Icon</span>
          </div>
        </div>
        
        <!-- Dark background -->
        <div class="bg-gray-800 p-4 rounded-lg">
          <h3 class="font-medium text-white mb-2">Dark Background</h3>
          <div class="flex items-center gap-2">
            <PlusIcon size="md" variant="white" />
            <span class="text-white">White Icon</span>
          </div>
        </div>
        
        <!-- Blue background -->
        <div class="bg-blue-600 p-4 rounded-lg">
          <h3 class="font-medium text-white mb-2">Blue Background</h3>
          <div class="flex items-center gap-2">
            <PlusIcon size="md" variant="white" />
            <span class="text-white">White Icon</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Test comparison with original Lucide -->
    <div class="space-y-4">
      <h2 class="text-lg font-semibold text-ink-gray-8">Comparison Test</h2>
      
      <div class="flex items-center gap-8">
        <div class="flex items-center gap-2">
          <LucidePlus class="size-4 stroke-current" />
          <span>Original Lucide Plus</span>
        </div>
        <div class="flex items-center gap-2">
          <PlusIcon size="md" variant="default" />
          <span>Custom Plus Icon</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Button } from 'frappe-ui'
import PlusIcon from '@/components/icons/PlusIcon.vue'
import LucidePlus from '~icons/lucide/plus'
</script>
