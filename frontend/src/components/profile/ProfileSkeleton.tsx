import React from 'react';
import { Skeleton } from '../feedback';
import styles from './ProfileSkeleton.module.css';

export default function ProfileSkeleton() {
  return (
    <div className={styles.root}>
      {/* Header */}
      <div className={styles.header}>
        <Skeleton variant="circle" width={80} height={80} />
        <div className={styles.headerInfo}>
          <Skeleton width="200px" height="28px" />
          <div style={{ marginTop: '8px' }}><Skeleton width="160px" height="16px" /></div>
          <div style={{ marginTop: '12px' }}><Skeleton width="120px" height="22px" /></div>
        </div>
      </div>
      {/* Fields grid */}
      <div className={styles.grid}>
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className={`${styles.fieldCard} ${i >= 4 ? styles.full : ''}`}>
            <Skeleton width="80px" height="10px" />
            <div style={{ marginTop: '8px' }}><Skeleton width="100%" height="18px" /></div>
          </div>
        ))}
      </div>
    </div>
  );
}
