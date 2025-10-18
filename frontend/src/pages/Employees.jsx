import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Users, Plus, Edit2, Trash2 } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Employees = () => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [employeeToDelete, setEmployeeToDelete] = useState(null);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    hourly_rate: '',
    notes: ''
  });

  useEffect(() => {
    loadEmployees();
  }, []);

  const loadEmployees = async () => {
    try {
      const response = await axios.get(`${API}/employees`);
      setEmployees(response.data);
    } catch (error) {
      console.error('Error loading employees:', error);
      toast.error('Nie udało się załadować pracowników');
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
      
      loadEmployees();
      setDialogOpen(false);
      resetForm();
    } catch (error) {
      console.error('Error saving employee:', error);
      toast.error('Nie udało się zapisać pracownika');
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
        loadEmployees();
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

  const handleAddNew = () => {
    resetForm();
    setDialogOpen(true);
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

      {/* Add/Edit Dialog */}
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
