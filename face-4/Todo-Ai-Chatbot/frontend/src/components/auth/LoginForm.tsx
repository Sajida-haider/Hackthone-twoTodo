'use client';

/**
 * Login form component with React Hook Form and Zod validation.
 */
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema, type LoginFormData } from '@/lib/validation/auth-schemas';
import { useAuth } from '@/components/auth/AuthProvider';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

export default function LoginForm() {
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    mode: 'onBlur',
  });

  const onSubmit = async (data: LoginFormData) => {
    setApiError(null);
    setIsLoading(true);

    try {
      await login(data.email, data.password);
      // Success - AuthProvider handles redirect
    } catch (err: any) {
      // Show the actual error from backend
      const errorMsg = err?.response?.data?.detail || err?.message || 'Login failed. Please try again.';
      setApiError(errorMsg);
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
      {apiError && (
        <div className="rounded-md bg-red-900/50 border border-red-700 p-4" role="alert">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-red-300">{apiError}</p>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-4">
        <Input
          label="Email address"
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          disabled={isLoading}
          {...register('email')}
        />

        <Input
          label="Password"
          type="password"
          autoComplete="current-password"
          error={errors.password?.message}
          disabled={isLoading}
          {...register('password')}
        />
      </div>

      <div className="flex items-center justify-between">
        <div className="text-sm">
          <a
            href="/verify-email"
            className="font-medium text-blue-400 hover:text-blue-300"
          >
            Resend verification email
          </a>
        </div>
      </div>

      <Button
        type="submit"
        variant="primary"
        size="md"
        fullWidth
        isLoading={isLoading}
        disabled={isLoading}
      >
        {isLoading ? 'Signing in...' : 'Sign in'}
      </Button>
    </form>
  );
}
