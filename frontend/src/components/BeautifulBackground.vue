<template>
  <div :class="[
    'min-h-screen w-full relative',
    backgroundClass
  ]">
    <!-- Animated background elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <!-- Primary decorative shapes -->
      <div 
        v-for="shape in decorativeShapes" 
        :key="shape.id"
        :class="[
          'absolute rounded-full blur-xl opacity-20',
          shape.color,
          shape.size,
          shape.animation
        ]"
        :style="shape.position"
      ></div>
      
      <!-- Subtle grid pattern -->
      <div 
        class="absolute inset-0 opacity-10"
        :style="{
          backgroundImage: `radial-gradient(circle at 1px 1px, ${gridColor} 1px, transparent 0)`,
          backgroundSize: '24px 24px'
        }"
      ></div>
    </div>
    
    <!-- Content slot -->
    <div class="relative z-10">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  theme?: 'blue' | 'green' | 'purple' | 'rose' | 'amber' | 'cyan' | 'neutral'
  variant?: 'gradient' | 'solid' | 'mesh'
}

const props = withDefaults(defineProps<Props>(), {
  theme: 'blue',
  variant: 'gradient'
})

const themeConfig = {
  blue: {
    gradient: 'bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50',
    solid: 'bg-blue-50',
    mesh: 'bg-gradient-to-br from-blue-50 via-cyan-50 to-indigo-50',
    shapes: ['bg-blue-200', 'bg-indigo-200', 'bg-cyan-200'],
    grid: '#3b82f6'
  },
  green: {
    gradient: 'bg-gradient-to-br from-slate-50 via-green-50 to-emerald-50',
    solid: 'bg-green-50',
    mesh: 'bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50',
    shapes: ['bg-green-200', 'bg-emerald-200', 'bg-teal-200'],
    grid: '#10b981'
  },
  purple: {
    gradient: 'bg-gradient-to-br from-slate-50 via-purple-50 to-violet-50',
    solid: 'bg-purple-50',
    mesh: 'bg-gradient-to-br from-purple-50 via-violet-50 to-fuchsia-50',
    shapes: ['bg-purple-200', 'bg-violet-200', 'bg-fuchsia-200'],
    grid: '#8b5cf6'
  },
  rose: {
    gradient: 'bg-gradient-to-br from-slate-50 via-rose-50 to-pink-50',
    solid: 'bg-rose-50',
    mesh: 'bg-gradient-to-br from-rose-50 via-pink-50 to-red-50',
    shapes: ['bg-rose-200', 'bg-pink-200', 'bg-red-200'],
    grid: '#f43f5e'
  },
  amber: {
    gradient: 'bg-gradient-to-br from-slate-50 via-amber-50 to-orange-50',
    solid: 'bg-amber-50',
    mesh: 'bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50',
    shapes: ['bg-amber-200', 'bg-yellow-200', 'bg-orange-200'],
    grid: '#f59e0b'
  },
  cyan: {
    gradient: 'bg-gradient-to-br from-slate-50 via-cyan-50 to-sky-50',
    solid: 'bg-cyan-50',
    mesh: 'bg-gradient-to-br from-cyan-50 via-sky-50 to-blue-50',
    shapes: ['bg-cyan-200', 'bg-sky-200', 'bg-blue-200'],
    grid: '#06b6d4'
  },
  neutral: {
    gradient: 'bg-gradient-to-br from-gray-50 via-slate-50 to-stone-50',
    solid: 'bg-gray-50',
    mesh: 'bg-gradient-to-br from-slate-50 via-gray-50 to-zinc-50',
    shapes: ['bg-gray-200', 'bg-slate-200', 'bg-stone-200'],
    grid: '#6b7280'
  }
}

const backgroundClass = computed(() => {
  return themeConfig[props.theme][props.variant]
})

const gridColor = computed(() => {
  return themeConfig[props.theme].grid + '30' // Add transparency
})

const decorativeShapes = computed(() => {
  const shapes = themeConfig[props.theme].shapes
  return [
    {
      id: 1,
      color: shapes[0],
      size: 'w-32 h-32',
      position: { top: '20%', left: '15%' },
      animation: 'animate-pulse'
    },
    {
      id: 2,
      color: shapes[1],
      size: 'w-40 h-40',
      position: { bottom: '25%', right: '20%' },
      animation: 'animate-pulse animation-delay-1000'
    },
    {
      id: 3,
      color: shapes[2],
      size: 'w-24 h-24',
      position: { top: '60%', right: '15%' },
      animation: 'animate-pulse animation-delay-500'
    },
    {
      id: 4,
      color: shapes[0],
      size: 'w-20 h-20',
      position: { top: '10%', right: '40%' },
      animation: 'animate-pulse animation-delay-2000'
    },
    {
      id: 5,
      color: shapes[1],
      size: 'w-16 h-16',
      position: { bottom: '40%', left: '25%' },
      animation: 'animate-pulse animation-delay-1500'
    }
  ]
})
</script>

<style scoped>
.animation-delay-500 {
  animation-delay: 0.5s;
}

.animation-delay-1000 {
  animation-delay: 1s;
}

.animation-delay-1500 {
  animation-delay: 1.5s;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

/* Smooth animations */
@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.animate-float {
  animation: float 6s ease-in-out infinite;
}

/* Custom backdrop blur for better performance */
.backdrop-blur-custom {
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
</style>
