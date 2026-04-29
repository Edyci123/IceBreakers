import React, { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import { useAuth } from '../../features/auth/useAuth';
import AuthLayout from '../../components/layout/AuthLayout';
import { FloatingInput, Button } from '../../components/ui';
import { Alert } from '../../components/feedback';
import { getErrorMessage } from '../../lib/errorMessages';
import styles from './RegisterPage.module.css';

interface FormState {
  fullName: string;
  email: string;
  password: string;
  confirmPassword: string;
}

interface Errors {
  fullName?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
}

type Touched = Partial<Record<keyof FormState, boolean>>;

function validate(form: FormState): Errors {
  const errors: Errors = {};
  if (!form.fullName || form.fullName.trim().length < 2) errors.fullName = 'Full name must be at least 2 characters';
  if (!form.email) errors.email = 'Email is required';
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errors.email = 'Enter a valid email address';
  if (!form.password) errors.password = 'Password is required';
  else if (form.password.length < 8) errors.password = 'Password must be at least 8 characters';
  if (!form.confirmPassword) errors.confirmPassword = 'Please confirm your password';
  else if (form.password !== form.confirmPassword) errors.confirmPassword = 'Passwords do not match';
  return errors;
}

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const prefersReduced = useReducedMotion();

  const [form, setForm] = useState<FormState>({ fullName: '', email: '', password: '', confirmPassword: '' });
  const [touched, setTouched] = useState<Touched>({});
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const errors = validate(form);
  const isValid = Object.keys(errors).length === 0;

  const handleChange = (field: keyof FormState) => (value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setServerError(null);
  };

  const handleBlur = (field: keyof FormState) => () => {
    setTouched((prev) => ({ ...prev, [field]: true }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setTouched({ fullName: true, email: true, password: true, confirmPassword: true });
    if (!isValid) return;

    setLoading(true);
    setServerError(null);
    try {
      await register({ email: form.email, password: form.password, full_name: form.fullName });
      setSuccess(true);
      setTimeout(() => navigate('/login', { replace: true }), 2200);
    } catch (err) {
      setServerError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const fields: { id: string; label: string; type: string; field: keyof FormState }[] = [
    { id: 'fullName', label: 'Full Name', type: 'text', field: 'fullName' },
    { id: 'email', label: 'Email address', type: 'email', field: 'email' },
    { id: 'password', label: 'Password', type: 'password', field: 'password' },
    { id: 'confirmPassword', label: 'Confirm password', type: 'password', field: 'confirmPassword' },
  ];

  if (success) {
    return (
      <AuthLayout>
        <motion.div
          className={styles.successState}
          initial={prefersReduced ? false : { scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
        >
          <div className={styles.checkIcon}>✓</div>
          <h3 className={styles.successTitle}>Account created!</h3>
          <p className={styles.successSub}>Redirecting to sign in…</p>
          <div className={styles.progressBarTrack}>
            <motion.div
              className={styles.progressBar}
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 2, ease: 'linear' }}
              style={{ transformOrigin: 'left' }}
            />
          </div>
        </motion.div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout>
      <div className={styles.formWrapper}>
        <h2 className={styles.title}>Create your account</h2>
        <p className={styles.subtitle}>Join IceBreakers today</p>

        <AnimatePresence>
          {serverError && (
            <Alert type="error" message={serverError} onDismiss={() => setServerError(null)} />
          )}
        </AnimatePresence>

        <form className={styles.form} onSubmit={handleSubmit} noValidate>
          {fields.map(({ id, label, type, field }, i) => (
            <motion.div
              key={id}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.07, duration: 0.35 }}
            >
              <FloatingInput
                id={id}
                label={label}
                type={type}
                value={form[field]}
                onChange={handleChange(field)}
                onBlur={handleBlur(field)}
                error={errors[field]}
                touched={touched[field]}
              />
            </motion.div>
          ))}

          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={loading}
            className={styles.submitBtn}
          >
            Create account
          </Button>
        </form>

        <p className={styles.switchText}>
          Already have an account?{' '}
          <Link to="/login">Sign in</Link>
        </p>
      </div>
    </AuthLayout>
  );
}