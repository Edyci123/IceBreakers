import React from 'react';
import styles from './Skeleton.module.css';

interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  variant?: 'text' | 'circle' | 'rect';
  lines?: number;
  className?: string;
}

export default function Skeleton({ width, height, variant = 'rect', lines = 1, className }: SkeletonProps) {
  const style = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  };

  if (variant === 'text' && lines > 1) {
    return (
      <div className={`${styles.textGroup} ${className ?? ''}`}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={styles.skeleton}
            style={{ width: i === lines - 1 ? '70%' : '100%', height: '14px' }}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={`${styles.skeleton} ${variant === 'circle' ? styles.circle : ''} ${className ?? ''}`}
      style={style}
    />
  );
}
