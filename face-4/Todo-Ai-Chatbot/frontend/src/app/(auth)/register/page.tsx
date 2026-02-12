'use client';

/**
 * Registration page for new user signup.
 */
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import RegisterForm from '@/components/auth/RegisterForm';

export default function RegisterPage() {
  const router = useRouter();
  const [registrationSuccess, setRegistrationSuccess] = useState(false);

  const handleRegistrationSuccess = () => {
    setRegistrationSuccess(true);
    // Redirect to login after 3 seconds
    setTimeout(() => {
      router.push('/login?registered=true');
    }, 3000);
  };

  if (registrationSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="mx-auto h-12 w-12 text-green-400">
              <svg
                className="h-12 w-12"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h2 className="mt-6 text-3xl font-extrabold text-white">
              Registration Successful!
            </h2>
            <p className="mt-2 text-sm text-gray-300">
              Please check your email to verify your account.
            </p>
            <p className="mt-2 text-sm text-gray-400">
              Redirecting to login page...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-300">
            Or{' '}
            <a
              href="/login"
              className="font-medium text-blue-400 hover:text-blue-300"
            >
              sign in to your existing account
            </a>
          </p>
        </div>
        <RegisterForm onSuccess={handleRegistrationSuccess} />
      </div>
    </div>
  );
}
