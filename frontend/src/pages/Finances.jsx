import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Plus, Edit2, Trash2, DollarSign, TrendingUp, TrendingDown, Camera, FileText } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CATEGORIES = {
  // Przychody
  invoice_sales: { label: 'Faktura sprzedażowa', type: 'income', ocr: true },
  cash_income: { label: 'Pieniądze bez faktury', type: 'income', ocr: false },
  
  // Wydatki
  invoice_purchase: { label: 'Faktura zakupowa', type: 'expense', ocr: true },
  fuel: { label: 'Paliwo', type: 'expense', ocr: true },
  salaries: { label: 'Wypłaty pracowników', type: 'expense', ocr: false },
  taxes: { label: 'Podatki', type: 'expense', ocr: false },
  zus: { label: 'ZUS', type: 'expense', ocr: false },
  equipment: { label: 'Sprzęt', type: 'expense', ocr: false },
  clothes: { label: 'Ciuchy dla pracowników', type: 'expense', ocr: false },
};

const Finances = () => {
  const [entries, setEntries] = useState([]);
  const [summary, setSummary] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7));
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [entryToDelete, setEntryToDelete] = useState(null);
  const [editingEntry, setEditingEntry] = useState(null);
  const [useOCR, setUseOCR] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  const [formData, setFormData] = useState({
    category: '',
    date: new Date().toISOString().split('T')[0],
    description: '',
    amount_net: '',
    amount_gross: '',
    vat_rate: '',
    notes: '',
    image: null
  });

  useEffect(() => {
    loadData();
  }, [selectedMonth]);

  const loadData = async () => {
    try {
      const [entriesRes, summaryRes] = await Promise.all([
        axios.get(`${API}/financial-entries`, { params: { month: selectedMonth } }),
        axios.get(`${API}/financial-entries/summary`, { params: { month: selectedMonth } })
      ]);
      setEntries(entriesRes.data);
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
      if (useOCR && formData.image && !editingEntry) {
        // OCR upload
        toast.info('Przetwarzam fakturę... To może potrwać do 10 sekund');
        
        const reader = new FileReader();
        reader.onloadend = async () => {
          try {
            const base64 = reader.result.split(',')[1];
            console.log('Wysyłam obraz do OCR...');
            
            const response = await axios.post(`${API}/financial-entries/ocr`, {
              category: formData.category,
              image: base64,
              date: formData.date
            });
            
            console.log('OCR response:', response.data);
            toast.success('Faktura przetworzona i dodana pomyślnie! ✅');
            setDialogOpen(false);
            resetForm();
            loadData();
          } catch (error) {
            console.error('Błąd OCR:', error);
            const errorMsg = error.response?.data?.detail || error.message;
            toast.error(`Nie udało się przetworzyć faktury: ${errorMsg}`);
          }
        };
        
        reader.onerror = () => {
          toast.error('Nie udało się odczytać pliku obrazu');
        };
        
        reader.readAsDataURL(formData.image);
        return; // Don't continue with normal submit
      }
      
      // Normal manual entry
      const data = {
        category: formData.category,
        date: formData.date,
        description: formData.description,
        amount_net: parseFloat(formData.amount_net),
        amount_gross: parseFloat(formData.amount_gross),
        vat_rate: formData.vat_rate ? parseFloat(formData.vat_rate) : null,
        notes: formData.notes || null
      };
      
      if (editingEntry) {
        await axios.put(`${API}/financial-entries/${editingEntry.id}`, data);
        toast.success('Wpis zaktualizowany pomyślnie');
      } else {
        await axios.post(`${API}/financial-entries`, data);
        toast.success('Wpis dodany pomyślnie');
      }
      
      setDialogOpen(false);
      resetForm();
      loadData();
    } catch (error) {
      console.error('Błąd zapisywania wpisu:', error);
      toast.error('Nie udało się zapisać wpisu: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleEdit = (entry) => {
    setEditingEntry(entry);
    setFormData({
      category: entry.category,
      date: entry.date,
      description: entry.description,
      amount_net: entry.amount_net.toString(),
      amount_gross: entry.amount_gross.toString(),
      vat_rate: entry.vat_rate ? entry.vat_rate.toString() : '',
      notes: entry.notes || '',
      image: null
    });
    setUseOCR(false);
    setDialogOpen(true);
  };

  const handleDelete = (id) => {
    setEntryToDelete(id);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (entryToDelete) {
      try {
        await axios.delete(`${API}/financial-entries/${entryToDelete}`);
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
      category: '',
      date: new Date().toISOString().split('T')[0],
      description: '',
      amount_net: '',
      amount_gross: '',
      vat_rate: '',
      notes: '',
      image: null
    });
    setEditingEntry(null);
    setUseOCR(false);
    setImagePreview(null);
  };

  const handleAddNew = () => {
    resetForm();
    setDialogOpen(true);
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFormData({ ...formData, image: file });
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCategoryChange = (category) => {
    setFormData({ ...formData, category });
    // Don't auto-enable OCR - let user choose
  };

  if (loading) {
    return <div className="text-center py-12">Ładowanie...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Finanse</h2>
          <p className="text-gray-600 mt-1">Zarządzaj przychodami i wydatkami</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Label htmlFor="month-select" className="text-sm text-gray-600">Miesiąc:</Label>
            <Input
              id="month-select"
              type="month"
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
              className="w-40"
            />
          </div>
          <Button onClick={handleAddNew} className="bg-green-600 hover:bg-green-700">
            <Plus className="h-4 w-4 mr-2" />
            Dodaj wpis
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-green-600">
                <TrendingUp className="h-5 w-5 mr-2" />
                Przychody
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Netto:</span>
                  <span className="text-lg font-bold">{summary.totals.income_net.toFixed(2)} zł</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Brutto:</span>
                  <span className="text-lg font-bold">{summary.totals.income_gross.toFixed(2)} zł</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-red-600">
                <TrendingDown className="h-5 w-5 mr-2" />
                Wydatki
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Netto:</span>
                  <span className="text-lg font-bold">{summary.totals.expense_net.toFixed(2)} zł</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Brutto:</span>
                  <span className="text-lg font-bold">{summary.totals.expense_gross.toFixed(2)} zł</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-blue-600">
                <DollarSign className="h-5 w-5 mr-2" />
                Bilans
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Netto:</span>
                  <span className={`text-lg font-bold ${summary.totals.balance_net >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {summary.totals.balance_net.toFixed(2)} zł
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Brutto:</span>
                  <span className={`text-lg font-bold ${summary.totals.balance_gross >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {summary.totals.balance_gross.toFixed(2)} zł
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Category Summary */}
      {summary && summary.categories.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Podsumowanie per kategoria</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {summary.categories.map((cat) => (
                <div key={cat.category} className="border rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">{CATEGORIES[cat.category]?.label}</h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Netto:</span>
                      <span className="font-semibold">{cat.total_net.toFixed(2)} zł</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Brutto:</span>
                      <span className="font-semibold">{cat.total_gross.toFixed(2)} zł</span>
                    </div>
                    <div className="flex justify-between text-gray-500">
                      <span>Wpisów:</span>
                      <span>{cat.count}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Entries Table - continued in next message due to length */}

      {/* All Entries Table */}
      <Card>
        <CardHeader>
          <CardTitle>Wszystkie wpisy</CardTitle>
        </CardHeader>
        <CardContent>
          {entries.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Brak wpisów dla wybranego miesiąca</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kategoria</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Opis</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Kwota netto</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Kwota brutto</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Akcje</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {entries.map((entry) => (
                    <tr key={entry.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-700">
                        {new Date(entry.date).toLocaleDateString('pl-PL')}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          CATEGORIES[entry.category]?.type === 'income' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {CATEGORIES[entry.category]?.label}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">{entry.description}</td>
                      <td className="px-4 py-3 text-sm text-right font-semibold">{entry.amount_net.toFixed(2)} zł</td>
                      <td className="px-4 py-3 text-sm text-right font-semibold">{entry.amount_gross.toFixed(2)} zł</td>
                      <td className="px-4 py-3 text-right">
                        <Button variant="ghost" size="sm" onClick={() => handleEdit(entry)}>
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(entry.id)}>
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
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingEntry ? 'Edytuj wpis' : 'Dodaj nowy wpis'}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="category">Kategoria *</Label>
                <Select
                  value={formData.category}
                  onValueChange={handleCategoryChange}
                  required
                  disabled={editingEntry}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Wybierz kategorię" />
                  </SelectTrigger>
                  <SelectContent position="popper" sideOffset={5}>
                    <div className="px-2 py-1 text-xs font-semibold text-green-600">PRZYCHODY</div>
                    {Object.entries(CATEGORIES).filter(([_, cat]) => cat.type === 'income').map(([key, cat]) => (
                      <SelectItem key={key} value={key}>{cat.label}</SelectItem>
                    ))}
                    <div className="px-2 py-1 text-xs font-semibold text-red-600 mt-2">WYDATKI</div>
                    {Object.entries(CATEGORIES).filter(([_, cat]) => cat.type === 'expense').map(([key, cat]) => (
                      <SelectItem key={key} value={key}>{cat.label}</SelectItem>
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
                />
              </div>
            </div>

            {/* OCR Toggle for supported categories */}
            {!editingEntry && formData.category && CATEGORIES[formData.category]?.ocr && (
              <div className="flex items-center gap-4 p-3 bg-blue-50 rounded-md">
                <Camera className="h-5 w-5 text-blue-600" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Ta kategoria obsługuje OCR</p>
                  <p className="text-xs text-gray-600">AI automatycznie wyciągnie dane z faktury</p>
                </div>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant={useOCR ? "default" : "outline"}
                    size="sm"
                    onClick={() => setUseOCR(true)}
                  >
                    <Camera className="h-4 w-4 mr-1" />
                    Zeskanuj
                  </Button>
                  <Button
                    type="button"
                    variant={!useOCR ? "default" : "outline"}
                    size="sm"
                    onClick={() => {
                      setUseOCR(false);
                      setImagePreview(null);
                      setFormData({ ...formData, image: null });
                    }}
                  >
                    <FileText className="h-4 w-4 mr-1" />
                    Wpisz ręcznie
                  </Button>
                </div>
              </div>
            )}

            {useOCR && !editingEntry ? (
              <div>
                <Label htmlFor="image">Zdjęcie faktury *</Label>
                <Input
                  id="image"
                  type="file"
                  accept="image/*"
                  capture="environment"
                  onChange={handleImageChange}
                  required
                />
                {imagePreview && (
                  <div className="mt-2">
                    <img src={imagePreview} alt="Preview" className="max-h-60 rounded border" />
                  </div>
                )}
                <p className="text-sm text-blue-600 mt-2">
                  📸 Zrób zdjęcie faktury - AI automatycznie wyciągnie wszystkie dane
                </p>
              </div>
            ) : (
              <>
                <div>
                  <Label htmlFor="description">Opis *</Label>
                  <Input
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Numer faktury, opis..."
                    required
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="amount_net">Kwota netto * (zł)</Label>
                    <Input
                      id="amount_net"
                      type="number"
                      step="0.01"
                      value={formData.amount_net}
                      onChange={(e) => setFormData({ ...formData, amount_net: e.target.value })}
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="amount_gross">Kwota brutto * (zł)</Label>
                    <Input
                      id="amount_gross"
                      type="number"
                      step="0.01"
                      value={formData.amount_gross}
                      onChange={(e) => setFormData({ ...formData, amount_gross: e.target.value })}
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="vat_rate">VAT (%)</Label>
                    <Input
                      id="vat_rate"
                      type="number"
                      step="0.01"
                      value={formData.vat_rate}
                      onChange={(e) => setFormData({ ...formData, vat_rate: e.target.value })}
                      placeholder="23"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="notes">Notatki</Label>
                  <Textarea
                    id="notes"
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    rows={3}
                  />
                </div>
              </>
            )}

            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                Anuluj
              </Button>
              <Button type="submit" className="bg-green-600 hover:bg-green-700">
                {editingEntry ? 'Zapisz zmiany' : (useOCR ? 'Przetwórz i dodaj' : 'Dodaj wpis')}
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
          <p className="text-gray-600">Czy na pewno chcesz usunąć ten wpis? Ta operacja jest nieodwracalna.</p>
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

export default Finances;
