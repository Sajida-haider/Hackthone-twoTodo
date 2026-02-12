/**
 * Task type definitions.
 */

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'completed';
  due_date?: string;
  created_at: string;
  updated_at: string;
  user_id: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  due_date?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: 'pending' | 'completed';
  due_date?: string;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}
