import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import './App.css';
import Dashboard from './pages/Dashboard';
import Clients from './pages/Clients';
import Projects from './pages/Projects';
import WorkHours from './pages/WorkHours';
import Calculators from './pages/Calculators';
import Photos from './pages/Photos';
import Reports from './pages/Reports';
import VoiceReport from './pages/VoiceReport';
import Mail from './pages/Mail';
import AIAssistant from './pages/AIAssistant';
import Employees from './pages/Employees';
import Finances from './pages/Finances';
import Reminders from './pages/Reminders';
import Layout from './components/Layout';
import InstallPWA from './components/InstallPWA';
import { requestNotificationPermission, startReminderService, scheduleDailyReportReminder } from './utils/notifications';

function App() {
  useEffect(() => {
    // Request notification permission after 5 seconds
    const timer = setTimeout(() => {
      requestNotificationPermission().then((granted) => {
        if (granted) {
          console.log('Notifications enabled');
          // Start reminder service for upcoming projects
          startReminderService();
          // Schedule daily report reminder at 18:00
          scheduleDailyReportReminder();
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
            <Route path="calculators" element={<Calculators />} />
            <Route path="photos" element={<Photos />} />
            <Route path="reports" element={<Reports />} />
            <Route path="reports/voice" element={<VoiceReport />} />
            <Route path="mail" element={<Mail />} />
            <Route path="ai-assistant" element={<AIAssistant />} />
            <Route path="employees" element={<Employees />} />
            <Route path="finances" element={<Finances />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
      <InstallPWA />
    </>
  );
}

export default App;
