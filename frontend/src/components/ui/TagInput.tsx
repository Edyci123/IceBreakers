import React, { useState, KeyboardEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './TagInput.module.css';

interface TagInputProps {
  id: string;
  label: string;
  tags: string[];
  onChange: (tags: string[]) => void;
  error?: string;
  touched?: boolean;
}

export default function TagInput({ id, label, tags, onChange, error, touched }: TagInputProps) {
  const [inputValue, setInputValue] = useState('');
  const [focused, setFocused] = useState(false);
  const showError = !!error && !!touched;

  const addTag = (value: string) => {
    const trimmed = value.trim().replace(/,$/, '').trim();
    if (trimmed && !tags.includes(trimmed)) {
      onChange([...tags, trimmed]);
    }
    setInputValue('');
  };

  const removeTag = (tag: string) => {
    onChange(tags.filter((t) => t !== tag));
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addTag(inputValue);
    } else if (e.key === 'Backspace' && inputValue === '' && tags.length > 0) {
      removeTag(tags[tags.length - 1]);
    }
  };

  const fieldCls = [
    styles.field,
    focused ? styles.focused : '',
    showError ? styles.error : '',
  ].filter(Boolean).join(' ');

  return (
    <div className={styles.wrapper}>
      <label htmlFor={id} className={styles.label}>{label}</label>
      <div className={fieldCls}>
        <div className={styles.tagsRow}>
          <AnimatePresence initial={false}>
            {tags.map((tag) => (
              <motion.span
                key={tag}
                className={styles.tag}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.15 }}
              >
                {tag}
                <button
                  type="button"
                  className={styles.removeTag}
                  onClick={() => removeTag(tag)}
                  aria-label={`Remove ${tag}`}
                >
                  ×
                </button>
              </motion.span>
            ))}
          </AnimatePresence>
          <input
            id={id}
            type="text"
            className={styles.input}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setFocused(true)}
            onBlur={() => { setFocused(false); if (inputValue) addTag(inputValue); }}
            placeholder={tags.length === 0 ? 'Type and press Enter or comma...' : ''}
          />
        </div>
      </div>
      <AnimatePresence>
        {showError && (
          <motion.p
            className={styles.errorMsg}
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            ⚠ {error}
          </motion.p>
        )}
      </AnimatePresence>
      <p className={styles.hint}>Press Enter or comma to add. Backspace to remove last.</p>
    </div>
  );
}
