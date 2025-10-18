import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Users, Plus, Edit2, Trash2, Clock, Calendar } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Employees = () => {
  const [employees, setEmployees] = useState([]);
  const [workEntries, setWorkEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [workDialogOpen, setWorkDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteWorkDialogOpen, setDeleteWorkDialogOpen] = useState(false);
  const [employeeToDelete, setEmployeeToDelete] = useState(null);
  const [workEntryToDelete, setWorkEntryToDelete] = useState(null);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [editingWorkEntry, setEditingWorkEntry] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    hourly_rate: '',
    notes: ''
  });
  const [workFormData, setWorkFormData] = useState({
    employee_id: '',
    date: new Date().toISOString().split('T')[0],
    hours: '',
    notes: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [employeesRes, workEntriesRes] = await Promise.all([
        axios.get(`${API}/employees`),
        axios.get(`${API}/employee-work-entries`)
      ]);
      setEmployees(employeesRes.data);
      setWorkEntries(workEntriesRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Nie udało się załadować danych');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (editingEmployee) {
        await axios.put(`${API}/employees/${editingEmployee.id}`, formData);
        toast.success('Pracownik zaktualizowany pomyślnie');
      } else {
        await axios.post(`${API}/employees`, formData);
        toast.success('Pracownik dodany pomyślnie');
      }
      
      loadData();
      setDialogOpen(false);
      resetForm();
    } catch (error) {
      console.error('Error saving employee:', error);
      toast.error('Nie udało się zapisać pracownika');
    }
  };

  const handleWorkSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const data = {
        ...workFormData,
        hours: parseFloat(workFormData.hours)
      };
      
      await axios.post(`${API}/employee-work-entries`, data);
      toast.success('Godziny dodane pomyślnie');
      
      loadData();
      setWorkDialogOpen(false);
      resetWorkForm();
    } catch (error) {
      console.error('Error saving work entry:', error);
      toast.error('Nie udało się zapisać godzin');
    }
  };

  const handleEdit = (employee) => {
    setEditingEmployee(employee);
    setFormData({
      name: employee.name,
      hourly_rate: employee.hourly_rate.toString(),
      notes: employee.notes || ''
    });
    setDialogOpen(true);
  };

  const handleDelete = (id) => {
    setEmployeeToDelete(id);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (employeeToDelete) {
      try {
        await axios.delete(`${API}/employees/${employeeToDelete}`);
        toast.success('Pracownik usunięty pomyślnie');
        loadData();
      } catch (error) {
        console.error('Error deleting employee:', error);
        toast.error('Nie udało się usunąć pracownika');
      } finally {
        setDeleteDialogOpen(false);
        setEmployeeToDelete(null);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      hourly_rate: '',
      notes: ''
    });
    setEditingEmployee(null);
  };

  const resetWorkForm = () => {
    setWorkFormData({
      employee_id: '',
      date: new Date().toISOString().split('T')[0],
      hours: '',
      notes: ''
    });
  };

  const handleAddNew = () => {
    resetForm();
    setDialogOpen(true);
  };

  const handleAddWorkHours = () => {
    resetWorkForm();
    setWorkDialogOpen(true);
  };

  // Calculate preview earnings when hours/employee changes
  const calculatePreviewEarnings = () => {
    if (workFormData.employee_id && workFormData.hours) {
      const employee = employees.find(e => e.id === workFormData.employee_id);
      if (employee) {
        return (parseFloat(workFormData.hours) * employee.hourly_rate).toFixed(2);
      }
    }
    return '0.00';
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Users className="h-8 w-8 text-blue-600" />
            Pracownicy
          </h2>
          <p className="text-gray-600 mt-1">Zarządzaj listą pracowników i ich stawkami</p>
        </div>
        <Button onClick={handleAddNew} className="bg-blue-600 hover:bg-blue-700">
          <Plus className="h-4 w-4 mr-2" />
          Dodaj pracownika
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Lista pracowników</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-gray-500 text-center py-4">Ładowanie...</p>
          ) : employees.length === 0 ? (
            <p className="text-gray-500 text-center py-4">Brak pracowników. Dodaj pierwszego pracownika.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Imię</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stawka (zł/h)</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Notatki</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Akcje</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {employees.map((employee) => (
                    <tr key={employee.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">{employee.name}</td>
                      <td className="px-4 py-3 text-sm text-gray-700">{employee.hourly_rate} zł</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{employee.notes || '-'}</td>
                      <td className="px-4 py-3 text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(employee)}
                        >
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(employee.id)}
                        >
                          <Trash2 className="h-4 w-4 text-red-600" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Work Hours Section */}
      <Card className="mt-6">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-green-600" />
              Godziny pracy
            </CardTitle>
            <p className="text-sm text-gray-600 mt-1">Rejestruj przepracowane godziny pracowników</p>
          </div>
          <Button onClick={handleAddWorkHours} className="bg-green-600 hover:bg-green-700">
            <Plus className="h-4 w-4 mr-2" />
            Dodaj godziny
          </Button>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-gray-500 text-center py-4">Ładowanie...</p>
          ) : workEntries.length === 0 ? (
            <p className="text-gray-500 text-center py-4">Brak wpisów. Dodaj pierwszy wpis godzin pracy.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Imię</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dzień</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Godziny</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Stawka (zł/h)</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Wynik (zł)</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Notatki</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Akcje</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {workEntries.map((entry) => (
                    <tr key={entry.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">{entry.employee_name}</td>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        {new Date(entry.date).toLocaleDateString('pl-PL')}
                      </td>
                      <td className="px-4 py-3 text-sm text-right text-gray-700">{entry.hours}h</td>
                      <td className="px-4 py-3 text-sm text-right text-gray-700">{entry.hourly_rate} zł</td>
                      <td className="px-4 py-3 text-sm text-right font-semibold text-green-600">
                        {entry.total_earnings.toFixed(2)} zł
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">{entry.notes || '-'}</td>
                      <td className="px-4 py-3 text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEditWorkEntry(entry)}
                        >
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteWorkEntry(entry.id)}
                        >
                          <Trash2 className="h-4 w-4 text-red-600" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add/Edit Employee Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingEmployee ? 'Edytuj pracownika' : 'Dodaj nowego pracownika'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Imię *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Stawka godzinowa (zł) *
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.hourly_rate}
                onChange={(e) => setFormData({ ...formData, hourly_rate: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Notatki
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
                rows={3}
              />
            </div>

            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setDialogOpen(false)}
              >
                Anuluj
              </Button>
              <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
                {editingEmployee ? 'Zapisz zmiany' : 'Dodaj pracownika'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Add Work Hours Dialog */}
      <Dialog open={workDialogOpen} onOpenChange={setWorkDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Dodaj godziny pracy</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleWorkSubmit} className="space-y-4">
            <div>
              <Label htmlFor="employee_id">Pracownik *</Label>
              <Select
                value={workFormData.employee_id}
                onValueChange={(value) => setWorkFormData({ ...workFormData, employee_id: value })}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Wybierz pracownika" />
                </SelectTrigger>
                <SelectContent position="popper" sideOffset={5}>
                  {employees.length === 0 ? (
                    <div className="px-2 py-1 text-sm text-gray-500">Brak pracowników</div>
                  ) : (
                    employees.map((employee) => (
                      <SelectItem key={employee.id} value={employee.id}>
                        {employee.name} ({employee.hourly_rate} zł/h)
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="date">Data *</Label>
              <Input
                id="date"
                type="date"
                value={workFormData.date}
                onChange={(e) => setWorkFormData({ ...workFormData, date: e.target.value })}
                required
              />
            </div>

            <div>
              <Label htmlFor="hours">Liczba godzin *</Label>
              <Input
                id="hours"
                type="number"
                step="0.25"
                min="0"
                value={workFormData.hours}
                onChange={(e) => setWorkFormData({ ...workFormData, hours: e.target.value })}
                placeholder="np. 8 lub 4.5"
                required
              />
            </div>

            {/* Preview Earnings */}
            {workFormData.employee_id && workFormData.hours && (
              <div className="bg-green-50 border border-green-200 rounded-md p-3">
                <p className="text-sm text-gray-700">
                  <span className="font-medium">Przewidywane zarobki:</span>{' '}
                  <span className="text-lg font-bold text-green-600">
                    {calculatePreviewEarnings()} zł
                  </span>
                </p>
              </div>
            )}

            <div>
              <Label htmlFor="work_notes">Notatki</Label>
              <textarea
                id="work_notes"
                value={workFormData.notes}
                onChange={(e) => setWorkFormData({ ...workFormData, notes: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
                rows={3}
                placeholder="Opis wykonanych prac..."
              />
            </div>

            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setWorkDialogOpen(false)}
              >
                Anuluj
              </Button>
              <Button type="submit" className="bg-green-600 hover:bg-green-700">
                Dodaj godziny
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
          </DialogHeader>
          <p className="text-gray-600">Czy na pewno chcesz usunąć tego pracownika? Ta operacja jest nieodwracalna.</p>
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

export default Employees;
