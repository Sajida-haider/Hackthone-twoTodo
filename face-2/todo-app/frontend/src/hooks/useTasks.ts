'use client';

/**
 * Custom hook for managing task state and operations.
 */
import { useState, useCallback } from 'react';
import { Task, TaskCreate, TaskUpdate } from '@/lib/types/task';
import { taskApi } from '@/lib/api/tasks';

interface UseTasksReturn {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  fetchTasks: () => Promise<void>;
  createTask: (data: TaskCreate) => Promise<Task>;
  updateTask: (id: string, data: TaskUpdate) => Promise<Task>;
  deleteTask: (id: string) => Promise<void>;
  toggleTaskCompletion: (id: string) => Promise<void>;
}

export function useTasks(): UseTasksReturn {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await taskApi.list();
      setTasks(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load tasks';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createTask = useCallback(async (data: TaskCreate): Promise<Task> => {
    try {
      setError(null);
      const newTask = await taskApi.create(data);
      setTasks((prev) => [newTask, ...prev]);
      return newTask;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create task';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const updateTask = useCallback(async (id: string, data: TaskUpdate): Promise<Task> => {
    try {
      setError(null);
      const updatedTask = await taskApi.update(id, data);
      setTasks((prev) =>
        prev.map((task) => (task.id === id ? updatedTask : task))
      );
      return updatedTask;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update task';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const deleteTask = useCallback(async (id: string): Promise<void> => {
    try {
      setError(null);
      await taskApi.delete(id);
      setTasks((prev) => prev.filter((task) => task.id !== id));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete task';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const toggleTaskCompletion = useCallback(async (id: string): Promise<void> => {
    const task = tasks.find((t) => t.id === id);
    if (!task) return;

    const newStatus = task.status === 'pending' ? 'completed' : 'pending';
    await updateTask(id, { status: newStatus });
  }, [tasks, updateTask]);

  return {
    tasks,
    isLoading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleTaskCompletion,
  };
}
