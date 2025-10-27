import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Bell, Check, Trash2, AlertCircle, Info, AlertTriangle, ExternalLink } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, unread, read

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const response = await axios.get(`${API}/api/notifications`);
      setNotifications(response.data);
    } catch (error) {
      console.error('Błąd ładowania powiadomień:', error);
      toast.error('Nie udało się załadować powiadomień');
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (id) => {
    try {
      await axios.put(`${API}/api/notifications/${id}/read`);
      loadNotifications();
    } catch (error) {
      toast.error('Nie udało się oznaczyć jako przeczytane');
    }
  };

  const deleteNotification = async (id) => {
    try {
      await axios.delete(`${API}/api/notifications/${id}`);
      toast.success('Powiadomienie usunięte');
      loadNotifications();
    } catch (error) {
      toast.error('Nie udało się usunąć powiadomienia');
    }
  };

  const deleteAllNotifications = async () => {
    if (!window.confirm('Usunąć wszystkie powiadomienia?')) return;
    
    try {
      await axios.delete(`${API}/api/notifications/all`);
      toast.success('Wszystkie powiadomienia usunięte');
      loadNotifications();
    } catch (error) {
      toast.error('Nie udało się usunąć powiadomień');
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'high':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      case 'medium':
        return <AlertTriangle className="h-5 w-5 text-orange-600" />;
      default:
        return <Info className="h-5 w-5 text-blue-600" />;
    }
  };

  const getPriorityBadge = (priority) => {
    const colors = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-orange-100 text-orange-800',
      low: 'bg-blue-100 text-blue-800',
    };
    const labels = {
      high: 'Wysoki',
      medium: 'Średni',
      low: 'Niski',
    };
    return <Badge className={colors[priority]}>{labels[priority]}</Badge>;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Przed chwilą';
    if (diffMins < 60) return `${diffMins} min temu`;
    if (diffHours < 24) return `${diffHours}h temu`;
    if (diffDays < 7) return `${diffDays} dni temu`;
    
    return new Intl.DateTimeFormat('pl-PL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'unread') return !n.read;
    if (filter === 'read') return n.read;
    return true;
  });

  const unreadCount = notifications.filter(n => !n.read).length;

  if (loading) {
    return <div className="text-center py-12">Ładowanie...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Bell className="h-8 w-8 text-purple-600" />
            Centrum Powiadomień
            {unreadCount > 0 && (
              <Badge className="bg-red-600 text-white">{unreadCount}</Badge>
            )}
          </h2>
          <p className="text-gray-600 mt-1">Wszystkie powiadomienia w jednym miejscu</p>
        </div>
        {notifications.length > 0 && (
          <Button onClick={deleteAllNotifications} variant="outline" className="text-red-600">
            <Trash2 className="h-4 w-4 mr-2" />
            Usuń wszystkie
          </Button>
        )}
      </div>

      {/* Webhook Info Card */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center">
            <ExternalLink className="h-5 w-5 mr-2 text-blue-600" />
            Webhook Endpoint - Odbieraj Powiadomienia z Innych Aplikacji
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-semibold text-gray-700">URL:</label>
              <code className="block mt-1 p-3 bg-white rounded border text-sm">
                POST {API}/api/notifications
              </code>
            </div>
            <div>
              <label className="text-sm font-semibold text-gray-700">Przykład JSON:</label>
              <pre className="block mt-1 p-3 bg-white rounded border text-xs overflow-x-auto">
{`{
  "title": "Nowe zamówienie",
  "message": "Klient Jan Kowalski złożył zamówienie",
  "source": "Sklep Online",
  "priority": "high"
}`}
              </pre>
            </div>
            <p className="text-sm text-gray-600">
              💡 Użyj tego endpointu w Zapier, n8n lub innej aplikacji aby wysyłać powiadomienia do Elektron!
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Filters */}
      <Tabs value={filter} onValueChange={setFilter} className="w-full">
        <TabsList>
          <TabsTrigger value="all">
            Wszystkie ({notifications.length})
          </TabsTrigger>
          <TabsTrigger value="unread">
            Nieprzeczytane ({unreadCount})
          </TabsTrigger>
          <TabsTrigger value="read">
            Przeczytane ({notifications.length - unreadCount})
          </TabsTrigger>
        </TabsList>

        <TabsContent value={filter} className="mt-6">
          {filteredNotifications.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <Bell className="h-16 w-16 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600 text-lg mb-2">Brak powiadomień</p>
                <p className="text-gray-500 text-sm">
                  {filter === 'unread' && 'Wszystkie powiadomienia są przeczytane'}
                  {filter === 'read' && 'Brak przeczytanych powiadomień'}
                  {filter === 'all' && 'Nie masz jeszcze żadnych powiadomień'}
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {filteredNotifications.map(notification => (
                <Card key={notification.id} className={`hover:shadow-lg transition-shadow ${notification.read ? 'bg-gray-50' : 'bg-white border-2 border-purple-200'}`}>
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      <div className="mt-1">
                        {getPriorityIcon(notification.priority)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className="font-semibold text-lg">{notification.title}</h3>
                              {!notification.read && (
                                <Badge className="bg-purple-600 text-white text-xs">NOWE</Badge>
                              )}
                            </div>
                            <p className="text-gray-700">{notification.message}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3 text-sm text-gray-500">
                          <span className="flex items-center gap-1">
                            <span className="font-medium">Źródło:</span> {notification.source}
                          </span>
                          <span>•</span>
                          {getPriorityBadge(notification.priority)}
                          <span>•</span>
                          <span>{formatDate(notification.created_at)}</span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {!notification.read && (
                          <Button
                            onClick={() => markAsRead(notification.id)}
                            variant="outline"
                            size="sm"
                            title="Oznacz jako przeczytane"
                          >
                            <Check className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          onClick={() => deleteNotification(notification.id)}
                          variant="ghost"
                          size="sm"
                          className="text-red-600 hover:text-red-700"
                          title="Usuń"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Notifications;
