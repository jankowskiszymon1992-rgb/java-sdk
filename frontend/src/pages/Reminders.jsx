import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Bell, Plus, Edit2, Trash2, Check, Calendar, Clock, RefreshCw, Send } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';
import { showNotification, checkPendingReminders } from '../utils/notifications';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Reminders = () => {
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [reminderToDelete, setReminderToDelete] = useState(null);
  const [editingReminder, setEditingReminder] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    reminder_date: new Date().toISOString().split('T')[0],
    reminder_time: '09:00',
    is_recurring: false
  });

  useEffect(() => {
    loadReminders();
  }, []);

  const loadReminders = async () => {
    try {
      const response = await axios.get(`${API}/reminders`);
      setReminders(response.data);
    } catch (error) {
      console.error('Błąd ładowania przypomnień:', error);
      toast.error('Nie udało się załadować przypomnień');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (editingReminder) {
        await axios.put(`${API}/reminders/${editingReminder.id}`, formData);
        toast.success('Przypomnienie zaktualizowane');
      } else {
        await axios.post(`${API}/reminders`, formData);
        toast.success('Przypomnienie dodane');
      }
      
      setDialogOpen(false);
      resetForm();
      loadReminders();
    } catch (error) {
      console.error('Błąd zapisywania przypomnienia:', error);
      toast.error('Nie udało się zapisać przypomnienia');
    }
  };

  const handleEdit = (reminder) => {
    setEditingReminder(reminder);
    setFormData({
      title: reminder.title,
      description: reminder.description || '',
      reminder_date: reminder.reminder_date,
      reminder_time: reminder.reminder_time,
      is_recurring: reminder.is_recurring
    });
    setDialogOpen(true);
  };

  const handleDelete = (id) => {
    setReminderToDelete(id);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (reminderToDelete) {
      try {
        await axios.delete(`${API}/reminders/${reminderToDelete}`);
        toast.success('Przypomnienie usunięte');
        loadReminders();
      } catch (error) {
        console.error('Błąd usuwania przypomnienia:', error);
        toast.error('Nie udało się usunąć przypomnienia');
      } finally {
        setDeleteDialogOpen(false);
        setReminderToDelete(null);
      }
    }
  };

  const handleToggleComplete = async (reminder) => {
    try {
      await axios.put(`${API}/reminders/${reminder.id}`, {
        is_completed: !reminder.is_completed
      });
      toast.success(reminder.is_completed ? 'Oznaczono jako nieukończone' : 'Oznaczono jako ukończone');
      loadReminders();
    } catch (error) {
      console.error('Błąd aktualizacji przypomnienia:', error);
      toast.error('Nie udało się zaktualizować');
    }
  };

  const setupRecurringReminders = async () => {
    try {
      const response = await axios.post(`${API}/reminders/setup-recurring`);
      toast.success(response.data.message);
      loadReminders();
    } catch (error) {
      console.error('Błąd tworzenia przypomnień cyklicznych:', error);
      toast.error('Nie udało się utworzyć przypomnień');
    }
  };

  const testNotifications = async () => {
    // Test if notifications work
    showNotification('Test powiadomienia 🔔', {
      body: 'Jeśli widzisz to powiadomienie, system działa poprawnie!',
      tag: 'test-notification'
    });
    toast.success('Wysłano testowe powiadomienie');
  };

  const checkNow = async () => {
    toast.info('Sprawdzam przypomnienia...');
    await checkPendingReminders();
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      reminder_date: new Date().toISOString().split('T')[0],
      reminder_time: '09:00',
      is_recurring: false
    });
    setEditingReminder(null);
  };

  const handleAddNew = () => {
    resetForm();
    setDialogOpen(true);
  };

  if (loading) {
    return <div className="text-center py-12">Ładowanie...</div>;
  }

  const upcomingReminders = reminders.filter(r => !r.is_completed && new Date(r.reminder_date) >= new Date().setHours(0,0,0,0));
  const completedReminders = reminders.filter(r => r.is_completed);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Przypomnienia</h2>
          <p className="text-gray-600 mt-1">Zarządzaj przypomnieniami i powiadomieniami</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={testNotifications} variant="outline" className="text-green-600">
            <Send className="h-4 w-4 mr-2" />
            Test powiadomień
          </Button>
          <Button onClick={checkNow} variant="outline" className="text-purple-600">
            <Bell className="h-4 w-4 mr-2" />
            Sprawdź teraz
          </Button>
          <Button onClick={setupRecurringReminders} variant="outline" className="text-blue-600">
            <RefreshCw className="h-4 w-4 mr-2" />
            Setup ZUS/Podatki
          </Button>
          <Button onClick={handleAddNew} className="bg-blue-600 hover:bg-blue-700">
            <Plus className="h-4 w-4 mr-2" />
            Dodaj przypomnienie
          </Button>
        </div>
      </div>

      {/* Info Card */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-4">
          <div className="flex items-start gap-3">
            <Bell className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <p className="text-sm text-blue-900 font-medium">
                Automatyczne przypomnienia: ZUS i Podatki
              </p>
              <p className="text-sm text-blue-700 mt-1">
                Kliknij "Setup ZUS/Podatki" aby utworzyć przypomnienia na 18-ty dzień każdego miesiąca. 
                Otrzymasz powiadomienie push na telefon o 9:00 rano.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Upcoming Reminders */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calendar className="h-5 w-5 mr-2 text-green-600" />
            Nadchodzące przypomnienia ({upcomingReminders.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {upcomingReminders.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Brak nadchodzących przypomnień</p>
          ) : (
            <div className="space-y-3">
              {upcomingReminders.map((reminder) => (
                <div 
                  key={reminder.id} 
                  className="flex items-start justify-between p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold text-gray-900">{reminder.title}</h4>
                      {reminder.is_recurring && (
                        <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded">
                          Cykliczne
                        </span>
                      )}
                      {reminder.reminder_type !== 'custom' && (
                        <span className="px-2 py-0.5 text-xs bg-purple-100 text-purple-800 rounded">
                          {reminder.reminder_type === 'zus' ? 'ZUS' : 'Podatki'}
                        </span>
                      )}
                    </div>
                    {reminder.description && (
                      <p className="text-sm text-gray-600 mt-1">{reminder.description}</p>
                    )}
                    <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {new Date(reminder.reminder_date).toLocaleDateString('pl-PL')}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        {reminder.reminder_time}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => handleToggleComplete(reminder)}
                      className="text-green-600"
                    >
                      <Check className="h-4 w-4" />
                    </Button>
                    {reminder.reminder_type === 'custom' && (
                      <>
                        <Button variant="ghost" size="sm" onClick={() => handleEdit(reminder)}>
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(reminder.id)}>
                          <Trash2 className="h-4 w-4 text-red-600" />
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Completed Reminders */}
      {completedReminders.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center text-gray-600">
              <Check className="h-5 w-5 mr-2" />
              Ukończone ({completedReminders.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {completedReminders.map((reminder) => (
                <div 
                  key={reminder.id} 
                  className="flex items-center justify-between p-3 border rounded-lg bg-gray-50 opacity-60"
                >
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-700 line-through">{reminder.title}</h4>
                    <span className="text-sm text-gray-500">
                      {new Date(reminder.reminder_date).toLocaleDateString('pl-PL')}
                    </span>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => handleToggleComplete(reminder)}
                  >
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Add/Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingReminder ? 'Edytuj przypomnienie' : 'Dodaj przypomnienie'}</DialogTitle>
            <DialogDescription>
              Utworzysz nowe przypomnienie z powiadomieniem push
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="title">Tytuł *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="np. Spotkanie z klientem"
                required
              />
            </div>

            <div>
              <Label htmlFor="description">Opis</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Dodatkowe szczegóły..."
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="reminder_date">Data *</Label>
                <Input
                  id="reminder_date"
                  type="date"
                  value={formData.reminder_date}
                  onChange={(e) => setFormData({ ...formData, reminder_date: e.target.value })}
                  required
                />
              </div>

              <div>
                <Label htmlFor="reminder_time">Godzina *</Label>
                <Input
                  id="reminder_time"
                  type="time"
                  value={formData.reminder_time}
                  onChange={(e) => setFormData({ ...formData, reminder_time: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                Anuluj
              </Button>
              <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
                {editingReminder ? 'Zapisz zmiany' : 'Dodaj przypomnienie'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Potwierdź usunięcie</DialogTitle>
            <DialogDescription>
              Ta operacja jest nieodwracalna.
            </DialogDescription>
          </DialogHeader>
          <p className="text-gray-600">Czy na pewno chcesz usunąć to przypomnienie?</p>
          <div className="flex justify-end gap-2 mt-4">
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              Anuluj
            </Button>
            <Button variant="destructive" onClick={confirmDelete}>
              Usuń
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Reminders;
