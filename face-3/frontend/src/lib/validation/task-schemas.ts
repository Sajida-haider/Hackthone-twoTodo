/**
 * Zod validation schemas for task forms.
 */
import { z } from 'zod';

export const taskTitleSchema = z
  .string()
  .min(1, 'Title is required')
  .max(200, 'Title must be less than 200 characters')
  .trim();

export const taskDescriptionSchema = z
  .string()
  .max(2000, 'Description must be less than 2000 characters')
  .trim()
  .optional();

export const taskDueDateSchema = z
  .string()
  .optional()
  .nullable()
  .transform((val) => {
    // Allow empty string, null, or undefined
    if (!val || val === '') return undefined;
    // Return the datetime-local value as-is for backend
    return val;
  });

export const createTaskSchema = z.object({
  title: taskTitleSchema,
  description: taskDescriptionSchema,
  due_date: taskDueDateSchema,
});

export const updateTaskSchema = z.object({
  title: taskTitleSchema.optional(),
  description: taskDescriptionSchema,
  status: z.enum(['pending', 'completed']).optional(),
  due_date: taskDueDateSchema,
});

export type CreateTaskFormData = z.infer<typeof createTaskSchema>;
export type UpdateTaskFormData = z.infer<typeof updateTaskSchema>;
