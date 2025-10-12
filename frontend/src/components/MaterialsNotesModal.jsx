import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Plus, Trash2, Save } from 'lucide-react';
import { projectsApi } from '../api/api';
import { toast } from 'sonner';

const MaterialsNotesModal = ({ open, onOpenChange, project, onSave }) => {
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && project) {
      setMaterials(project.materials_notes || []);
    }
  }, [open, project]);

  const addRow = () => {
    const newRow = {
      id: Date.now().toString(),
      category: 'zużyte',
      material: '',
      quantity: '',
      unit: 'szt.',
      notes: '',
      date: new Date().toISOString().split('T')[0],
    };
    setMaterials([...materials, newRow]);
  };

  const updateRow = (id, field, value) => {
    setMaterials(materials.map(row => 
      row.id === id ? { ...row, [field]: value } : row
    ));
  };

  const deleteRow = (id) => {
    setMaterials(materials.filter(row => row.id !== id));
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await projectsApi.update(project.id, {
        materials_notes: materials,
      });
      toast.success('Notatki materiałów zapisane pomyślnie');
      onSave();
      onOpenChange(false);
    } catch (error) {
      console.error('Błąd zapisywania notatek:', error);
      toast.error('Nie udało się zapisać notatek');
    } finally {
      setLoading(false);
    }
  };

  const categoryLabels = {
    zużyte: 'Zużyte',
    do_nabycia: 'Do nabycia',
    do_oddania: 'Do oddania',
  };

  const units = ['szt.', 'm', 'mb', 'kg', 'l', 'opak.', 'komplet'];

  if (!project) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <div>
              <span className="text-lg">Notatki materiałów</span>
              <p className="text-sm font-normal text-gray-600 mt-1">
                {project.title}
              </p>
            </div>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <Button
            onClick={addRow}
            className="bg-yellow-500 hover:bg-yellow-600"
            size="sm"
            data-testid="add-material-row"
          >
            <Plus className="h-4 w-4 mr-2" />
            Dodaj wiersz
          </Button>

          <div className="border rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="bg-gray-50">
                    <TableHead className="w-[140px]">Kategoria</TableHead>
                    <TableHead className="min-w-[200px]">Materiał</TableHead>
                    <TableHead className="w-[100px]">Ilość</TableHead>
                    <TableHead className="w-[100px]">Jedn.</TableHead>
                    <TableHead className="min-w-[200px]">Notatki</TableHead>
                    <TableHead className="w-[120px]">Data</TableHead>
                    <TableHead className="w-[60px]">Akcje</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {materials.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                        Brak materiałów. Dodaj pierwszy wiersz!
                      </TableCell>
                    </TableRow>
                  ) : (
                    materials.map((row) => (
                      <TableRow key={row.id}>
                        <TableCell>
                          <Select
                            value={row.category}
                            onValueChange={(value) => updateRow(row.id, 'category', value)}
                          >
                            <SelectTrigger className="h-9">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {Object.entries(categoryLabels).map(([key, label]) => (
                                <SelectItem key={key} value={key}>
                                  {label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </TableCell>
                        <TableCell>
                          <Input
                            value={row.material}
                            onChange={(e) => updateRow(row.id, 'material', e.target.value)}
                            placeholder="np. Kabel YDYp 3x1,5"
                            className="h-9"
                          />
                        </TableCell>
                        <TableCell>
                          <Input
                            type="number"
                            step="0.01"
                            value={row.quantity}
                            onChange={(e) => updateRow(row.id, 'quantity', e.target.value)}
                            placeholder="0"
                            className="h-9"
                          />
                        </TableCell>
                        <TableCell>
                          <Select
                            value={row.unit}
                            onValueChange={(value) => updateRow(row.id, 'unit', value)}
                          >
                            <SelectTrigger className="h-9">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {units.map((unit) => (
                                <SelectItem key={unit} value={unit}>
                                  {unit}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </TableCell>
                        <TableCell>
                          <Input
                            value={row.notes}
                            onChange={(e) => updateRow(row.id, 'notes', e.target.value)}
                            placeholder="Dodatkowe info..."
                            className="h-9"
                          />
                        </TableCell>
                        <TableCell>
                          <Input
                            type="date"
                            value={row.date}
                            onChange={(e) => updateRow(row.id, 'date', e.target.value)}
                            className="h-9"
                          />
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteRow(row.id)}
                            className="h-8 w-8 p-0"
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </div>

          {/* Podsumowanie */}
          {materials.length > 0 && (
            <div className="grid grid-cols-3 gap-4 pt-4 border-t">
              <div className="bg-red-50 p-3 rounded-lg">
                <p className="text-sm text-gray-600">Zużyte</p>
                <p className="text-xl font-bold text-red-700">
                  {materials.filter(m => m.category === 'zużyte').length}
                </p>
              </div>
              <div className="bg-blue-50 p-3 rounded-lg">
                <p className="text-sm text-gray-600">Do nabycia</p>
                <p className="text-xl font-bold text-blue-700">
                  {materials.filter(m => m.category === 'do_nabycia').length}
                </p>
              </div>
              <div className="bg-green-50 p-3 rounded-lg">
                <p className="text-sm text-gray-600">Do oddania</p>
                <p className="text-xl font-bold text-green-700">
                  {materials.filter(m => m.category === 'do_oddania').length}
                </p>
              </div>
            </div>
          )}

          <div className="flex justify-end space-x-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              Anuluj
            </Button>
            <Button
              onClick={handleSave}
              className="bg-yellow-500 hover:bg-yellow-600"
              disabled={loading}
              data-testid="save-materials-btn"
            >
              <Save className="h-4 w-4 mr-2" />
              {loading ? 'Zapisywanie...' : 'Zapisz'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default MaterialsNotesModal;
