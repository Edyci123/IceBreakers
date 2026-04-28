import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import styles from './MeshBackground.module.css';

export default function MeshBackground() {
  const prefersReduced = useReducedMotion();

  const orb1Animation = prefersReduced ? {} : {
    animate: { x: ['-50px', '50px', '-50px'], y: ['-40px', '40px', '-40px'] },
    transition: { duration: 12, repeat: Infinity, ease: 'easeInOut' as const },
  };
  const orb2Animation = prefersReduced ? {} : {
    animate: { x: ['25px', '-25px', '25px'], y: ['25px', '-15px', '25px'] },
    transition: { duration: 16, repeat: Infinity, ease: 'easeInOut' as const },
  };
  const orb3Animation = prefersReduced ? {} : {
    animate: { x: ['-15px', '35px', '-15px'], y: ['-30px', '20px', '-30px'] },
    transition: { duration: 20, repeat: Infinity, ease: 'easeInOut' as const },
  };

  return (
    <div className={styles.root} aria-hidden="true">
      <div className={styles.gradient} />
      <motion.div className={styles.orb1} {...orb1Animation} />
      <motion.div className={styles.orb2} {...orb2Animation} />
      <motion.div className={styles.orb3} {...orb3Animation} />
      <div className={styles.noise} />
    </div>
  );
}
