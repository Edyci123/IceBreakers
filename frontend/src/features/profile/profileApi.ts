import apiClient from '../../lib/apiClient';
import type { UserProfile, UpdateProfileRequest } from './types';

export const profileApi = {
  async getProfile(): Promise<UserProfile> {
    try {
      const response = await apiClient.get<UserProfile>('/profile');
      return response.data;
    } catch (error: any) {
      if (error.status === 404) {
        throw new Error('Profile not found');
      }
      throw error;
    }
  },

  async updateProfile(data: UpdateProfileRequest): Promise<UserProfile> {
    const response = await apiClient.put<UserProfile>('/profile', data);
    return response.data;
  }
};