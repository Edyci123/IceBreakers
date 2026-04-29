import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../features/auth/useAuth';
import { Spinner } from '../components/feedback';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isInitialized } = useAuth();

  if (!isInitialized) {
    return <Spinner fullPage />;
  }

  if (user === null) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
