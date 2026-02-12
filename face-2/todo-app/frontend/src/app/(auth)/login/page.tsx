'use client';

/**
 * Login page for user authentication.
 */
import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import LoginForm from '@/components/auth/LoginForm';

function LoginMessages() {
  const searchParams = useSearchParams();
  const registered = searchParams.get('registered');
  const verified = searchParams.get('verified');

  return (
    <>
      {registered && (
        <div className="rounded-md bg-blue-900/50 border border-blue-700 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-blue-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-blue-200">
                Registration successful! Please check your email to verify your account before logging in.
              </p>
            </div>
          </div>
        </div>
      )}

      {verified && (
        <div className="rounded-md bg-green-900/50 border border-green-700 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-green-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-green-200">
                Email verified successfully! You can now sign in.
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-100">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-400">
            Or{' '}
            <a
              href="/register"
              className="font-medium text-blue-400 hover:text-blue-300"
            >
              create a new account
            </a>
          </p>
        </div>

        <Suspense fallback={null}>
          <LoginMessages />
        </Suspense>

        <LoginForm />
      </div>
    </div>
  );
}
