import React, { ReactNode } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import MeshBackground from './MeshBackground';
import styles from './AuthLayout.module.css';

interface AuthLayoutProps {
  children: ReactNode;
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  const prefersReduced = useReducedMotion();

  return (
    <>
      <MeshBackground />
      <div className={styles.root}>
        <motion.div
          className={styles.card}
          initial={prefersReduced ? false : { opacity: 0, scale: 0.96, y: 32 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className={styles.logoArea}>
            <motion.div
              className={styles.logoMark}
              animate={prefersReduced ? {} : { scale: [1, 1.05, 1] }}
              transition={{ repeat: Infinity, duration: 2.5, ease: 'easeInOut' }}
            />
            <h1 className={styles.brand}>IceBreakers</h1>
            <p className={styles.tagline}>Connect with your colleagues</p>
          </div>
          <div className={styles.content}>
            {children}
          </div>
        </motion.div>
      </div>
    </>
  );
}