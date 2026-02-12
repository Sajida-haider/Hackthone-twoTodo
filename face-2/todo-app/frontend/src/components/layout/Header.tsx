'use client';

/**
 * Header component with user email display and logout button.
 */
import { useAuth } from '@/components/auth/AuthProvider';
import { Button } from '@/components/ui/Button';

export function Header() {
  const { user, logout, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return null;
  }

  return (
    <header className="bg-gray-800 border-b border-gray-700 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-white">Todo App</h1>
          </div>

          <div className="flex items-center gap-4">
            {user?.email && (
              <span className="text-sm text-gray-300 font-medium">
                {user.email}
              </span>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={logout}
              className="text-white hover:bg-gray-700"
            >
              Logout
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
