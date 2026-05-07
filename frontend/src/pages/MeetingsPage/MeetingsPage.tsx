import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import MainLayout from '../../components/layout/MainLayout';
import Button from '../../components/ui/Button';
import { Alert } from '../../components/feedback';
import { useMeetings } from '../../features/meetings/useMeetings';
import MeetingCard from '../../features/meetings/MeetingCard';
import MeetingsSkeleton from '../../features/meetings/MeetingsSkeleton';
import { useAuth } from '../../features/auth/useAuth';
import { useToast } from '../../components/feedback/ToastContext';
import styles from './MeetingsPage.module.css';

export default function MeetingsPage() {
  const { user } = useAuth();
  const { pushToast } = useToast();
  const { meetings, isLoading, error, mutatingIds, refresh, accept, reject } =
    useMeetings();

  const [showOnlyPending, setShowOnlyPending] = useState(false);

  const filteredMeetings = showOnlyPending
    ? meetings.filter((m) => {
        const isProposer = m.proposer_email === user?.email;
        const myStatus = isProposer ? m.proposer_status : m.receiver_status;
        return myStatus === 'pending';
      })
    : meetings;

  const handleAccept = async (id: string) => {
    await accept(id);
    // Check if there's still an error after the action
    pushToast({
      type: 'success',
      message: "Meeting accepted! We'll sync this with your calendar soon.",
    });
  };

  const handleReject = async (id: string) => {
    await reject(id);
    pushToast({
      type: 'info',
      message: "Meeting declined. We'll look for new matches for you.",
    });
  };

  const handleAcceptSafe = async (id: string) => {
    try {
      await handleAccept(id);
    } catch {
      pushToast({ type: 'error', message: 'Could not accept the meeting. Please try again.' });
    }
  };

  const handleRejectSafe = async (id: string) => {
    try {
      await handleReject(id);
    } catch {
      pushToast({ type: 'error', message: 'Could not decline the meeting. Please try again.' });
    }
  };

  return (
    <MainLayout>
      <div className={styles.page}>
        {/* Page header */}
        <motion.div
          className={styles.pageHeader}
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div>
            <h1 className={styles.title}>☕ Coffee Break Matches</h1>
            <p className={styles.subtitle}>
              Connect with colleagues over coffee or a quick catch-up.
            </p>
          </div>

          {/* Toolbar */}
          <div className={styles.toolbar}>
            <label className={styles.filterToggle}>
              <input
                type="checkbox"
                checked={showOnlyPending}
                onChange={(e) => setShowOnlyPending(e.target.checked)}
                id="filter-pending"
              />
              <span className={styles.toggleTrack}>
                <span className={styles.toggleThumb} />
              </span>
              <span className={styles.filterLabel}>Pending only</span>
            </label>

            <Button
              variant="ghost"
              size="sm"
              onClick={refresh}
              disabled={isLoading}
              isLoading={isLoading && meetings.length > 0}
              id="refresh-meetings"
            >
              ↻ Refresh
            </Button>
          </div>
        </motion.div>

        {/* Error state */}
        {error && !isLoading && (
          <Alert type="error" className={styles.alert}>
            {error}{' '}
            <button className={styles.retryBtn} onClick={refresh}>
              Try again
            </button>
          </Alert>
        )}

        {/* Loading state — skeleton on first load */}
        {isLoading && meetings.length === 0 && <MeetingsSkeleton count={4} />}

        {/* Empty state */}
        {!isLoading && !error && filteredMeetings.length === 0 && (
          <motion.div
            className={styles.emptyState}
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.35 }}
          >
            <div className={styles.emptyIcon}>☕</div>
            {meetings.length === 0 ? (
              <>
                <h2 className={styles.emptyTitle}>No matches yet</h2>
                <p className={styles.emptyText}>
                  Make sure your{' '}
                  <Link to="/profile" className={styles.emptyLink}>
                    profile is complete
                  </Link>{' '}
                  to be included in the next matching run. Matching happens periodically — check
                  back soon!
                </p>
              </>
            ) : (
              <>
                <h2 className={styles.emptyTitle}>No pending matches</h2>
                <p className={styles.emptyText}>
                  All your current meetings have been responded to. Turn off the filter to see
                  all meetings.
                </p>
              </>
            )}
          </motion.div>
        )}

        {/* Cards grid */}
        {filteredMeetings.length > 0 && (
          <motion.div
            className={styles.grid}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            <AnimatePresence mode="popLayout">
              {filteredMeetings.map((meeting) => (
                <MeetingCard
                  key={meeting.id}
                  meeting={meeting}
                  currentUserEmail={user?.email ?? ''}
                  isMutating={mutatingIds.has(meeting.id)}
                  onAccept={() => handleAcceptSafe(meeting.id)}
                  onReject={() => handleRejectSafe(meeting.id)}
                />
              ))}
            </AnimatePresence>
          </motion.div>
        )}
      </div>
    </MainLayout>
  );
}
