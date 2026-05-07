import React from 'react';
import styles from './MeetingsSkeleton.module.css';

function SkeletonCard() {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div className={`${styles.shimmer} ${styles.tag}`} />
        <div className={`${styles.shimmer} ${styles.badge}`} />
      </div>
      <div className={styles.avatarRow}>
        <div className={`${styles.shimmer} ${styles.avatar}`} />
        <div className={styles.lines}>
          <div className={`${styles.shimmer} ${styles.line} ${styles.lineLong}`} />
          <div className={`${styles.shimmer} ${styles.line} ${styles.lineShort}`} />
        </div>
      </div>
      <div className={`${styles.shimmer} ${styles.block}`} />
      <div className={styles.actions}>
        <div className={`${styles.shimmer} ${styles.btn}`} />
        <div className={`${styles.shimmer} ${styles.btn}`} />
      </div>
    </div>
  );
}

export default function MeetingsSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className={styles.grid}>
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}
