# Procurement Workflow Components

This document describes the Vue.js components built for the Procurement Workflow system.

## Overview

The procurement workflow system provides a visual, interactive way to track tasks through four main stages:
1. **Draft** - Initial creation
2. **Procurement Review** - Under review
3. **Procurement Rework** - Needs changes
4. **Final Approved** - Ready for bucket

## Components

### 1. ProcurementWorkflowStepper.vue

The main component that displays the horizontal stepper with all workflow stages.

**Features:**
- Horizontal progress line with gradient colors
- Interactive stage circles with icons
- Task cards for each stage
- Animated bucket for approved tasks
- Toast notifications for task movements
- Responsive design

**Props:**
- None (uses global state from `useArtworkKanban`)

**Events:**
- `task-clicked` - Emitted when a task card is clicked
- `task-moved` - Emitted when a task is moved between stages

### 2. ProcurementBucketAnimated.vue

An animated bucket component that displays approved tasks as stacked documents.

**Features:**
- Animated bucket icon with bounce effect
- Stacked document visualization
- Drop animation when new tasks are added
- Modal with task list
- Hover effects and transitions

**Props:**
- `tasks` - Array of approved tasks
- `bucketBounce` - Boolean to trigger bounce animation

**Events:**
- `task-clicked` - Emitted when a task is clicked
- `bucket-clicked` - Emitted when the bucket is clicked

### 3. ProcurementTaskCard.vue

Individual task card component with animation support.

**Features:**
- Priority-based styling
- Drop animation when moving to bucket
- Hover effects
- Customer and cycle information

**Props:**
- `task` - Task object
- `stageKey` - Current stage key
- `isDroppingToBucket` - Boolean to trigger drop animation

**Events:**
- `click` - Emitted when the card is clicked

### 4. ProcurementWorkflow.vue

Main page component that integrates all workflow components.

**Features:**
- Header with refresh functionality
- Statistics cards
- Task detail modal
- Integration with existing data layer

### 5. ProcurementWorkflowDemo.vue

Demo page with sample data and interactive controls.

**Features:**
- Sample task data
- Interactive demo controls
- Simulated task movements
- Statistics display
- Reset functionality

## Usage

### Basic Usage

```vue
<template>
  <ProcurementWorkflowStepper 
    @task-clicked="handleTaskClick"
    @task-moved="handleTaskMove"
  />
</template>

<script setup>
import ProcurementWorkflowStepper from '@/components/ProcurementWorkflowStepper.vue'

const handleTaskClick = (task) => {
  console.log('Task clicked:', task)
}

const handleTaskMove = (payload) => {
  console.log('Task moved:', payload)
}
</script>
```

### With Animated Bucket

```vue
<template>
  <ProcurementBucketAnimated 
    :tasks="approvedTasks"
    :bucket-bounce="bucketBounce"
    @task-clicked="handleTaskClick"
  />
</template>

<script setup>
import { ref } from 'vue'
import ProcurementBucketAnimated from '@/components/ProcurementBucketAnimated.vue'

const approvedTasks = ref([])
const bucketBounce = ref(false)

const handleTaskClick = (task) => {
  console.log('Task clicked:', task)
}
</script>
```

## Styling

The components use Tailwind CSS with custom animations and transitions:

- **Colors**: Orange to green gradient for progress
- **Animations**: Smooth transitions and bounce effects
- **Shadows**: Soft shadows for depth
- **Rounded corners**: Modern, playful design
- **Responsive**: Works on all screen sizes

## Animation Details

### Drop to Bucket Animation
When a task is moved to "Final Approved":
1. Task card animates with scale and opacity changes
2. Bucket bounces slightly when receiving the document
3. Toast notification appears with success message
4. Task is removed from stepper and added to bucket

### Document Stack Animation
- Documents are stacked with slight rotation and offset
- New documents animate in from the top
- Overflow indicator shows count of additional documents

## Data Structure

Tasks should have the following structure:

```typescript
interface Task {
  name: string
  title: string
  customer_title: string
  priority: 'Low' | 'Medium' | 'High' | 'Urgent'
  modified: string
  cycle_count?: number
  status: string
  workflow_type: 'Procurement Cycle'
}
```

## Integration

The components integrate with the existing data layer:
- Uses `useArtworkKanban` composable for data
- Integrates with existing API calls
- Maintains consistency with current design system
- Uses Frappe UI components for consistency

## Browser Support

- Modern browsers with CSS Grid and Flexbox support
- CSS Custom Properties (CSS Variables)
- CSS Transitions and Animations
- ES6+ JavaScript features

## Performance

- Optimized animations using CSS transforms
- Efficient re-rendering with Vue 3 reactivity
- Lazy loading of modal content
- Debounced API calls
