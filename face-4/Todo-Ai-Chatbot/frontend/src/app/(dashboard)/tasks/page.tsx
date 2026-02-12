'use client';

/**
 * Tasks page - main dashboard for task management.
 */
import { useEffect } from 'react';
import { useTasks } from '@/hooks/useTasks';
import TaskForm from '@/components/tasks/TaskForm';
import TaskItem from '@/components/tasks/TaskItem';
import { EmptyState } from '@/components/tasks/EmptyState';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { FloatingChatButton } from '@/components/chat/FloatingChatButton';

export default function TasksPage() {
  const { tasks, isLoading, error, fetchTasks, toggleTaskCompletion, deleteTask } = useTasks();

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleToggle = async (taskId: string) => {
    await toggleTaskCompletion(taskId);
    await fetchTasks();
  };

  const handleDelete = async (taskId: string) => {
    await deleteTask(taskId);
    await fetchTasks();
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-4xl font-extrabold text-white mb-8">My Tasks</h1>

      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white mb-4">Create New Task</h2>
        <TaskForm onSuccess={fetchTasks} />
      </div>

      <div className="mt-8">
        {isLoading ? (
          <div className="text-center py-12">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-gray-400">Loading tasks...</p>
          </div>
        ) : error ? (
          <ErrorMessage
            message={error}
            onRetry={fetchTasks}
            className="my-4"
          />
        ) : tasks.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-white">
              Your Tasks ({tasks.length})
            </h2>
            <div className="space-y-3">
              {tasks.map((task) => (
                <TaskItem
                  key={task.id}
                  task={task}
                  onToggle={() => handleToggle(task.id)}
                  onUpdate={fetchTasks}
                  onDelete={() => handleDelete(task.id)}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Floating AI Chat Button */}
      <FloatingChatButton />
    </div>
  );
}
