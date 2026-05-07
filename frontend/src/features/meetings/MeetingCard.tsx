import React from 'react';
import { motion } from 'framer-motion';
import { format, formatDistanceToNow, parseISO } from 'date-fns';
import Button from '../../components/ui/Button';
import styles from './MeetingCard.module.css';
import type { Meeting, ProposalStatus } from './types';

interface MeetingCardProps {
  meeting: Meeting;
  /** The email of the currently logged-in user — used to determine which side we are. */
  currentUserEmail: string;
  onAccept(): void;
  onReject(): void;
  isMutating?: boolean;
}

const STATUS_LABELS: Record<ProposalStatus, string> = {
  pending: 'Pending',
  accepted: 'Accepted',
  rejected: 'Declined',
};

const STATUS_ICONS: Record<ProposalStatus, string> = {
  pending: '⏳',
  accepted: '✓',
  rejected: '✕',
};

function Avatar({ name, size = 36 }: { name: string; size?: number }) {
  const initials = name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
  return (
    <div
      className={styles.avatar}
      style={{ width: size, height: size, fontSize: size * 0.38 }}
      aria-hidden="true"
    >
      {initials}
    </div>
  );
}

export default function MeetingCard({
  meeting,
  currentUserEmail,
  onAccept,
  onReject,
  isMutating = false,
}: MeetingCardProps) {
  const isProposer = meeting.proposer_email === currentUserEmail;
  const myStatus: ProposalStatus = isProposer
    ? meeting.proposer_status
    : meeting.receiver_status;
  const otherEmail = isProposer ? meeting.receiver_email : meeting.proposer_email;
  const otherName = otherEmail.split('@')[0].replace(/[._]/g, ' ');
  const isPending = myStatus === 'pending';

  const typeLabel =
    meeting.meeting_type === 'coffeebreak' ? '☕ Coffee Break' : '📅 Meeting';

  const timeDisplay = meeting.proposed_time
    ? format(parseISO(meeting.proposed_time), 'EEE, MMM d · HH:mm')
    : null;

  const durationDisplay = meeting.duration_minutes
    ? `${meeting.duration_minutes} min`
    : null;

  const createdAgo = formatDistanceToNow(parseISO(meeting.created_at), {
    addSuffix: true,
  });

  return (
    <motion.article
      className={styles.card}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      whileHover={{ y: -3, boxShadow: '0 20px 60px rgba(0,0,0,0.35)' }}
      layout
    >
      {/* Header row: type + status badge */}
      <div className={styles.header}>
        <span className={styles.typeLabel}>{typeLabel}</span>
        <span className={`${styles.badge} ${styles[`badge_${myStatus}`]}`}>
          <span className={styles.badgeIcon}>{STATUS_ICONS[myStatus]}</span>
          {STATUS_LABELS[myStatus]}
        </span>
      </div>

      {/* Main content */}
      <div className={styles.body}>
        <div className={styles.avatarRow}>
          <Avatar name={otherName} size={44} />
          <div className={styles.personInfo}>
            <p className={styles.personName}>{otherName}</p>
            <p className={styles.personEmail}>{otherEmail}</p>
          </div>
        </div>

        {/* Time / location */}
        {(timeDisplay || meeting.location) && (
          <div className={styles.details}>
            {timeDisplay && (
              <div className={styles.detailRow}>
                <span className={styles.detailIcon}>🗓</span>
                <span>
                  {timeDisplay}
                  {durationDisplay && (
                    <span className={styles.duration}> · {durationDisplay}</span>
                  )}
                </span>
              </div>
            )}
            {meeting.location && (
              <div className={styles.detailRow}>
                <span className={styles.detailIcon}>📍</span>
                <span>{meeting.location}</span>
              </div>
            )}
          </div>
        )}

        {/* Message / icebreaker */}
        {meeting.message && (
          <blockquote className={styles.message}>"{meeting.message}"</blockquote>
        )}

        <p className={styles.meta}>Created {createdAgo}</p>
      </div>

      {/* Action buttons */}
      <div className={styles.actions}>
        <Button
          variant="primary"
          size="sm"
          onClick={onAccept}
          disabled={!isPending || isMutating}
          isLoading={isMutating && isPending}
          id={`accept-${meeting.id}`}
        >
          Accept
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onReject}
          disabled={!isPending || isMutating}
          id={`reject-${meeting.id}`}
        >
          Decline
        </Button>
      </div>
    </motion.article>
  );
}
