/**
 * Tests for LoginForm component.
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LoginForm from '@/components/auth/LoginForm';
import { useAuth } from '@/components/auth/AuthProvider';

// Mock the auth context
jest.mock('@/components/auth/AuthProvider', () => ({
  useAuth: jest.fn(),
}));

describe('LoginForm', () => {
  const mockLogin = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useAuth as jest.Mock).mockReturnValue({
      login: mockLogin,
      logout: jest.fn(),
      register: jest.fn(),
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  it('renders login form with all fields', () => {
    render(<LoginForm />);

    expect(screen.getByPlaceholderText('Email address')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign in/i })).toBeInTheDocument();
    expect(screen.getByText(/Resend verification email/i)).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    render(<LoginForm />);

    const submitButton = screen.getByRole('button', { name: /Sign in/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Please enter both email and password/i)).toBeInTheDocument();
    });

    expect(mockLogin).not.toHaveBeenCalled();
  });

  it('submits form with valid credentials', async () => {
    mockLogin.mockResolvedValue(undefined);

    render(<LoginForm />);

    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: /Sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'SecurePass123!');
    });
  });

  it('displays error for invalid credentials', async () => {
    mockLogin.mockRejectedValue(new Error('Invalid email or password'));

    render(<LoginForm />);

    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: /Sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'WrongPass123!' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Invalid email or password/i)).toBeInTheDocument();
    });
  });

  it('displays error for unverified email', async () => {
    mockLogin.mockRejectedValue(new Error('Email address is not verified'));

    render(<LoginForm />);

    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: /Sign in/i });

    fireEvent.change(emailInput, { target: { value: 'unverified@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Please verify your email address/i)).toBeInTheDocument();
    });
  });

  it('displays error for locked account', async () => {
    mockLogin.mockRejectedValue(
      new Error('Account is locked due to too many failed login attempts. Please try again in 15 minutes.')
    );

    render(<LoginForm />);

    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: /Sign in/i });

    fireEvent.change(emailInput, { target: { value: 'locked@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Account is locked/i)).toBeInTheDocument();
      expect(screen.getByText(/15 minutes/i)).toBeInTheDocument();
    });
  });

  it('shows loading state during submission', async () => {
    mockLogin.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(<LoginForm />);

    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: /Sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.click(submitButton);

    expect(screen.getByText(/Signing in.../i)).toBeInTheDocument();
    expect(submitButton).toBeDisabled();

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalled();
    });
  });

  it('disables form inputs during submission', async () => {
    mockLogin.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(<LoginForm />);

    const emailInput = screen.getByPlaceholderText('Email address') as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText('Password') as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /Sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.click(submitButton);

    expect(emailInput.disabled).toBe(true);
    expect(passwordInput.disabled).toBe(true);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalled();
    });
  });
});
