import React, { useState, InputHTMLAttributes } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './FloatingInput.module.css';

interface FloatingInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  id: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  error?: string;
  touched?: boolean;
  hint?: string;
}

export default function FloatingInput({
  id,
  label,
  value,
  onChange,
  error,
  touched,
  hint,
  type = 'text',
  disabled,
  ...props
}: FloatingInputProps) {
  const [focused, setFocused] = useState(false);
  const hasValue = value !== '';
  const showError = !!error && !!touched;

  const fieldCls = [
    styles.field,
    focused ? styles.focused : '',
    showError ? styles.error : '',
    (focused || hasValue) ? styles.hasValue : '',
  ].filter(Boolean).join(' ');

  return (
    <div className={styles.wrapper}>
      <div className={fieldCls}>
        <input
          id={id}
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          className={styles.input}
          disabled={disabled}
          {...props}
        />
        <label htmlFor={id} className={styles.label}>{label}</label>
      </div>
      <AnimatePresence>
        {showError && (
          <motion.p
            className={styles.errorMsg}
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.2 }}
          >
            ⚠ {error}
          </motion.p>
        )}
      </AnimatePresence>
      {hint && !showError && <p className={styles.hint}>{hint}</p>}
    </div>
  );
}
