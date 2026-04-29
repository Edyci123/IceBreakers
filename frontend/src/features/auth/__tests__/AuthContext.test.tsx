import { render, screen, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AuthProvider } from '../AuthContext';
import { useAuth } from '../useAuth';
import { authApi } from '../authApi';

vi.mock('../authApi', () => ({
  authApi: {
    getCurrentUser: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn(),
  }
}));

const TestConsumer = () => {
  const { user, isInitialized, login, logout } = useAuth();
  return (
    <div>
      <div data-testid="init">{isInitialized.toString()}</div>
      <div data-testid="user">{user ? user.email : 'null'}</div>
      <button onClick={() => login({ email: 'test@test.com', password: 'password' })}>Login</button>
      <button onClick={() => logout()}>Logout</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('initializes with null user on authApi fail', async () => {
    vi.mocked(authApi.getCurrentUser).mockRejectedValueOnce(new Error('no user'));
    render(<AuthProvider><TestConsumer /></AuthProvider>);
    await waitFor(() => expect(screen.getByTestId('init').textContent).toBe('true'));
    expect(screen.getByTestId('user').textContent).toBe('null');
  });

  it('initializes with user on authApi success', async () => {
    vi.mocked(authApi.getCurrentUser).mockResolvedValueOnce({ id: '1', email: 'a@b.com', full_name: 'A', role: 'employee', is_active: true, created_at: '', updated_at: '' });
    render(<AuthProvider><TestConsumer /></AuthProvider>);
    await waitFor(() => expect(screen.getByTestId('init').textContent).toBe('true'));
    expect(screen.getByTestId('user').textContent).toBe('a@b.com');
  });

  it('login sets user on success', async () => {
    vi.mocked(authApi.getCurrentUser).mockRejectedValueOnce(new Error('no initial user'))
      .mockResolvedValueOnce({ id: '1', email: 'a@b.com', full_name: 'A', role: 'employee', is_active: true, created_at: '', updated_at: '' });
    vi.mocked(authApi.login).mockResolvedValueOnce(undefined);

    render(<AuthProvider><TestConsumer /></AuthProvider>);
    await waitFor(() => expect(screen.getByTestId('init').textContent).toBe('true'));
    
    screen.getByText('Login').click();
    await waitFor(() => expect(screen.getByTestId('user').textContent).toBe('a@b.com'));
  });

  it('logout clears user', async () => {
    vi.mocked(authApi.getCurrentUser).mockResolvedValueOnce({ id: '1', email: 'a@b.com', full_name: 'A', role: 'employee', is_active: true, created_at: '', updated_at: '' });
    vi.mocked(authApi.logout).mockResolvedValueOnce(undefined);

    render(<AuthProvider><TestConsumer /></AuthProvider>);
    await waitFor(() => expect(screen.getByTestId('init').textContent).toBe('true'));
    
    screen.getByText('Logout').click();
    await waitFor(() => expect(screen.getByTestId('user').textContent).toBe('null'));
  });

  it('auth:unauthorized event triggers logout', async () => {
    vi.mocked(authApi.getCurrentUser).mockResolvedValueOnce({ id: '1', email: 'a@b.com', full_name: 'A', role: 'employee', is_active: true, created_at: '', updated_at: '' });
    render(<AuthProvider><TestConsumer /></AuthProvider>);
    await waitFor(() => expect(screen.getByTestId('user').textContent).toBe('a@b.com'));

    act(() => {
      window.dispatchEvent(new Event('auth:unauthorized'));
    });
    await waitFor(() => expect(screen.getByTestId('user').textContent).toBe('null'));
  });
});
