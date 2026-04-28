import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import LoginPage from '../LoginPage';
import { useAuth } from '../../../features/auth/useAuth';

vi.mock('../../../features/auth/useAuth', () => ({
  useAuth: vi.fn()
}));

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate
  };
});

describe('LoginPage', () => {
  const mockLogin = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useAuth).mockReturnValue({ login: mockLogin } as any);
  });

  it('shows field errors on empty submit', async () => {
    render(<MemoryRouter><LoginPage /></MemoryRouter>);
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    
    expect(await screen.findByText('Email is required')).toBeInTheDocument();
    expect(await screen.findByText('Password is required')).toBeInTheDocument();
  });

  it('shows email format error for invalid email', async () => {
    render(<MemoryRouter><LoginPage /></MemoryRouter>);
    const emailInput = screen.getByLabelText(/email address/i);
    fireEvent.change(emailInput, { target: { value: 'notanemail' } });
    fireEvent.blur(emailInput);
    
    expect(await screen.findByText('Enter a valid email address')).toBeInTheDocument();
  });

  it('shows password length error for short password', async () => {
    render(<MemoryRouter><LoginPage /></MemoryRouter>);
    const pwdInput = screen.getByLabelText(/password/i);
    fireEvent.change(pwdInput, { target: { value: 'short' } });
    fireEvent.blur(pwdInput);
    
    expect(await screen.findByText('Password must be at least 8 characters')).toBeInTheDocument();
  });

  it('calls auth.login with form values on valid submit', async () => {
    mockLogin.mockResolvedValueOnce(undefined);
    render(<MemoryRouter><LoginPage /></MemoryRouter>);
    
    fireEvent.change(screen.getByLabelText(/email address/i), { target: { value: 'test@test.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({ email: 'test@test.com', password: 'password123' });
    });
    expect(mockNavigate).toHaveBeenCalledWith('/profile', { replace: true });
  });

  it('shows server error alert on login failure', async () => {
    mockLogin.mockRejectedValueOnce(new Error('Invalid credentials'));
    render(<MemoryRouter><LoginPage /></MemoryRouter>);
    
    fireEvent.change(screen.getByLabelText(/email address/i), { target: { value: 'test@test.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    
    expect(await screen.findByText('Invalid credentials')).toBeInTheDocument();
  });
});
