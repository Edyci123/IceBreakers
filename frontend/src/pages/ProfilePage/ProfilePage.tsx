import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../features/auth/useAuth';
import MainLayout from '../../components/layout/MainLayout';
import { Alert } from '../../components/feedback';
import { Button, FloatingInput, FloatingTextarea, TagInput } from '../../components/ui';
import ProfileAvatar from '../../components/profile/ProfileAvatar';
import ProfileCompletionRing from '../../components/profile/ProfileCompletionRing';
import ProfileCompletionBadge from '../../components/profile/ProfileCompletionBadge';
import ProfileSkeleton from '../../components/profile/ProfileSkeleton';
import { profileApi } from '../../features/profile/profileApi';
import type { UserProfile, UpdateProfileRequest } from '../../features/profile/types';
import { getErrorMessage } from '../../lib/errorMessages';
import styles from './ProfilePage.module.css';

// Compute completion % from filled fields
function calcCompletion(p: UserProfile | null): number {
  if (!p) return 0;
  if (p.is_profile_complete) return 100;
  const fields = [p.first_name, p.last_name, p.location, p.interests?.length, p.bio];
  const filled = fields.filter(Boolean).length;
  return Math.round((filled / fields.length) * 100);
}

const staggerContainer = {
  visible: { transition: { staggerChildren: 0.07 } },
};
const staggerChild = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35 } },
};

interface ReadFieldProps {
  label: string;
  value: string | null | undefined;
  full?: boolean;
}

function ReadField({ label, value, full }: ReadFieldProps) {
  return (
    <motion.div
      className={`${styles.fieldCard} ${full ? styles.fieldFull : ''}`}
      variants={staggerChild}
    >
      <span className={styles.fieldLabel}>{label}</span>
      <span className={`${styles.fieldValue} ${!value ? styles.fieldEmpty : ''}`}>
        {value || '—'}
      </span>
    </motion.div>
  );
}

export default function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // Edit form state
  const [form, setForm] = useState<UpdateProfileRequest>({
    first_name: '',
    last_name: '',
    middle_name: '',
    location: '',
    bio: '',
    interests: [],
    avatar_url: null,
  });
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const fetchProfile = async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const data = await profileApi.getProfile();
      setProfile(data);
      setForm({
        first_name: data.first_name ?? '',
        last_name: data.last_name ?? '',
        middle_name: data.middle_name ?? '',
        location: data.location ?? '',
        bio: data.bio ?? '',
        interests: data.interests ?? [],
        avatar_url: data.avatar_url ?? null,
      });
    } catch (err) {
      setLoadError('Could not load your profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchProfile(); }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaveError(null);
    setSaveSuccess(false);
    try {
      const updated = await profileApi.updateProfile(form);
      setProfile(updated);
      setSaveSuccess(true);
      setIsEditing(false);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setSaveError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setSaveError(null);
    if (profile) {
      setForm({
        first_name: profile.first_name ?? '',
        last_name: profile.last_name ?? '',
        middle_name: profile.middle_name ?? '',
        location: profile.location ?? '',
        bio: profile.bio ?? '',
        interests: profile.interests ?? [],
        avatar_url: profile.avatar_url ?? null,
      });
    }
  };

  const completionPercent = calcCompletion(profile);
  const displayName = [profile?.first_name, profile?.last_name].filter(Boolean).join(' ') || 'Your Profile';

  return (
    <MainLayout>
      <div className={styles.page}>
        {/* Retry on load error */}
        <AnimatePresence>
          {loadError && (
            <Alert
              type="error"
              message={loadError}
              onDismiss={() => setLoadError(null)}
            />
          )}
        </AnimatePresence>

        {/* Save success */}
        <AnimatePresence>
          {saveSuccess && (
            <Alert type="success" message="Profile saved successfully!" />
          )}
        </AnimatePresence>

        {/* Retry button */}
        {loadError && !loading && (
          <div className={styles.retryRow}>
            <Button variant="secondary" size="sm" onClick={fetchProfile}>
              Retry
            </Button>
          </div>
        )}

        {/* Skeleton */}
        {loading && !profile && <ProfileSkeleton />}

        {/* Loaded content */}
        {!loading && profile && (
          <>
            {/* Profile Header */}
            <div className={styles.profileHeader}>
              <div className={styles.avatarArea}>
                <div className={styles.avatarStack}>
                  <ProfileAvatar
                    email={user?.email}
                    firstName={profile.first_name ?? undefined}
                    size={80}
                  />
                  <div className={styles.ringWrapper}>
                    <ProfileCompletionRing percentage={completionPercent} size={100} showText={false} />
                  </div>
                </div>
              </div>
              <div className={styles.headerInfo}>
                <h1 className={styles.profileName}>{displayName}</h1>
                <p className={styles.profileEmail}>{user?.email}</p>
                <ProfileCompletionBadge
                  isComplete={profile.is_profile_complete}
                  percent={completionPercent}
                />
              </div>
              <div className={styles.headerActions}>
                {!isEditing && (
                  <Button variant="primary" size="md" onClick={() => setIsEditing(true)}>
                    Edit Profile
                  </Button>
                )}
              </div>
            </div>

            {/* Save error */}
            <AnimatePresence>
              {saveError && (
                <Alert type="error" message={saveError} onDismiss={() => setSaveError(null)} />
              )}
            </AnimatePresence>

            {/* Read / Edit view with AnimatePresence transition */}
            <AnimatePresence mode="wait">
              {!isEditing ? (
                <motion.div
                  key="read"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.25 }}
                >
                  <motion.div
                    className={styles.fieldsGrid}
                    variants={staggerContainer}
                    initial="hidden"
                    animate="visible"
                  >
                    <ReadField label="First Name" value={profile.first_name} />
                    <ReadField label="Last Name" value={profile.last_name} />
                    <ReadField label="Middle Name" value={profile.middle_name} />
                    <ReadField label="Location" value={profile.location} />
                    <ReadField label="Interests" value={profile.interests?.join(', ')} full />
                    <ReadField label="About" value={profile.bio} full />
                  </motion.div>
                </motion.div>
              ) : (
                <motion.div
                  key="edit"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.25 }}
                >
                  <div className={styles.editForm}>
                    <div className={styles.editGrid}>
                      <FloatingInput
                        id="first_name"
                        label="First Name"
                        value={form.first_name ?? ''}
                        onChange={(v) => setForm((f) => ({ ...f, first_name: v }))}
                      />
                      <FloatingInput
                        id="last_name"
                        label="Last Name"
                        value={form.last_name ?? ''}
                        onChange={(v) => setForm((f) => ({ ...f, last_name: v }))}
                      />
                      <FloatingInput
                        id="middle_name"
                        label="Middle Name"
                        value={form.middle_name ?? ''}
                        onChange={(v) => setForm((f) => ({ ...f, middle_name: v }))}
                      />
                      <FloatingInput
                        id="location"
                        label="Location"
                        value={form.location ?? ''}
                        onChange={(v) => setForm((f) => ({ ...f, location: v }))}
                      />
                      <div className={styles.editFull}>
                        <TagInput
                          id="interests"
                          label="Interests"
                          tags={form.interests ?? []}
                          onChange={(tags) => setForm((f) => ({ ...f, interests: tags }))}
                        />
                      </div>
                      <div className={styles.editFull}>
                        <FloatingTextarea
                          id="bio"
                          label="About"
                          value={form.bio ?? ''}
                          onChange={(v) => setForm((f) => ({ ...f, bio: v }))}
                          maxLength={1000}
                        />
                      </div>
                    </div>

                    <motion.div
                      className={styles.formActions}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.3 }}
                    >
                      <Button variant="ghost" onClick={handleCancel}>
                        Cancel
                      </Button>
                      <Button variant="primary" isLoading={saving} onClick={handleSave}>
                        Save changes
                      </Button>
                    </motion.div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </>
        )}
      </div>
    </MainLayout>
  );
}