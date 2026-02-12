'use client';

/**
 * Registration form component with React Hook Form and Zod validation.
 */
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { registerSchema, type RegisterFormData } from '@/lib/validation/auth-schemas';
import { authApi } from '@/lib/api/auth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface RegisterFormProps {
  onSuccess: () => void;
}

export default function RegisterForm({ onSuccess }: RegisterFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [passwordStrength, setPasswordStrength] = useState<string>('');

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    mode: 'onBlur',
  });

  const password = watch('password', '');

  // Calculate password strength
  const checkPasswordStrength = (password: string): string => {
    if (password.length === 0) return '';
    if (password.length < 8) return 'Too short (min 8 characters)';

    let strength = 0;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;

    if (strength <= 2) return 'Weak';
    if (strength <= 3) return 'Medium';
    return 'Strong';
  };

  // Update password strength when password changes
  useState(() => {
    setPasswordStrength(checkPasswordStrength(password));
  });

  const getPasswordStrengthColor = () => {
    if (passwordStrength === 'Strong') return 'text-green-400';
    if (passwordStrength === 'Medium') return 'text-yellow-400';
    return 'text-red-400';
  };

  const onSubmit = async (data: RegisterFormData) => {
    setApiError(null);
    setIsLoading(true);

    try {
      await authApi.register({ email: data.email, password: data.password });
      onSuccess();
    } catch (err: any) {
      setApiError(err.message || 'Registration failed. Please try again.');
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
          autoComplete="new-password"
          error={errors.password?.message}
          helperText="Min 8 characters, must include uppercase, lowercase, number, and special character"
          disabled={isLoading}
          {...register('password')}
        />

        {password && (
          <div className="text-sm">
            <span className="text-gray-300">Password strength: </span>
            <span className={`font-medium ${getPasswordStrengthColor()}`}>
              {passwordStrength}
            </span>
          </div>
        )}

        <Input
          label="Confirm Password"
          type="password"
          autoComplete="new-password"
          error={errors.confirmPassword?.message}
          disabled={isLoading}
          {...register('confirmPassword')}
        />
      </div>

      <Button
        type="submit"
        variant="primary"
        size="md"
        fullWidth
        isLoading={isLoading}
        disabled={isLoading}
      >
        {isLoading ? 'Creating account...' : 'Create account'}
      </Button>
    </form>
  );
}
