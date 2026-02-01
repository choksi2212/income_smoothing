import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from './store/authStore';
import { useTheme } from './hooks/useTheme';
import { authAPI } from './services/api';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import IncomeBreakdown from './pages/IncomeBreakdown';
import IncomeSmoothing from './pages/IncomeSmoothing';
import Insights from './pages/Insights';
import ManualEntry from './pages/ManualEntry';
import Layout from './components/Layout';

function App() {
  const { isAuthenticated, setUser } = useAuthStore();
  const { theme } = useTheme();

  useEffect(() => {
    if (isAuthenticated) {
      authAPI.getCurrentUser()
        .then(setUser)
        .catch(() => useAuthStore.getState().logout());
    }
  }, [isAuthenticated, setUser]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />
        <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/" />} />
        
        <Route element={isAuthenticated ? <Layout /> : <Navigate to="/login" />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/income" element={<IncomeBreakdown />} />
          <Route path="/smoothing" element={<IncomeSmoothing />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="/manual-entry" element={<ManualEntry />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
