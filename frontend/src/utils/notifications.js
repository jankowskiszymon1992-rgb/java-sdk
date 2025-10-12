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
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      // Use service worker to show notification (works even when app is closed)
      navigator.serviceWorker.ready.then((registration) => {
        registration.showNotification(title, {
          icon: '/icon-192.png',
          badge: '/icon-192.png',
          vibrate: [200, 100, 200],
          ...options,
        });
      });
    } else {
      // Fallback to direct notification
      new Notification(title, {
        icon: '/icon-192.png',
        ...options,
      });
    }
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
