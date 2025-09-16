# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Backend Development
```bash
# Setup frappe-bench and install gameplan (see README.md for full setup)
bench start                                    # Start frappe server
bench --site gameplan.test browse             # Access admin interface
bench --site gameplan.test execute gameplan.debug.execute  # Run debug scripts
bench --site gameplan.test migrate            # Run database migrations
bench --site gameplan.test install-app gameplan  # Install the app

# For debugging, create files like gameplan/debug.py with execute() function
```

### Frontend Development
```bash
npm run dev                  # Start Vite dev server (runs on port 8080)
npm run build               # Build for production
npm run frontend:pnpm_install  # Install frontend dependencies
```

### Testing
```bash
# Frontend tests
cd frontend && pnpm test                       # Run Cypress tests
cd frontend && pnpm test-local                 # Open Cypress in browser

# Access development app
http://gameplan.test:8080/g                    # Vite dev server
http://gameplan.test:8000/g                    # Production build
```

## Architecture Overview

### Backend Architecture (Frappe Framework)
- **DocTypes**: Core entities in `gameplan/gameplan/doctype/` following naming pattern `gp_*`
- **API Endpoints**: Defined in `gameplan/api.py` with `@frappe.whitelist()` decorators
- **Permissions**: Custom logic via `has_permission` hooks in `hooks.py`
- **Real-time**: Socket.IO integration using `frappe.publish_realtime()`
- **Search**: SQLite FTS5 implementation in `gameplan/search_sqlite.py`

### Frontend Architecture (Vue 3 + TypeScript)
- **Composition API**: Uses `<script setup>` syntax throughout
- **Data Layer**: frappe-ui composables (`useDoc`, `useList`, `useCall`) in `frontend/src/data/`
- **Components**: Reusable components in `frontend/src/components/`
- **Pages**: Route components in `frontend/src/pages/`
- **Routing**: Vue Router with nested layouts under `/g/` base path
- **Styling**: TailwindCSS with semantic classes (`text-ink-gray-*`, `bg-surface-*`)

### Core Entities
- **GP Project** → "Spaces" in UI (projects/workspaces)
- **GP Team** → "Categories" in UI (project groupings)
- **GP Discussion** → Main discussion threads
- **GP Comment** → Comments on discussions/tasks with reactions
- **GP Page** → Collaborative documents
- **GP Artwork Task** → New artwork workflow management (see below)

### Artwork Management System
A complete role-based workflow system with three user roles:

#### User Roles & Permissions
- **Artwork Sales Team**: Create tasks, edit own drafts/rework, submit for review
- **Artwork Quality Team**: Review tasks, approve/reject, handle final review
- **Artwork Procurement Team**: Handle approved tasks, prepare for final review

#### Workflow States
1. `Draft` → `Awaiting Quality Review` (Sales)
2. `Awaiting Quality Review` → `Approved by Quality` | `Rework` (Quality)
3. `Approved by Quality` → `Awaiting Final Review` (Procurement)
4. `Awaiting Final Review` → `Final Approved` | `Final Rework` (Quality)
5. `Final Rework` → `Awaiting Final Review` (Procurement)

#### Key Files
**Backend:**
- `gameplan/gameplan/doctype/gp_artwork_task/` - Main doctype
- `gameplan/gameplan/doctype/gp_artwork_attachment/` - File attachments
- `gameplan/gameplan/doctype/gp_artwork_status_history/` - Status tracking
- `gameplan/realtime_artwork.py` - Real-time notifications

**Frontend:**
- `frontend/src/pages/ArtworkKanban.vue` - Drag-and-drop kanban board
- `frontend/src/pages/ArtworkTask.vue` - Task detail view with discussions
- `frontend/src/pages/ApprovedArtworkTasks.vue` - Reporting view
- `frontend/src/data/artworkTasks.ts` - Data management composables

## Development Patterns

### Backend Patterns
```python
# API endpoints
@frappe.whitelist()
@validate_type
def create_artwork_task(title: str, project: str):
    # Implementation
    
# Custom permissions
def has_permission(doc, user=None, permission_type=None):
    # Role-based logic
    
# Real-time notifications
frappe.publish_realtime(
    event="artwork_task_update",
    message=data,
    user=target_user
)
```

### Frontend Patterns
```typescript
// Data composables
const { data, loading, error } = useList({
  doctype: 'GP Artwork Task',
  fields: ['name', 'title', 'status'],
  auto: true
})

// Status management with transitions
const allowedTransitions = computed(() => 
  taskDetails.value?.allowed_transitions || []
)
```

### File Organization
- Backend: Follow Frappe DocType structure with separate files for each entity
- Frontend: Feature-based organization with shared components
- Use TypeScript interfaces for type safety
- Implement proper error handling and loading states

### Integration Points
- Socket.IO events for real-time updates
- frappe-ui for consistent data fetching patterns
- Existing GP Comment system for discussions
- Built-in permission system with role-based access
- Search integration with existing SQLite FTS5

## Key Implementation Details

### Permission System
The artwork system implements strict role-based permissions:
- Sales can only edit their own tasks in specific states
- Quality team controls approval workflows
- Procurement team manages final preparation
- All changes trigger appropriate notifications

### Real-time Features
- Status changes broadcast to relevant users
- Comment additions notify task participants  
- Attachment uploads trigger participant notifications
- Kanban board updates reflect changes immediately

### Data Consistency
- Status history tracks all transitions with reasons
- Attachment versioning with metadata
- Activity logging for audit trails
- Proper transaction handling for state changes

This system demonstrates proper integration with existing Gameplan patterns while adding comprehensive workflow management capabilities.
