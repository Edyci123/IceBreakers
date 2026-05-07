import { useState, useEffect, useCallback, useRef } from 'react';
import { meetingsApi } from './meetingsApi';
import { getErrorMessage } from '../../lib/errorMessages';
import type { Meeting, ProposalStatus } from './types';

interface UseMeetingsResult {
  meetings: Meeting[];
  isLoading: boolean;
  isMutating: boolean;
  error: string | null;
  mutatingIds: Set<string>;
  refresh(): Promise<void>;
  accept(id: string): Promise<void>;
  reject(id: string): Promise<void>;
}

/**
 * Hook that manages the full lifecycle of meeting proposals:
 * fetching, optimistic accept/reject with rollback, and error handling.
 */
export function useMeetings(): UseMeetingsResult {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mutatingIds, setMutatingIds] = useState<Set<string>>(new Set());

  // Track current meetings in a ref so callbacks can access latest state
  const meetingsRef = useRef(meetings);
  meetingsRef.current = meetings;

  const fetchMeetings = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await meetingsApi.listMeetings();
      setMeetings(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMeetings();
  }, [fetchMeetings]);

  const refresh = useCallback(async () => {
    await fetchMeetings();
  }, [fetchMeetings]);

  /**
   * Optimistically update the meeting's status for the current user,
   * then confirm with the server. Rolls back on error.
   */
  const mutate = useCallback(
    async (
      id: string,
      optimisticField: 'proposer_status' | 'receiver_status',
      newStatus: ProposalStatus,
      apiCall: () => Promise<Meeting>,
    ) => {
      // Save snapshot for rollback
      const snapshot = meetingsRef.current;

      // Optimistic update
      setMutatingIds((prev) => new Set(prev).add(id));
      setMeetings((prev) =>
        prev.map((m) =>
          m.id === id ? { ...m, [optimisticField]: newStatus } : m,
        ),
      );
      setError(null);

      try {
        const updated = await apiCall();
        // Merge server response (source of truth)
        setMeetings((prev) =>
          prev.map((m) => (m.id === updated.id ? updated : m)),
        );
      } catch (err) {
        // Roll back to snapshot
        setMeetings(snapshot);
        setError(getErrorMessage(err));
      } finally {
        setMutatingIds((prev) => {
          const next = new Set(prev);
          next.delete(id);
          return next;
        });
      }
    },
    [],
  );

  /**
   * Determine which status field belongs to the current user.
   * The user is the proposer if their id matches proposer_id.
   * Since we don't have the current user id in this hook, we check both statuses:
   * we optimistically update whichever side is still 'pending'.
   */
  const getOptimisticField = useCallback(
    (meeting: Meeting): 'proposer_status' | 'receiver_status' => {
      // If proposer is still pending (shouldn't happen on user-created, but covers engine), update proposer
      if (meeting.proposer_status === 'pending') return 'proposer_status';
      return 'receiver_status';
    },
    [],
  );

  const accept = useCallback(
    async (id: string) => {
      const meeting = meetingsRef.current.find((m) => m.id === id);
      if (!meeting) return;
      const field = getOptimisticField(meeting);
      await mutate(id, field, 'accepted', () => meetingsApi.acceptMeeting(id));
    },
    [mutate, getOptimisticField],
  );

  const reject = useCallback(
    async (id: string) => {
      const meeting = meetingsRef.current.find((m) => m.id === id);
      if (!meeting) return;
      const field = getOptimisticField(meeting);
      await mutate(id, field, 'rejected', () => meetingsApi.rejectMeeting(id));
    },
    [mutate, getOptimisticField],
  );

  return {
    meetings,
    isLoading,
    isMutating: mutatingIds.size > 0,
    error,
    mutatingIds,
    refresh,
    accept,
    reject,
  };
}
