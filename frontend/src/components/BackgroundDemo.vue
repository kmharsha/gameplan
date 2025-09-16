<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-7xl mx-auto">
      <h1 class="text-3xl font-bold text-center mb-8 text-gray-900">Beautiful Background Themes</h1>
      
      <!-- Theme selector -->
      <div class="flex justify-center mb-8 gap-2 flex-wrap">
        <button 
          v-for="theme in themes" 
          :key="theme"
          @click="selectedTheme = theme"
          :class="[
            'px-4 py-2 rounded-lg font-medium capitalize transition-all',
            selectedTheme === theme 
              ? 'bg-blue-600 text-white shadow-lg' 
              : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
          ]"
        >
          {{ theme }}
        </button>
      </div>
      
      <!-- Variant selector -->
      <div class="flex justify-center mb-8 gap-2">
        <button 
          v-for="variant in variants" 
          :key="variant"
          @click="selectedVariant = variant"
          :class="[
            'px-3 py-1 rounded-md text-sm capitalize transition-all',
            selectedVariant === variant 
              ? 'bg-gray-800 text-white' 
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          ]"
        >
          {{ variant }}
        </button>
      </div>
      
      <!-- Preview card -->
      <div class="relative h-96 rounded-2xl overflow-hidden shadow-2xl">
        <BeautifulBackground :theme="selectedTheme" :variant="selectedVariant">
          <div class="h-full flex items-center justify-center p-8">
            <div class="glass-card rounded-2xl p-8 max-w-md w-full">
              <div class="flex items-center gap-4 mb-4">
                <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                  <PlusIcon size="md" variant="white" />
                </div>
                <div>
                  <h3 class="text-xl font-semibold text-gray-900">Sample Card</h3>
                  <p class="text-gray-600">{{ selectedTheme }} • {{ selectedVariant }}</p>
                </div>
              </div>
              
              <p class="text-gray-700 mb-6">
                This demonstrates how your content looks with the {{ selectedTheme }} theme 
                using {{ selectedVariant }} variant. Beautiful glass-morphism effects and 
                subtle animations create a modern, professional appearance.
              </p>
              
              <div class="flex gap-3">
                <button class="glass-button px-4 py-2 rounded-lg text-sm font-medium text-gray-700 hover:text-gray-900">
                  Cancel
                </button>
                <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
                  <PlusIcon size="sm" variant="white" />
                  Create
                </button>
              </div>
            </div>
          </div>
        </BeautifulBackground>
      </div>
      
      <!-- Code example -->
      <div class="mt-8 bg-gray-900 rounded-xl p-6 overflow-x-auto">
        <pre class="text-green-400 text-sm"><code>&lt;BeautifulBackground theme="{{ selectedTheme }}" variant="{{ selectedVariant }}"&gt;
  &lt;!-- Your content here --&gt;
&lt;/BeautifulBackground&gt;</code></pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import BeautifulBackground from './BeautifulBackground.vue'
import PlusIcon from './icons/PlusIcon.vue'

const selectedTheme = ref<'blue' | 'green' | 'purple' | 'rose' | 'amber' | 'cyan' | 'neutral'>('blue')
const selectedVariant = ref<'gradient' | 'solid' | 'mesh'>('gradient')

const themes = ['blue', 'green', 'purple', 'rose', 'amber', 'cyan', 'neutral'] as const
const variants = ['gradient', 'solid', 'mesh'] as const
</script>
