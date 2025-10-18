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

export const showNotification = (title, options = {}) => {
  if (Notification.permission === 'granted') {
    if ('serviceWorker' in navigator) {
      // Always use service worker for PWA
      navigator.serviceWorker.ready.then((registration) => {
        registration.showNotification(title, {
          icon: '/icon-192.png',
          badge: '/icon-192.png',
          vibrate: [200, 100, 200],
          ...options,
        });
      }).catch((error) => {
        console.error('Error showing notification:', error);
      });
    } else {
      console.warn('Service Worker not available - notifications may not work');
    }
  } else {
    console.warn('Notification permission not granted');
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
  try {
    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
    const response = await fetch(`${BACKEND_URL}/api/reminders/check/pending`);
    const data = await response.json();

    if (data.reminders && data.reminders.length > 0) {
      data.reminders.forEach((reminder) => {
        showNotification(reminder.title, {
          body: reminder.description || 'Przypomnienie',
          tag: `reminder-${reminder.id}`,
          requireInteraction: true,
          data: {
            url: '/reminders',
            reminderId: reminder.id,
          },
        });
      });
      console.log(`Sent ${data.count} reminder notifications`);
    }
  } catch (error) {
    console.error('Error checking pending reminders:', error);
  }
};

// Start reminder checking service - checks every 5 minutes
export const startRemindersCheckService = () => {
  checkPendingReminders(); // Check immediately
  setInterval(checkPendingReminders, 5 * 60 * 1000); // Check every 5 minutes
};
