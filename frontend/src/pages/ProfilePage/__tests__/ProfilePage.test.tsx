import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import ProfilePage from '../ProfilePage';
import { profileApi } from '../../../features/profile/profileApi';

vi.mock('../../../features/profile/profileApi', () => ({
  profileApi: {
    getProfile: vi.fn(),
    updateProfile: vi.fn()
  }
}));

vi.mock('../../../features/auth/useAuth', () => ({
  useAuth: () => ({
    user: { email: 'test@example.com' },
    logout: vi.fn()
  })
}));

describe('ProfilePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders profile data after load', async () => {
    vi.mocked(profileApi.getProfile).mockResolvedValueOnce({
      id: '1', user_id: '1', first_name: 'Alice', last_name: 'Smith',
      middle_name: null, bio: null, interests: null, avatar_url: null, location: null,
      is_profile_complete: true, created_at: '', updated_at: ''
    });

    render(<MemoryRouter><ProfilePage /></MemoryRouter>);
    
    expect(await screen.findByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Smith')).toBeInTheDocument();
    expect(screen.queryByText('Complete your profile to get better matches')).not.toBeInTheDocument();
  });

  it('shows incomplete profile alert when is_profile_complete is false', async () => {
    vi.mocked(profileApi.getProfile).mockResolvedValueOnce({
      id: '1', user_id: '1', first_name: 'Alice', last_name: 'Smith',
      middle_name: null, bio: null, interests: null, avatar_url: null, location: null,
      is_profile_complete: false, created_at: '', updated_at: ''
    });

    render(<MemoryRouter><ProfilePage /></MemoryRouter>);
    
    expect(await screen.findByText('Complete your profile to get better matches')).toBeInTheDocument();
  });

  it('shows error alert and retry button on load failure', async () => {
    vi.mocked(profileApi.getProfile).mockRejectedValueOnce({ message: 'Server error', status: 500 });

    render(<MemoryRouter><ProfilePage /></MemoryRouter>);
    
    expect(await screen.findByText('Could not load your profile. Please try again.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  it('saves profile on form submit', async () => {
    vi.mocked(profileApi.getProfile).mockResolvedValueOnce({
      id: '1', user_id: '1', first_name: 'Alice', last_name: 'Smith',
      middle_name: null, bio: null, interests: null, avatar_url: null, location: null,
      is_profile_complete: true, created_at: '', updated_at: ''
    });
    vi.mocked(profileApi.updateProfile).mockResolvedValueOnce({
      id: '1', user_id: '1', first_name: 'Bob', last_name: 'Smith',
      middle_name: null, bio: null, interests: null, avatar_url: null, location: null,
      is_profile_complete: true, created_at: '', updated_at: ''
    });

    render(<MemoryRouter><ProfilePage /></MemoryRouter>);
    
    await screen.findByText('Alice');
    
    fireEvent.click(screen.getByRole('button', { name: /edit profile/i }));
    
    const nameInput = screen.getByLabelText(/first name/i);
    fireEvent.change(nameInput, { target: { value: 'Bob' } });
    
    fireEvent.click(screen.getByRole('button', { name: /save changes/i }));
    
    await waitFor(() => {
      expect(profileApi.updateProfile).toHaveBeenCalledWith(expect.objectContaining({
        first_name: 'Bob'
      }));
    });
    
    expect(await screen.findByText('Profile saved successfully!')).toBeInTheDocument();
  });
});
