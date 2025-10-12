import { useState, useEffect } from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { Users, Briefcase, Clock, LayoutDashboard, Zap, Wifi, WifiOff, Calculator, Camera, FileText, Mail } from 'lucide-react';

const Layout = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/clients', icon: Users, label: 'Klienci' },
    { to: '/projects', icon: Briefcase, label: 'Zlecenia' },
    { to: '/workhours', icon: Clock, label: 'Godziny pracy' },
    { to: '/reports', icon: FileText, label: 'Raporty' },
    { to: '/mail', icon: Mail, label: 'Poczta' },
    { to: '/calculators', icon: Calculator, label: 'Kalkulatory' },
    { to: '/photos', icon: Camera, label: 'Zdjęcia' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <img src="/logo.png" alt="Elektron Logo" className="h-12 w-auto" />
              <h1 className="text-2xl font-bold text-gray-900">Elektron</h1>
            </div>
            <div className="flex items-center space-x-2">
              {isOnline ? (
                <div className="flex items-center space-x-2 text-green-600 text-sm">
                  <Wifi className="h-4 w-4" />
                  <span className="hidden sm:inline">Online</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2 text-orange-600 text-sm font-medium bg-orange-50 px-3 py-1 rounded-full">
                  <WifiOff className="h-4 w-4" />
                  <span>Tryb offline</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="flex max-w-7xl mx-auto">
        {/* Sidebar Navigation */}
        <aside className="w-64 bg-white border-r border-gray-200 min-h-[calc(100vh-4rem)] sticky top-16">
          <nav className="p-4 space-y-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-yellow-50 text-yellow-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`
                }
              >
                <item.icon className="h-5 w-5" />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
