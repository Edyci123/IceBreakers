import React from 'react';
import styles from './ProfileAvatar.module.css';

interface ProfileAvatarProps {
  email?: string;
  firstName?: string;
  size?: number;
}

export default function ProfileAvatar({ email, firstName, size = 80 }: ProfileAvatarProps) {
  const initial = firstName
    ? firstName[0].toUpperCase()
    : email
    ? email[0].toUpperCase()
    : '?';

  return (
    <div
      className={styles.avatar}
      style={{ width: size, height: size, fontSize: size * 0.4 }}
      aria-label={`Avatar for ${email ?? 'user'}`}
    >
      {initial}
    </div>
  );
}
