// Notification utilities for Elektron app

export const requestNotificationPermission = async () => {
  if (!('Notification' in window)) {
    console.log('This browser does not support notifications');
    return false;
  }

  if (Notification.permission === 'granted') {
    return true;
  }

  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }

  return false;
};

export const showNotification = async (title, options = {}) => {
  console.log('showNotification called:', title);
  console.log('Notification.permission:', Notification.permission);
  
  if (Notification.permission !== 'granted') {
    console.warn('Notification permission not granted. Requesting...');
    const permission = await Notification.requestPermission();
    console.log('Permission result:', permission);
    if (permission !== 'granted') {
      alert('Powiadomienia są zablokowane. Włącz je w ustawieniach przeglądarki.');
      return false;
    }
  }

  // Check if running as standalone PWA
  const isStandalone = window.matchMedia('(display-mode: standalone)').matches || 
                       window.navigator.standalone === true;
  console.log('Is standalone PWA:', isStandalone);

  if (!('serviceWorker' in navigator)) {
    console.error('Service Worker not supported');
    alert('Ta przeglądarka nie obsługuje powiadomień');
    return false;
  }

  try {
    console.log('Getting SW registration...');
    let registration = await navigator.serviceWorker.getRegistration();
    
    // If no registration, wait for it
    if (!registration) {
      console.log('No registration found, waiting for ready...');
      registration = await navigator.serviceWorker.ready;
    }
    
    console.log('SW Registration:', registration);
    console.log('SW Active:', registration?.active);
    console.log('SW Installing:', registration?.installing);
    console.log('SW Waiting:', registration?.waiting);
    
    if (!registration) {
      throw new Error('Service Worker nie jest zarejestrowany');
    }
    
    // Use Service Worker notification
    await registration.showNotification(title, {
      icon: '/icon-192.png',
      badge: '/icon-192.png',
      vibrate: [200, 100, 200],
      tag: options.tag || 'elektron-notification',
      requireInteraction: false,
      body: options.body || '',
      data: options.data || {},
    });
    
    console.log('✅ Notification shown via SW!');
    return true;
    
  } catch (error) {
    console.error('❌ Error showing notification:', error);
    
    // Only use fallback on desktop browser (not PWA)
    if (!isStandalone && typeof Notification !== 'undefined') {
      try {
        console.log('Trying direct notification fallback...');
        const notification = new Notification(title, {
          icon: '/icon-192.png',
          body: options.body || '',
        });
        setTimeout(() => notification.close(), 10000);
        console.log('✅ Direct notification shown!');
        return true;
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
      }
    }
    
    alert(`Błąd powiadomienia: ${error.message}\n\nSpróbuj odinstalować i zainstalować aplikację ponownie.`);
    return false;
  }
};

export const scheduleProjectReminder = (project) => {
  if (!project || !project.start_date) return;

  const projectDate = new Date(project.start_date);
  const now = new Date();
  const tomorrow = new Date(now);
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(8, 0, 0, 0);

  // If project starts tomorrow, schedule a reminder
  if (
    projectDate.toDateString() === tomorrow.toDateString() ||
    projectDate.toDateString() === now.toDateString()
  ) {
    const clientName = project.client?.name || 'klienta';
    showNotification('Przypomnienie o zleceniu ⚡', {
      body: `Dziś/jutro masz zlecenie: ${project.title} u ${clientName}`,
      tag: `project-${project.id}`,
      requireInteraction: true,
      data: {
        url: '/projects',
        projectId: project.id,
      },
    });
  }
};

export const checkUpcomingProjects = async () => {
  try {
    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
    const response = await fetch(`${BACKEND_URL}/api/projects`);
    const projects = await response.json();

    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);

    projects.forEach((project) => {
      if (project.status === 'in_progress' || project.status === 'new') {
        scheduleProjectReminder(project);
      }
    });
  } catch (error) {
    console.error('Error checking upcoming projects:', error);
  }
};

// Check for reminders every hour
export const startReminderService = () => {
  checkUpcomingProjects(); // Check immediately
  setInterval(checkUpcomingProjects, 60 * 60 * 1000); // Check every hour
};

// Schedule daily report reminder at 18:00
export const scheduleDailyReportReminder = () => {
  const checkTime = () => {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    
    // Trigger at 18:00 (6 PM)
    if (hours === 18 && minutes === 0) {
      showNotification('Zrób raport dzienny 📝', {
        body: 'Czas na zapisanie raportu z dzisiejszego dnia pracy!',
        tag: 'daily-report-reminder',
        requireInteraction: true,
        data: {
          url: '/reports/voice',
        },
        actions: [
          {
            action: 'open-voice',
            title: 'Nagraj raport'
          },
          {
            action: 'dismiss',
            title: 'Przypomnij później'
          }
        ]
      });
    }
  };
  
  // Check every minute
  checkTime(); // Check immediately
  setInterval(checkTime, 60 * 1000); // Check every minute
};

// Check for pending reminders from backend
export const checkPendingReminders = async () => {
  console.log('🔍 Checking pending reminders...');
  try {
    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
    const response = await fetch(`${BACKEND_URL}/api/reminders/check/pending`);
    const data = await response.json();

    console.log('Pending reminders response:', data);

    if (data.reminders && data.reminders.length > 0) {
      console.log(`📬 Found ${data.count} pending reminders`);
      
      for (const reminder of data.reminders) {
        await showNotification(reminder.title, {
          body: reminder.description || 'Przypomnienie',
          tag: `reminder-${reminder.id}`,
          requireInteraction: true,
          data: {
            url: '/reminders',
            reminderId: reminder.id,
          },
        });
      }
      
      console.log(`✅ Sent ${data.count} reminder notifications`);
    } else {
      console.log('No pending reminders at this time');
    }
  } catch (error) {
    console.error('❌ Error checking pending reminders:', error);
  }
};

// Start reminder checking service - checks every 5 minutes
export const startRemindersCheckService = () => {
  checkPendingReminders(); // Check immediately
  setInterval(checkPendingReminders, 5 * 60 * 1000); // Check every 5 minutes
};
