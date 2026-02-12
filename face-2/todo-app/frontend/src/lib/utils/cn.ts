/**
 * Utility function to merge Tailwind CSS classes.
 * Combines clsx for conditional classes and tailwind-merge for intelligent merging.
 */
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
