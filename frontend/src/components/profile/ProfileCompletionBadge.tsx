import React from 'react';
import styles from './ProfileCompletionBadge.module.css';

interface ProfileCompletionBadgeProps {
  isComplete?: boolean;
  percent: number;
}

export default function ProfileCompletionBadge({ isComplete, percent }: ProfileCompletionBadgeProps) {
  if (isComplete) {
    return (
      <div className={`${styles.badge} ${styles.complete}`}>
        ✓ Profile Complete
      </div>
    );
  }
  return (
    <div className={`${styles.badge} ${styles.incomplete}`}>
      {percent}% Complete — finish your profile
    </div>
  );
}
