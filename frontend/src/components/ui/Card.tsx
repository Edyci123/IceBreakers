import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';
import styles from './Card.module.css';

interface CardProps {
  children: ReactNode;
  variant?: 'default' | 'elevated' | 'highlight';
  animate?: boolean;
  className?: string;
}

export default function Card({ children, variant = 'default', animate = true, className }: CardProps) {
  const cls = [styles.card, styles[variant], className].filter(Boolean).join(' ');

  if (animate) {
    return (
      <motion.div
        className={cls}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      >
        {children}
      </motion.div>
    );
  }

  return <div className={cls}>{children}</div>;
}
