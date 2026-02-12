/**
 * Tests for RegisterForm component.
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import RegisterForm from '@/components/auth/RegisterForm';
import { authApi } from '@/lib/api/auth';

// Mock the auth API
jest.mock('@/lib/api/auth', () => ({
  authApi: {
    register: jest.fn(),
  },
}));

describe('RegisterForm', () => {
  const mockOnSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders registration form with all fields', () => {
    render(<RegisterForm onSuccess={mockOnSuccess} />);

    expect(screen.getByPlaceholderText('Email address')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Password \(min 8 characters\)/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Confirm password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Create account/i })).toBeInTheDocument();
  });

  it('validates email format', async () => {
    render(<RegisterForm onSuccess={mockOnSuccess} />);

    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText(/Password \(min 8 characters\)/i);
    const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');
    const submitButton = screen.getByRole('button', { name: /Create account/i });

    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Please enter a valid email address/i)).toBeInTheDocument();
    });

    expect(authApi.register).not.toHaveBeenCalled();
  });

  it('validates password length', async () => {
    render(<RegisterForm onSuccess={mockOnSuccess} />);

    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText(/Password \(min 8 characters\)/i);
    const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');
    const submitButton = screen.getByRole('button', { name: /Create account/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'Short1!' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'Short1!' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Password must be at least 8 characters long/i)).toBeInTheDocument();
    });

    expect(authApi.register).not.toHaveBeenCalled();
  });

  it('validates password confirmation match', async () => {
    render(<RegisterForm onSuccess={mockOnSuccess} />);

    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText(/Password \(min 8 characters\)/i);
    const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');
    const submitButton = screen.getByRole('button', { name: /Create account/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'DifferentPass456!' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Passwords do not match/i)).toBeInTheDocument();
    });

    expect(authApi.register).not.toHaveBeenCalled();
  });

  it('displays password strength indicator', () => {
    render(<RegisterForm onSuccess={mockOnSuccess} />);

    const passwordInput = screen.getByPlaceholderText(/Password \(min 8 characters\)/i);

    // Weak password
    fireEvent.change(passwordInput, { target: { value: 'password' } });
    expect(screen.getByText(/Weak/i)).toBeInTheDocument();

    // Strong password
    fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });
    expect(screen.getByText(/Strong/i)).toBeInTheDocument();
  });

  it('submits form with valid data', async () => {
    (authApi.register as jest.Mock).mockResolvedValue({
      message: 'Registration successful',
      user_id: '123',
      email: 'test@example.com',
    });

    render(<RegisterForm onSuccess={mockOnSuccess} />);

    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText(/Password \(min 8 characters\)/i);
    const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');
    const submitButton = screen.getByRole('button', { name: /Create account/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(authApi.register).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'SecurePass123!',
      });
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  it('displays error message on registration failure', async () => {
    (authApi.register as jest.Mock).mockRejectedValue(
      new Error('Email address is already registered')
    );

    render(<RegisterForm onSuccess={mockOnSuccess} />);

    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText(/Password \(min 8 characters\)/i);
    const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');
    const submitButton = screen.getByRole('button', { name: /Create account/i });

    fireEvent.change(emailInput, { target: { value: 'existing@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Email address is already registered/i)).toBeInTheDocument();
    });

    expect(mockOnSuccess).not.toHaveBeenCalled();
  });

  it('shows loading state during submission', async () => {
    (authApi.register as jest.Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(<RegisterForm onSuccess={mockOnSuccess} />);

    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText(/Password \(min 8 characters\)/i);
    const confirmPasswordInput = screen.getByPlaceholderText('Confirm password');
    const submitButton = screen.getByRole('button', { name: /Create account/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.click(submitButton);

    expect(screen.getByText(/Creating account.../i)).toBeInTheDocument();
    expect(submitButton).toBeDisabled();

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });
});
