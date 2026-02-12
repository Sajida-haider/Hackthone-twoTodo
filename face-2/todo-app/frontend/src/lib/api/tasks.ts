/**
 * Task API client.
 */

import { getToken } from '@/lib/auth/better-auth';
import { Task, TaskCreate, TaskUpdate } from '@/lib/types/task';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Get authorization headers with JWT token.
 */
function getAuthHeaders(): HeadersInit {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };
}

/**
 * List all tasks for the current user.
 */
async function list(): Promise<Task[]> {
  const response = await fetch(`${API_URL}/api/v1/tasks`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to fetch tasks' }));
    throw new Error(error.detail || 'Failed to fetch tasks');
  }

  return response.json();
}

/**
 * Get a single task by ID.
 */
async function get(id: string): Promise<Task> {
  const response = await fetch(`${API_URL}/api/v1/tasks/${id}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to fetch task' }));
    throw new Error(error.detail || 'Failed to fetch task');
  }

  return response.json();
}

/**
 * Create a new task.
 */
async function create(data: TaskCreate): Promise<Task> {
  const response = await fetch(`${API_URL}/api/v1/tasks`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to create task' }));
    throw new Error(error.detail || 'Failed to create task');
  }

  return response.json();
}

/**
 * Update an existing task.
 */
async function update(id: string, data: TaskUpdate): Promise<Task> {
  const response = await fetch(`${API_URL}/api/v1/tasks/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to update task' }));
    throw new Error(error.detail || 'Failed to update task');
  }

  return response.json();
}

/**
 * Delete a task.
 */
async function deleteTask(id: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/v1/tasks/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to delete task' }));
    throw new Error(error.detail || 'Failed to delete task');
  }
}

export const taskApi = {
  list,
  get,
  create,
  update,
  delete: deleteTask,
};
