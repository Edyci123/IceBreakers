import React, { useState, useRef, useEffect, TextareaHTMLAttributes } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './FloatingTextarea.module.css';

interface FloatingTextareaProps extends Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'onChange'> {
  id: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  error?: string;
  touched?: boolean;
  maxLength?: number;
}

export default function FloatingTextarea({
  id,
  label,
  value,
  onChange,
  error,
  touched,
  maxLength = 1000,
  disabled,
  ...props
}: FloatingTextareaProps) {
  const [focused, setFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const hasValue = value !== '';
  const showError = !!error && !!touched;

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [value]);

  const fieldCls = [
    styles.field,
    focused ? styles.focused : '',
    showError ? styles.error : '',
    (focused || hasValue) ? styles.hasValue : '',
  ].filter(Boolean).join(' ');

  const charCount = value.length;
  const isOverLimit = charCount > 900;

  return (
    <div className={styles.wrapper}>
      <div className={fieldCls}>
        <textarea
          id={id}
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          className={styles.textarea}
          maxLength={maxLength}
          disabled={disabled}
          rows={1}
          {...props}
        />
        <label htmlFor={id} className={styles.label}>{label}</label>
      </div>
      <div className={styles.footer}>
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
        <span className={`${styles.counter} ${isOverLimit ? styles.counterWarning : ''}`}>
          {charCount} / {maxLength}
        </span>
      </div>
    </div>
  );
}
