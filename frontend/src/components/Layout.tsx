import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Home, TrendingUp, Repeat, Lightbulb, LogOut, Edit } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { useTheme } from '../hooks/useTheme';
import styles from './Layout.module.css';

const Layout = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const { theme } = useTheme();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar}>
        <div className={styles.logo}>
          <h1>Income Smoothing</h1>
        </div>
        
        <nav className={styles.nav}>
          <NavLink to="/" className={({ isActive }) => isActive ? styles.navLinkActive : styles.navLink}>
            <Home size={20} />
            <span>Dashboard</span>
          </NavLink>
          
          <NavLink to="/income" className={({ isActive }) => isActive ? styles.navLinkActive : styles.navLink}>
            <TrendingUp size={20} />
            <span>Income Breakdown</span>
          </NavLink>
          
          <NavLink to="/smoothing" className={({ isActive }) => isActive ? styles.navLinkActive : styles.navLink}>
            <Repeat size={20} />
            <span>Income Smoothing</span>
          </NavLink>
          
          <NavLink to="/insights" className={({ isActive }) => isActive ? styles.navLinkActive : styles.navLink}>
            <Lightbulb size={20} />
            <span>Insights</span>
          </NavLink>
          
          <NavLink to="/manual-entry" className={({ isActive }) => isActive ? styles.navLinkActive : styles.navLink}>
            <Edit size={20} />
            <span>Manual Entry</span>
          </NavLink>
        </nav>
        
        <div className={styles.userSection}>
          <div className={styles.userInfo}>
            <div className={styles.userName}>{user?.full_name}</div>
            <div className={styles.userEmail}>{user?.email}</div>
          </div>
          <button onClick={handleLogout} className={styles.logoutBtn}>
            <LogOut size={18} />
          </button>
        </div>
      </aside>
      
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
