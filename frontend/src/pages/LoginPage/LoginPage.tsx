import React, { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../features/auth/useAuth';
import AuthLayout from '../../components/layout/AuthLayout';
import { FloatingInput, Button } from '../../components/ui';
import { Alert } from '../../components/feedback';
import { getErrorMessage } from '../../lib/errorMessages';
import styles from './LoginPage.module.css';

interface FormState {
  email: string;
  password: string;
}

interface Errors {
  email?: string;
  password?: string;
}

interface Touched {
  email?: boolean;
  password?: boolean;
}

function validate(form: FormState): Errors {
  const errors: Errors = {};
  if (!form.email) errors.email = 'Email is required';
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errors.email = 'Enter a valid email address';
  if (!form.password) errors.password = 'Password is required';
  else if (form.password.length < 8) errors.password = 'Password must be at least 8 characters';
  return errors;
}

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>({ email: '', password: '' });
  const [touched, setTouched] = useState<Touched>({});
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

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
    setTouched({ email: true, password: true });
    if (!isValid) return;

    setLoading(true);
    setServerError(null);
    try {
      await login({ email: form.email, password: form.password });
      navigate('/profile', { replace: true });
    } catch (err) {
      setServerError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const fields = [
    { id: 'email', label: 'Email address', type: 'email', field: 'email' as const },
    { id: 'password', label: 'Password', type: 'password', field: 'password' as const },
  ];

  return (
    <AuthLayout>
      <div className={styles.formWrapper}>
        <h2 className={styles.title}>Welcome back</h2>
        <p className={styles.subtitle}>Sign in to your account</p>

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
              transition={{ delay: i * 0.08, duration: 0.35 }}
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
                autoComplete={type === 'email' ? 'email' : 'current-password'}
              />
            </motion.div>
          ))}

          <div className={styles.forgotRow}>
            <a href="#" className={styles.forgotLink}>Forgot password?</a>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={loading}
            className={styles.submitBtn}
          >
            Sign in
          </Button>
        </form>

        <div className={styles.divider}>
          <span>or</span>
        </div>

        <p className={styles.switchText}>
          Don't have an account?{' '}
          <Link to="/register">Create one</Link>
        </p>
      </div>
    </AuthLayout>
  );
}