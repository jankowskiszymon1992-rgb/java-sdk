import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { X, Download } from 'lucide-react';

const InstallPWA = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);

  useEffect(() => {
    const handler = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      
      // Show install prompt if not installed and not dismissed recently
      const dismissed = localStorage.getItem('pwa-install-dismissed');
      const dismissedTime = dismissed ? parseInt(dismissed) : 0;
      const dayInMs = 24 * 60 * 60 * 1000;
      
      if (!dismissed || Date.now() - dismissedTime > dayInMs) {
        setShowInstallPrompt(true);
      }
    };

    window.addEventListener('beforeinstallprompt', handler);

    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setShowInstallPrompt(false);
    }

    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    console.log(`User response to install prompt: ${outcome}`);
    setDeferredPrompt(null);
    setShowInstallPrompt(false);
  };

  const handleDismiss = () => {
    localStorage.setItem('pwa-install-dismissed', Date.now().toString());
    setShowInstallPrompt(false);
  };

  if (!showInstallPrompt) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:max-w-sm z-50 animate-in slide-in-from-bottom-5">
      <div className="bg-gradient-to-r from-yellow-400 to-yellow-500 text-gray-900 rounded-lg shadow-2xl p-4">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center space-x-2">
            <Download className="h-5 w-5" />
            <h3 className="font-bold text-lg">Zainstaluj Elektron</h3>
          </div>
          <button
            onClick={handleDismiss}
            className="text-gray-700 hover:text-gray-900"
            aria-label="Zamknij"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <p className="text-sm mb-3 text-gray-800">
          Zainstaluj aplikację na swoim urządzeniu i korzystaj jak z normalnej aplikacji!
        </p>
        <div className="flex space-x-2">
          <Button
            onClick={handleInstall}
            className="flex-1 bg-gray-900 hover:bg-gray-800 text-white"
            size="sm"
          >
            Zainstaluj
          </Button>
          <Button
            onClick={handleDismiss}
            variant="outline"
            className="bg-white/20 hover:bg-white/30 border-gray-800"
            size="sm"
          >
            Później
          </Button>
        </div>
      </div>
    </div>
  );
};

export default InstallPWA;
