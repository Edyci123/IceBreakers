import type { AppError } from './apiClient';

export function getErrorMessage(error: unknown): string {
  if (!error) return 'Something went wrong. Please try again later.';

  // If it's not an AppError object (e.g. standard Error), return its message or generic
  const appError = error as AppError;
  if (!appError.status) {
    return (error as Error).message || 'An unexpected error occurred.';
  }

  // Handle FastAPI detail array (422 validation errors)
  if (appError.detail && Array.isArray(appError.detail)) {
    for (const err of appError.detail) {
      const loc: string = err?.loc?.[err.loc.length - 1] ?? '';
      // CSRF errors should never be shown as raw field names
      if (loc === 'x-csrf-token') {
        return 'Your session token is missing or expired. Please refresh the page and try again.';
      }
    }
    // Generic validation fallback — don't expose raw Pydantic field names
    return 'Some fields are invalid. Please check your input and try again.';
  }

  // Handle FastAPI detail string
  if (appError.detail && typeof appError.detail === 'string') {
    return appError.detail;
  }

  // Fallback to HTTP status codes
  switch (appError.status) {
    case 400: return 'Invalid data provided.';
    case 401: return 'Session expired, please sign in again.';
    case 403: return "You don't have permission to do this.";
    case 404: return 'Resource not found.';
    case 409: return 'This resource already exists or there is a conflict.';
    case 422: return 'Validation error, please check your inputs.';
    case 500: return 'Something went wrong on our end. Please try again later.';
    default: return appError.message || 'An unexpected network error occurred.';
  }
}
