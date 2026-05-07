/**
 * API client for the meetings endpoints.
 *
 * Endpoints (from icebreakers/meetings/api/router.py):
 *   POST   /api/meetings/proposals                       → create meeting
 *   GET    /api/meetings/proposals                       → list meetings for current user
 *   GET    /api/meetings/proposals/{id}                  → get single meeting
 *   PUT    /api/meetings/proposals/{id}/accept           → accept (CSRF required)
 *   PUT    /api/meetings/proposals/{id}/reject           → reject (CSRF required)
 *   DELETE /api/meetings/proposals/{id}                  → delete user-created meeting (CSRF required)
 */

import apiClient from '../../lib/apiClient';
import type { Meeting, MeetingCreateRequest, ProposalStatus } from './types';

export const meetingsApi = {
  /**
   * List all meetings involving the current authenticated user.
   * Optional filters: status (user's own status) and role (proposer | receiver).
   */
  async listMeetings(opts?: {
    status?: ProposalStatus;
    role?: 'proposer' | 'receiver';
  }): Promise<Meeting[]> {
    const params: Record<string, string> = {};
    if (opts?.status) params['status'] = opts.status;
    if (opts?.role) params['role'] = opts.role;

    const response = await apiClient.get<Meeting[]>('/meetings/proposals', { params });
    return response.data;
  },

  /** Get a single meeting by id. */
  async getMeeting(id: string): Promise<Meeting> {
    const response = await apiClient.get<Meeting>(`/meetings/proposals/${id}`);
    return response.data;
  },

  /** Create a new meeting proposal (proposer is auto-accepted). */
  async createMeeting(data: MeetingCreateRequest): Promise<Meeting> {
    const response = await apiClient.post<Meeting>('/meetings/proposals', data);
    return response.data;
  },

  /** Accept a meeting — sets the current user's own status to accepted. */
  async acceptMeeting(id: string): Promise<Meeting> {
    const response = await apiClient.put<Meeting>(`/meetings/proposals/${id}/accept`);
    return response.data;
  },

  /** Reject a meeting — sets the current user's own status to rejected. */
  async rejectMeeting(id: string): Promise<Meeting> {
    const response = await apiClient.put<Meeting>(`/meetings/proposals/${id}/reject`);
    return response.data;
  },

  /** Delete a user-created meeting (only creator, only while receiver is still pending). */
  async deleteMeeting(id: string): Promise<void> {
    await apiClient.delete(`/meetings/proposals/${id}`);
  },
};
