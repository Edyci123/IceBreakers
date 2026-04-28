import React from 'react';
import { motion } from 'framer-motion';
import styles from './ProfileCompletionRing.module.css';

interface ProfileCompletionRingProps {
  percentage: number;
  size?: number;
  showText?: boolean;
}

export default function ProfileCompletionRing({
  percentage,
  size = 90,
  showText = true
}: ProfileCompletionRingProps) {
  const strokeWidth = 6;
  const radius = (size - strokeWidth * 2) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  const gradientId = 'ringGrad';

  return (
    <svg
      width={size}
      height={size}
      className={styles.ring}
      aria-label={`Profile ${percentage}% complete`}
    >
      <defs>
        <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="var(--color-primary-400)" />
          <stop offset="100%" stopColor="var(--color-accent-400)" />
        </linearGradient>
      </defs>
      {/* Track */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="rgba(255,255,255,0.08)"
        strokeWidth={strokeWidth}
      />
      {/* Progress */}
      <motion.circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke={`url(#${gradientId})`}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={circumference}
        initial={{ strokeDashoffset: circumference }}
        animate={{ strokeDashoffset: offset }}
        transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
        style={{ transformOrigin: 'center', transform: 'rotate(-90deg)' }}
      />
      {/* Center text */}
      {showText && (
        <text
          x="50%"
          y="50%"
          textAnchor="middle"
          dominantBaseline="central"
          className={styles.label}
          fontSize={size * 0.22}
        >
          {percentage}%
        </text>
      )}
    </svg>
  );
}
