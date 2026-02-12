/**
 * Utility functions for formatting data.
 */

/**
 * Format a date string or Date object to a readable format.
 */
export function formatDate(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;

  if (isNaN(dateObj.getTime())) {
    return 'Invalid date';
  }

  const now = new Date();
  const diffMs = now.getTime() - dateObj.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  // Less than 1 minute ago
  if (diffMins < 1) {
    return 'Just now';
  }

  // Less than 1 hour ago
  if (diffMins < 60) {
    return `${diffMins} ${diffMins === 1 ? 'minute' : 'minutes'} ago`;
  }

  // Less than 24 hours ago
  if (diffHours < 24) {
    return `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ago`;
  }

  // Less than 7 days ago
  if (diffDays < 7) {
    return `${diffDays} ${diffDays === 1 ? 'day' : 'days'} ago`;
  }

  // Format as date
  return dateObj.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Format a date to ISO string for datetime-local input.
 */
export function formatDateTimeLocal(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;

  if (isNaN(dateObj.getTime())) {
    return '';
  }

  return dateObj.toISOString().slice(0, 16);
}
