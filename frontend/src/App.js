import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import './App.css';
import Dashboard from './pages/Dashboard';
import Clients from './pages/Clients';
import Projects from './pages/Projects';
import WorkHours from './pages/WorkHours';
import Calculators from './pages/Calculators';
import Layout from './components/Layout';
import InstallPWA from './components/InstallPWA';
import { requestNotificationPermission, startReminderService } from './utils/notifications';

function App() {
  useEffect(() => {
    // Request notification permission after 5 seconds
    const timer = setTimeout(() => {
      requestNotificationPermission().then((granted) => {
        if (granted) {
          console.log('Notifications enabled');
          // Start reminder service for upcoming projects
          startReminderService();
        }
      });
    }, 5000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="clients" element={<Clients />} />
            <Route path="projects" element={<Projects />} />
            <Route path="workhours" element={<WorkHours />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
      <InstallPWA />
    </>
  );
}

export default App;
