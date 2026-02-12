'use client';

/**
 * Task creation form with React Hook Form and Zod validation.
 */
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { createTaskSchema, type CreateTaskFormData } from '@/lib/validation/task-schemas';
import { useToast } from '@/hooks/useToast';
import { useTasks } from '@/hooks/useTasks';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface TaskFormProps {
  onSuccess?: () => void;
}

export default function TaskForm({ onSuccess }: TaskFormProps) {
  const { showToast } = useToast();
  const { createTask } = useTasks();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<CreateTaskFormData>({
    resolver: zodResolver(createTaskSchema),
    mode: 'onBlur',
  });

  const title = watch('title', '');
  const description = watch('description', '');

  const onSubmit = async (data: CreateTaskFormData) => {
    setIsSubmitting(true);

    try {
      await createTask({
        title: data.title,
        description: data.description,
        due_date: data.due_date,
      });

      reset();
      showToast('Task created successfully!', 'success');

      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create task';
      showToast(errorMessage, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 p-6 border border-gray-700 rounded-lg bg-gray-800 shadow-sm">
      <div>
        <Input
          label="Title"
          type="text"
          placeholder="Enter task title"
          error={errors.title?.message}
          disabled={isSubmitting}
          {...register('title')}
        />
        <p className="mt-1 text-xs text-gray-400 text-right">
          {title.length}/200 characters
        </p>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-1">
          Description
        </label>
        <textarea
          id="description"
          placeholder="Enter task description (optional)"
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
        <Input
          label="Due Date (optional)"
          type="datetime-local"
          error={errors.due_date?.message}
          disabled={isSubmitting}
          {...register('due_date')}
        />
      </div>

      <Button
        type="submit"
        variant="primary"
        size="md"
        fullWidth
        isLoading={isSubmitting}
        disabled={isSubmitting}
      >
        {isSubmitting ? 'Creating...' : 'Create Task'}
      </Button>
    </form>
  );
}
