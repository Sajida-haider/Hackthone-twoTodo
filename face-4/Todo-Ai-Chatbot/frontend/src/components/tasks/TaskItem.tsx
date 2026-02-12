'use client';

/**
 * Task item component with toggle, edit, and delete functionality.
 */
import { useState } from 'react';
import { Task } from '@/lib/types/task';
import { useTasks } from '@/hooks/useTasks';
import { useToast } from '@/hooks/useToast';
import { formatDate } from '@/lib/utils/format';
import { Button } from '@/components/ui/Button';
import TaskEditModal from './TaskEditModal';

interface TaskItemProps {
  task: Task;
  onToggle?: () => void;
  onUpdate?: () => void;
  onDelete?: () => void;
}

export default function TaskItem({ task, onToggle, onUpdate, onDelete }: TaskItemProps) {
  const { showToast } = useToast();
  const { toggleTaskCompletion, deleteTask } = useTasks();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  const handleToggleComplete = async () => {
    if (onToggle) {
      // Use parent's callback
      setIsToggling(true);
      try {
        await onToggle();
        showToast(
          task.status === 'pending' ? 'Task marked as completed!' : 'Task marked as pending',
          'success'
        );
      } catch (error) {
        showToast('Failed to update task status', 'error');
        console.error('Failed to toggle task:', error);
      } finally {
        setIsToggling(false);
      }
    } else {
      // Fallback to local useTasks
      try {
        await toggleTaskCompletion(task.id);
        showToast(
          task.status === 'pending' ? 'Task marked as completed!' : 'Task marked as pending',
          'success'
        );
        if (onUpdate) onUpdate();
      } catch (error) {
        showToast('Failed to update task status', 'error');
        console.error('Failed to toggle task:', error);
      }
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    if (onDelete) {
      // Use parent's callback
      setIsDeleting(true);
      try {
        await onDelete();
        showToast('Task deleted successfully!', 'success');
      } catch (error) {
        showToast('Failed to delete task', 'error');
        console.error('Failed to delete task:', error);
      } finally {
        setIsDeleting(false);
      }
    } else {
      // Fallback to local useTasks
      setIsDeleting(true);
      try {
        await deleteTask(task.id);
        showToast('Task deleted successfully!', 'success');
        if (onUpdate) onUpdate();
      } catch (error) {
        showToast('Failed to delete task', 'error');
        console.error('Failed to delete task:', error);
      } finally {
        setIsDeleting(false);
      }
    }
  };

  return (
    <>
      <div className="p-4 border border-gray-700 rounded-lg bg-gray-800 hover:shadow-lg hover:border-gray-600 transition-all">
        <div className="flex items-start gap-3">
          <input
            type="checkbox"
            checked={task.status === 'completed'}
            onChange={handleToggleComplete}
            disabled={isToggling}
            className="mt-1 w-5 h-5 cursor-pointer text-blue-500 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-offset-gray-800"
            aria-label={`Mark task "${task.title}" as ${task.status === 'completed' ? 'pending' : 'completed'}`}
          />

          <div className="flex-1 min-w-0">
            <h3
              className={`font-medium ${
                task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-100'
              }`}
            >
              {task.title}
            </h3>

            {task.description && (
              <p className="text-sm text-gray-400 mt-1 whitespace-pre-wrap">
                {task.description}
              </p>
            )}

            <div className="flex flex-wrap gap-3 mt-2 text-xs text-gray-500">
              <span>Created: {formatDate(task.created_at)}</span>
              {task.due_date && (
                <>
                  <span>•</span>
                  <span>Due: {formatDate(task.due_date)}</span>
                </>
              )}
              <span>•</span>
              <span className={`font-medium ${
                task.status === 'completed' ? 'text-green-400' : 'text-yellow-400'
              }`}>
                {task.status}
              </span>
            </div>
          </div>

          <div className="flex gap-2 flex-shrink-0">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsEditModalOpen(true)}
            >
              Edit
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={handleDelete}
              isLoading={isDeleting}
              disabled={isDeleting}
            >
              Delete
            </Button>
          </div>
        </div>
      </div>

      <TaskEditModal
        task={task}
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        onSuccess={() => {
          setIsEditModalOpen(false);
          if (onUpdate) onUpdate();
        }}
      />
    </>
  );
}
