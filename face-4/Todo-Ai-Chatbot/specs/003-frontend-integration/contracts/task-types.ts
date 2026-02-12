/**
 * Task Type Definitions
 *
 * Type definitions for task-related data structures
 * used throughout the frontend application.
 */

/**
 * Task entity from backend
 */
export interface Task {
  id: string                    // UUID from backend
  title: string                 // Task title (max 200 chars)
  description: string           // Task description (max 2000 chars)
  isCompleted: boolean          // Completion status
  userId: string                // Owner user ID
  createdAt: string             // ISO 8601 timestamp
  updatedAt: string             // ISO 8601 timestamp
}

/**
 * Task creation data (sent to API)
 */
export interface CreateTaskData {
  title: string
  description: string
}

/**
 * Task update data (sent to API)
 */
export interface UpdateTaskData {
  title?: string
  description?: string
  isCompleted?: boolean
}

/**
 * Task form data (used in forms)
 */
export interface TaskFormData {
  title: string
  description: string
}

/**
 * Task state for UI
 */
export interface TaskState {
  tasks: Task[]
  isLoading: boolean
  error: string | null
  selectedTask: Task | null
}

/**
 * Task display state (per-task UI state)
 */
export interface TaskDisplayState {
  task: Task
  isEditing: boolean
  isDeleting: boolean
  isSaving: boolean
  error: string | null
}

/**
 * Task filter options
 */
export enum TaskFilter {
  ALL = 'all',
  ACTIVE = 'active',
  COMPLETED = 'completed',
}

/**
 * Task sort options
 */
export enum TaskSort {
  CREATED_DESC = 'created_desc',
  CREATED_ASC = 'created_asc',
  UPDATED_DESC = 'updated_desc',
  UPDATED_ASC = 'updated_asc',
  TITLE_ASC = 'title_asc',
  TITLE_DESC = 'title_desc',
}

/**
 * Task list view options
 */
export interface TaskListOptions {
  filter: TaskFilter
  sort: TaskSort
  searchQuery?: string
}

/**
 * Task statistics
 */
export interface TaskStats {
  total: number
  completed: number
  active: number
  completionRate: number
}

/**
 * Task operation result
 */
export type TaskOperationResult<T = Task> =
  | { success: true; data: T }
  | { success: false; error: string }

/**
 * Task event types for logging/analytics
 */
export enum TaskEventType {
  CREATED = 'task_created',
  UPDATED = 'task_updated',
  DELETED = 'task_deleted',
  COMPLETED = 'task_completed',
  UNCOMPLETED = 'task_uncompleted',
}

/**
 * Task event data
 */
export interface TaskEvent {
  type: TaskEventType
  timestamp: Date
  taskId: string
  userId: string
}
