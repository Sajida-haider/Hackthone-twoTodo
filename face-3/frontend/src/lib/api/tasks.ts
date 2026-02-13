/**
 * Task API methods for frontend.
 */
import { apiClient } from './client';
import { Task, TaskCreate, TaskUpdate } from '../types/task';

export const taskApi = {
  /**
   * Create a new task.
   */
  create: async (data: TaskCreate): Promise<Task> => {
    return apiClient.post<Task>('/api/v1/tasks', data);
  },

  /**
   * Get all tasks for the authenticated user.
   */
  list: async (): Promise<Task[]> => {
    return apiClient.get<Task[]>('/api/v1/tasks');
  },

  /**
   * Get a single task by ID.
   */
  get: async (id: string): Promise<Task> => {
    return apiClient.get<Task>(`/api/v1/tasks/${id}`);
  },

  /**
   * Update a task.
   */
  update: async (id: string, data: TaskUpdate): Promise<Task> => {
    return apiClient.patch<Task>(`/api/v1/tasks/${id}`, data);
  },

  /**
   * Delete a task.
   */
  delete: async (id: string): Promise<void> => {
    return apiClient.delete<void>(`/api/v1/tasks/${id}`);
  },
};
