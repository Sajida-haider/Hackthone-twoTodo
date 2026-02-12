/**
 * Tests for VerifyEmail page component.
 */
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { useRouter, useSearchParams } from 'next/navigation';
import VerifyEmailPage from '@/app/(auth)/verify-email/page';
import { authApi } from '@/lib/api/auth';

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useSearchParams: jest.fn(),
}));

// Mock the auth API
jest.mock('@/lib/api/auth', () => ({
  authApi: {
    verifyEmail: jest.fn(),
    resendVerification: jest.fn(),
  },
}));

describe('VerifyEmailPage', () => {
  const mockPush = jest.fn();
  const mockGet = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    (useSearchParams as jest.Mock).mockReturnValue({ get: mockGet });
  });

  it('shows verifying state initially', () => {
    mockGet.mockReturnValue('test-token-123');

    render(<VerifyEmailPage />);

    expect(screen.getByText(/Verifying your email.../i)).toBeInTheDocument();
  });

  it('shows error when no token provided', () => {
    mockGet.mockReturnValue(null);

    render(<VerifyEmailPage />);

    expect(screen.getByText(/Verification Failed/i)).toBeInTheDocument();
    expect(screen.getByText(/No verification token provided/i)).toBeInTheDocument();
  });

  it('shows success message on successful verification', async () => {
    mockGet.mockReturnValue('valid-token-123');
    (authApi.verifyEmail as jest.Mock).mockResolvedValue({
      message: 'Email verified successfully',
      user_id: '123',
    });

    render(<VerifyEmailPage />);

    await waitFor(() => {
      expect(screen.getByText(/Email Verified!/i)).toBeInTheDocument();
      expect(screen.getByText(/Email verified successfully/i)).toBeInTheDocument();
    });

    expect(authApi.verifyEmail).toHaveBeenCalledWith('valid-token-123');
  });

  it('redirects to login after successful verification', async () => {
    mockGet.mockReturnValue('valid-token-123');
    (authApi.verifyEmail as jest.Mock).mockResolvedValue({
      message: 'Email verified successfully',
      user_id: '123',
    });

    jest.useFakeTimers();
    render(<VerifyEmailPage />);

    await waitFor(() => {
      expect(screen.getByText(/Email Verified!/i)).toBeInTheDocument();
    });

    // Fast-forward time
    jest.advanceTimersByTime(3000);

    expect(mockPush).toHaveBeenCalledWith('/login?verified=true');

    jest.useRealTimers();
  });

  it('shows error message on verification failure', async () => {
    mockGet.mockReturnValue('invalid-token-123');
    (authApi.verifyEmail as jest.Mock).mockRejectedValue(
      new Error('Invalid verification token')
    );

    render(<VerifyEmailPage />);

    await waitFor(() => {
      expect(screen.getByText(/Verification Failed/i)).toBeInTheDocument();
      expect(screen.getByText(/Invalid verification token/i)).toBeInTheDocument();
    });
  });

  it('shows resend verification form on error', async () => {
    mockGet.mockReturnValue('expired-token-123');
    (authApi.verifyEmail as jest.Mock).mockRejectedValue(
      new Error('Token expired')
    );

    render(<VerifyEmailPage />);

    await waitFor(() => {
      expect(screen.getByText(/Need a new verification link?/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/Enter your email/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Resend/i })).toBeInTheDocument();
    });
  });
});
