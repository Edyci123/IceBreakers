import React from 'react';
import { motion } from 'framer-motion';
import styles from './Alert.module.css';

interface AlertProps {
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  onDismiss?: () => void;
  compact?: boolean;
}

const icons = {
  success: '✓',
  error: '✕',
  info: 'ℹ',
  warning: '⚠',
};

export default function Alert({ type, message, onDismiss, compact }: AlertProps) {
  return (
    <motion.div
      className={`${styles.alert} ${styles[type]} ${compact ? styles.compact : ''}`}
      role="alert"
      initial={{ opacity: 0, y: -16, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -8, scale: 0.97 }}
      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
    >
      <span className={styles.icon} aria-hidden="true">{icons[type]}</span>
      <div className={styles.message}>{message}</div>
      {onDismiss && (
        <button
          className={styles.dismissBtn}
          onClick={onDismiss}
          aria-label="Dismiss alert"
        >
          ×
        </button>
      )}
    </motion.div>
  );
}