## 1. Overview
Sprint 1 establishes the authentication and profile foundation for IceBreakers. The frontend exposes these backend capabilities via a simple and clear web interface. We successfully integrated a secure, HttpOnly cookie-based session strategy for login and registration, and a complete UI for reading and updating user profiles.

## 2. Tech Stack
- React
- TypeScript
- Vite
- React Router
- Axios
- Vitest
- CSS Modules

## 3. Project Structure
```
frontend/src/
├── app/               # Root routing, route guards, and App entry point
├── components/        # Reusable UI (Alert, Spinner) and global Layouts (MainLayout, AuthLayout)
├── features/          # Domain features containing API wrappers, types, and Contexts (auth, profile)
├── lib/               # Global utilities (Axios apiClient, config, errorMessages)
├── pages/             # Route level components (LoginPage, RegisterPage, ProfilePage)
├── styles/            # Global CSS variables and design tokens (tokens.css)
├── test/              # Vitest setup scripts
└── main.tsx           # React DOM rendering entry point
```

## 4. Running the Frontend
1. Ensure you have Node.js version 20+ and npm installed.
2. Install dependencies: `npm install`
3. Start the dev server: `npm run dev` (Available at http://localhost:5173)
4. Ensure the backend is running at http://localhost:8000
5. Build for production: `npm run build`

## 5. Backend API Contract
All endpoints are accessed via the `/api` prefix, seamlessly proxied by Vite in development.

| Method | Path | Request Shape | Response Shape |
|--------|------|---------------|----------------|
| POST | `/api/auth/register` | `{ email, password, full_name }` | `UserResponse` (sets HttpOnly cookie) |
| POST | `/api/auth/login` | `{ email, password }` | `UserResponse` (sets HttpOnly cookie) |
| GET | `/api/auth/me` | None | `UserResponse` |
| GET | `/api/profile` | None | `UserProfile` |
| PUT | `/api/profile` | `UpdateProfileRequest` | `UserProfile` |

*Note: The actual shapes match exactly with `icebreakers/auth/domain/schemas.py` and `icebreakers/profile/domain/schemas.py`.*

## 6. Auth Flow
We use a **Secure HttpOnly Cookie** strategy.
- **Login/Register:** On successful login or registration, the backend sets an `HttpOnly` cookie containing the session JWT. We do not store tokens in `localStorage`.
- **Session Persistence:** On app mount, `AuthContext` calls `/api/auth/me`. Because Axios is configured with `withCredentials: true`, the cookie is sent automatically. If valid, the user is authenticated.
- **401 Handling:** The Axios interceptor listens for `401 Unauthorized`. If triggered, it dispatches an `auth:unauthorized` event which logs the user out globally and redirects to `/login`.
- **Logout:** Clears the cookie on the backend via `/api/auth/logout`.

## 7. Environment Variables
- `VITE_API_BASE_URL` — Optional, defaults to `/api`. Vite automatically proxies `/api` requests to `http://localhost:8000`.

## 8. Running Tests
- Run all unit tests: `npm test`

## 9. Known Limitations / TODOs for Sprint 2
- No SSO support yet (architecture-ready).
- No matching/meeting pages yet.
- Interests field is stored as a comma-separated string locally before converting to an array (Sprint 2: convert to tag/array UI).
- No password reset flow.
- The `vite.config.ts` proxy rewrite might need adjusting if the backend changes its `/api` prefix requirements.
