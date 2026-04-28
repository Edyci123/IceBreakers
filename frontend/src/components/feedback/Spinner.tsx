import React from 'react';
import styles from './Spinner.module.css';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  fullPage?: boolean;
  color?: 'primary' | 'white';
}

const sizeMap = { sm: 16, md: 24, lg: 40 };

export default function Spinner({ size = 'md', fullPage = false, color = 'primary' }: SpinnerProps) {
  const px = sizeMap[size];

  const spinner = (
    <div
      className={`${styles.spinner} ${styles[color]}`}
      style={{ width: px, height: px }}
      role="status"
      aria-label="Loading"
    >
      <div className={styles.outer} />
      <div className={styles.inner} />
    </div>
  );

  if (fullPage) {
    return (
      <div className={styles.fullPage}>
        {spinner}
        <span className={styles.loadingText}>Loading…</span>
      </div>
    );
  }

  return spinner;
}