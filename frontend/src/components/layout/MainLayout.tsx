import React, { useState, useEffect, ReactNode } from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../../features/auth/useAuth';
import MeshBackground from './MeshBackground';
import styles from './MainLayout.module.css';

interface MainLayoutProps {
  children: ReactNode;
}

function Logo() {
  return (
    <Link to="/" className={styles.logo}>
      IceBreakers
    </Link>
  );
}

function UserChip({ email }: { email?: string }) {
  const initial = email ? email[0].toUpperCase() : '?';
  return (
    <div className={styles.userChip}>
      <div className={styles.avatar}>{initial}</div>
      <span className={styles.email}>{email}</span>
    </div>
  );
}

export default function MainLayout({ children }: MainLayoutProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  return (
    <>
      <MeshBackground />
      <div className={styles.root}>
        <motion.header
          className={styles.header}
          data-scrolled={scrolled}
          initial={{ y: -64 }}
          animate={{ y: 0 }}
          transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className={styles.headerInner}>
            <Logo />
            <nav className={styles.nav}>
              <NavLink
                to="/profile"
                className={({ isActive }) =>
                  isActive ? `${styles.navLink} ${styles.navLinkActive}` : styles.navLink
                }
              >
                Profile
              </NavLink>
            </nav>
            <div className={styles.headerRight}>
              <UserChip email={user?.email} />
              <button className={styles.logoutBtn} onClick={handleLogout}>
                Sign out
              </button>
            </div>
          </div>
        </motion.header>

        <main className={styles.main}>
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
          >
            {children}
          </motion.div>
        </main>
      </div>
    </>
  );
}