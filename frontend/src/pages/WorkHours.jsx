import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Plus, Edit, Trash2, Clock as ClockIcon } from 'lucide-react';
import { workHoursApi, projectsApi } from '../api/api';
import { toast } from 'sonner';

const WorkHours = () => {
  const [workHours, setWorkHours] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [entryToDelete, setEntryToDelete] = useState(null);
  const [editingEntry, setEditingEntry] = useState(null);
  const [summary, setSummary] = useState({ total_hours: 0, total_entries: 0 });
  const [formData, setFormData] = useState({
    project_id: '',
    date: new Date().toISOString().split('T')[0],
    hours: '',
    notes: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [workHoursRes, projectsRes, summaryRes] = await Promise.all([
        workHoursApi.getAll(),
        projectsApi.getAll(),
        workHoursApi.getSummary(),
      ]);
      console.log('📊 Loaded projects:', projectsRes.data);
      console.log('📊 Projects count:', projectsRes.data?.length);
      setWorkHours(workHoursRes.data);
      setProjects(projectsRes.data);
      setSummary(summaryRes.data);
    } catch (error) {
      console.error('Błąd ładowania danych:', error);
      toast.error('Nie udało się załadować danych');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = {
        ...formData,
        hours: parseFloat(formData.hours),
      };
      
      if (editingEntry) {
        await workHoursApi.update(editingEntry.id, data);
        toast.success('Wpis zaktualizowany pomyślnie');
      } else {
        await workHoursApi.create(data);
        toast.success('Godziny dodane pomyślnie');
      }
      setDialogOpen(false);
      resetForm();
      loadData();
    } catch (error) {
      console.error('Błąd zapisywania godzin:', error);
      toast.error('Nie udało się zapisać godzin');
    }
  };

  const handleEdit = (entry) => {
    setEditingEntry(entry);
    setFormData({
      project_id: entry.project_id,
      date: entry.date,
      hours: entry.hours.toString(),
      notes: entry.notes || '',
    });
    setDialogOpen(true);
  };

  const handleDelete = async (id) => {
    setEntryToDelete(id);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (entryToDelete) {
      try {
        await workHoursApi.delete(entryToDelete);
        toast.success('Wpis usunięty pomyślnie');
        loadData();
      } catch (error) {
        console.error('Błąd usuwania wpisu:', error);
        toast.error('Nie udało się usunąć wpisu');
      } finally {
        setDeleteDialogOpen(false);
        setEntryToDelete(null);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      project_id: '',
      date: new Date().toISOString().split('T')[0],
      hours: '',
      notes: '',
    });
    setEditingEntry(null);
  };

  const handleDialogChange = (open) => {
    setDialogOpen(open);
    if (!open) {
      resetForm();
    }
  };

  // Sort by date (newest first)
  const sortedWorkHours = [...workHours].sort((a, b) => new Date(b.date) - new Date(a.date));

  if (loading) {
    return <div className="text-center py-12">Ładowanie...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Godziny pracy</h2>
          <p className="text-gray-600 mt-1">Rejestruj przepracowane godziny</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={handleDialogChange}>
          <DialogTrigger asChild>
            <Button className="bg-yellow-500 hover:bg-yellow-600" data-testid="add-workhour-btn">
              <Plus className="h-4 w-4 mr-2" />
              Dodaj godziny
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>{editingEntry ? 'Edytuj wpis' : 'Dodaj godziny pracy'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="project_id">Zlecenie *</Label>
                  <Select
                    value={formData.project_id}
                    onValueChange={(value) => setFormData({ ...formData, project_id: value })}
                    required
                  >
                    <SelectTrigger data-testid="workhour-project-select">
                      <SelectValue placeholder="Wybierz zlecenie" />
                    </SelectTrigger>
                    <SelectContent>
                      {projects.map((project) => (
                        <SelectItem key={project.id} value={project.id}>
                          {project.title} ({project.client?.name})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="date">Data *</Label>
                  <Input
                    id="date"
                    type="date"
                    value={formData.date}
                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                    required
                    data-testid="workhour-date-input"
                  />
                </div>
                <div>
                  <Label htmlFor="hours">Liczba godzin *</Label>
                  <Input
                    id="hours"
                    type="number"
                    step="0.25"
                    min="0"
                    value={formData.hours}
                    onChange={(e) => setFormData({ ...formData, hours: e.target.value })}
                    placeholder="np. 8 lub 4.5"
                    required
                    data-testid="workhour-hours-input"
                  />
                </div>
                <div>
                  <Label htmlFor="notes">Notatki</Label>
                  <Textarea
                    id="notes"
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    rows={3}
                    placeholder="Opis wykonanych prac..."
                    data-testid="workhour-notes-input"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => handleDialogChange(false)}>
                  Anuluj
                </Button>
                <Button type="submit" className="bg-yellow-500 hover:bg-yellow-600" data-testid="workhour-submit-btn">
                  {editingEntry ? 'Zapisz' : 'Dodaj'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <ClockIcon className="h-5 w-5 mr-2 text-yellow-500" />
              Łączna liczba godzin
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-gray-900">{summary.total_hours}</p>
            <p className="text-sm text-gray-600 mt-1">wszystkie wpisy</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <ClockIcon className="h-5 w-5 mr-2 text-blue-500" />
              Liczba wpisów
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-gray-900">{summary.total_entries}</p>
            <p className="text-sm text-gray-600 mt-1">zarejestrowanych
</p>
          </CardContent>
        </Card>
      </div>

      {/* Work Hours Table */}
      <Card>
        <CardHeader>
          <CardTitle>Historia godzin pracy</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {sortedWorkHours.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              Brak wpisów. Dodaj swoje pierwsze godziny pracy!
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Data</TableHead>
                    <TableHead>Zlecenie</TableHead>
                    <TableHead>Klient</TableHead>
                    <TableHead className="text-center">Godziny</TableHead>
                    <TableHead>Notatki</TableHead>
                    <TableHead className="text-right">Akcje</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedWorkHours.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell className="font-medium">
                        {new Date(entry.date).toLocaleDateString('pl-PL', {
                          weekday: 'short',
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </TableCell>
                      <TableCell>{entry.project?.title || 'Brak'}</TableCell>
                      <TableCell className="text-gray-600">
                        {entry.project?.client?.name || 'Brak'}
                      </TableCell>
                      <TableCell className="text-center">
                        <span className="inline-flex items-center px-3 py-1 rounded-full bg-yellow-100 text-yellow-800 font-medium">
                          {entry.hours}h
                        </span>
                      </TableCell>
                      <TableCell className="max-w-xs truncate text-gray-600">
                        {entry.notes || '-'}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(entry)}
                          data-testid={`edit-workhour-${entry.id}`}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(entry.id)}
                          data-testid={`delete-workhour-${entry.id}`}
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Potwierdź usunięcie</DialogTitle>
          </DialogHeader>
          <p className="text-gray-600">Czy na pewno chcesz usunąć ten wpis godzin pracy? Ta operacja jest nieodwracalna.</p>
          <div className="flex justify-end gap-2 mt-4">
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
            >
              Anuluj
            </Button>
            <Button
              variant="destructive"
              onClick={confirmDelete}
            >
              Usuń
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default WorkHours;
