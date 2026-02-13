"""TypeScript types for Task entity."""

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string | null;
  status: 'pending' | 'completed';
  due_date?: string | null;
  created_at: string;
  updated_at: string;
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
