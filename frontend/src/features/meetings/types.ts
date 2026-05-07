/**
 * TypeScript types for the Meetings feature.
 *
 * Maps to backend schemas:
 *  - MeetingResponse  → icebreakers/meetings/domain/schemas.py
 *  - ProposalStatus   → icebreakers/meetings/domain/enums.py  (ProposalStatus)
 *  - MeetingSource    → icebreakers/meetings/domain/enums.py  (MeetingSource)
 *  - MeetingType      → icebreakers/meetings/domain/enums.py  (MeetingType)
 */

/** Maps to backend ProposalStatus enum */
export type ProposalStatus = 'pending' | 'accepted' | 'rejected';

/** Maps to backend MeetingSource enum */
export type MeetingSource = 'user' | 'engine';

/** Maps to backend MeetingType enum */
export type MeetingType = 'coffeebreak' | 'other';

/**
 * Maps to backend MeetingResponse schema.
 * All dates are ISO 8601 strings on the frontend.
 */
export interface Meeting {
  id: string;
  proposer_id: string;
  receiver_id: string;
  proposer_status: ProposalStatus;
  receiver_status: ProposalStatus;
  source: MeetingSource;
  meeting_type: MeetingType;
  proposed_time: string | null;   // ISO 8601 or null
  duration_minutes: number | null;
  location: string | null;
  message: string | null;
  proposer_email: string;
  receiver_email: string;
  created_at: string;
  updated_at: string;
}

/** Payload for creating a new meeting (POST /api/meetings/proposals) */
export interface MeetingCreateRequest {
  receiver_id: string;
  meeting_type?: MeetingType;
  proposed_time?: string | null;
  duration_minutes?: number | null;
  location?: string | null;
  message?: string | null;
}
