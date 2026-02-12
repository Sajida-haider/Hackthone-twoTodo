'use client';

/**
 * Task edit modal with React Hook Form and Zod validation.
 */
import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { updateTaskSchema, type UpdateTaskFormData } from '@/lib/validation/task-schemas';
import { Task } from '@/lib/types/task';
import { useTasks } from '@/hooks/useTasks';
import { useToast } from '@/hooks/useToast';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface TaskEditModalProps {
  task: Task;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function TaskEditModal({ task, isOpen, onClose, onSuccess }: TaskEditModalProps) {
  const { showToast } = useToast();
  const { updateTask } = useTasks();

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<UpdateTaskFormData>({
    resolver: zodResolver(updateTaskSchema),
    mode: 'onBlur',
    defaultValues: {
      title: task.title,
      description: task.description || '',
      status: task.status,
      due_date: task.due_date ? new Date(task.due_date).toISOString().slice(0, 16) : '',
    },
  });

  const title = watch('title', '');
  const description = watch('description', '');

  // Reset form when task changes
  useEffect(() => {
    reset({
      title: task.title,
      description: task.description || '',
      status: task.status,
      due_date: task.due_date ? new Date(task.due_date).toISOString().slice(0, 16) : '',
    });
  }, [task, reset]);

  if (!isOpen) return null;

  const onSubmit = async (data: UpdateTaskFormData) => {
    try {
      await updateTask(task.id, {
        title: data.title,
        description: data.description || undefined,
        status: data.status,
        due_date: data.due_date ? new Date(data.due_date).toISOString() : undefined,
      });
      showToast('Task updated successfully!', 'success');
      onSuccess();
      onClose();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update task';
      showToast(errorMessage, 'error');
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget && !isSubmitting) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="edit-task-title"
    >
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 w-full max-w-md shadow-xl">
        <h2 id="edit-task-title" className="text-2xl font-bold text-gray-100 mb-4">
          Edit Task
        </h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <Input
              label="Title"
              type="text"
              error={errors.title?.message}
              disabled={isSubmitting}
              {...register('title')}
            />
            <p className="mt-1 text-xs text-gray-400 text-right">
              {title?.length || 0}/200 characters
            </p>
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-1">
              Description
            </label>
            <textarea
              id="description"
              rows={3}
              disabled={isSubmitting}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 text-gray-100 rounded-lg shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-800 disabled:cursor-not-allowed placeholder-gray-500"
              {...register('description')}
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-400" role="alert">
                {errors.description.message}
              </p>
            )}
            <p className="mt-1 text-xs text-gray-400 text-right">
              {description?.length || 0}/2000 characters
            </p>
          </div>

          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-300 mb-1">
              Status
            </label>
            <select
              id="status"
              disabled={isSubmitting}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 text-gray-100 rounded-lg shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-800 disabled:cursor-not-allowed"
              {...register('status')}
            >
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
            </select>
            {errors.status && (
              <p className="mt-1 text-sm text-red-400" role="alert">
                {errors.status.message}
              </p>
            )}
          </div>

          <div>
            <Input
              label="Due Date (optional)"
              type="datetime-local"
              error={errors.due_date?.message}
              disabled={isSubmitting}
              {...register('due_date')}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="submit"
              variant="primary"
              size="md"
              isLoading={isSubmitting}
              disabled={isSubmitting}
              className="flex-1"
            >
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              size="md"
              onClick={onClose}
              disabled={isSubmitting}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
