import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileText, Plus, Mic, Trash2, Edit } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingReport, setEditingReport] = useState(null);
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    title: '',
    work_description: '',
    materials_used: '',
    additional_info: ''
  });

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const response = await api.get('/daily-reports');
      setReports(response.data);
    } catch (error) {
      console.error('Błąd pobierania raportów:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingReport) {
        await api.put(`/daily-reports/${editingReport.id}`, formData);
      } else {
        await api.post('/daily-reports', formData);
      }
      setIsDialogOpen(false);
      resetForm();
      fetchReports();
    } catch (error) {
      console.error('Błąd zapisywania raportu:', error);
      alert('Błąd zapisywania raportu');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Czy na pewno chcesz usunąć ten raport?')) return;
    
    try {
      await api.delete(`/daily-reports/${id}`);
      fetchReports();
    } catch (error) {
      console.error('Błąd usuwania raportu:', error);
      alert('Błąd usuwania raportu');
    }
  };

  const handleEdit = (report) => {
    setEditingReport(report);
    setFormData({
      date: report.date,
      title: report.title,
      work_description: report.work_description,
      materials_used: report.materials_used,
      additional_info: report.additional_info
    });
    setIsDialogOpen(true);
  };

  const resetForm = () => {
    setEditingReport(null);
    setFormData({
      date: new Date().toISOString().split('T')[0],
      title: '',
      work_description: '',
      materials_used: '',
      additional_info: ''
    });
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pl-PL', {
      weekday: 'short',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Raporty Dzienne</h2>
          <p className="text-gray-600 mt-1">Zarządzaj raportami z wykonanych prac</p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => {
              resetForm();
              setIsDialogOpen(true);
            }}
            className="bg-blue-500 hover:bg-blue-600"
          >
            <Plus className="h-4 w-4 mr-2" />
            Nowy raport
          </Button>
          <Button
            onClick={() => window.location.href = '/reports/voice'}
            className="bg-green-500 hover:bg-green-600"
          >
            <Mic className="h-4 w-4 mr-2" />
            Raport głosowy
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-500">Ładowanie raportów...</p>
        </div>
      ) : reports.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-500 mb-4">Brak raportów dziennych</p>
            <Button onClick={() => setIsDialogOpen(true)} className="bg-blue-500 hover:bg-blue-600">
              <Plus className="h-4 w-4 mr-2" />
              Dodaj pierwszy raport
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {reports.map((report) => (
            <Card key={report.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-blue-100 border-b">
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-xl text-blue-900">{report.title}</CardTitle>
                    <p className="text-sm text-blue-700 mt-1">{formatDate(report.date)}</p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleEdit(report)}
                      className="hover:bg-blue-200"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDelete(report.id)}
                      className="hover:bg-red-200 text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <h4 className="font-semibold text-sm text-gray-700 mb-2">Wykonane Prace</h4>
                    <p className="text-sm text-gray-600 whitespace-pre-wrap">{report.work_description}</p>
                  </div>
                  <div>
                    <h4 className="font-semibold text-sm text-gray-700 mb-2">Zużyte Materiały</h4>
                    <p className="text-sm text-gray-600 whitespace-pre-wrap">{report.materials_used}</p>
                  </div>
                  <div>
                    <h4 className="font-semibold text-sm text-gray-700 mb-2">Informacje Dodatkowe</h4>
                    <p className="text-sm text-gray-600 whitespace-pre-wrap">{report.additional_info}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingReport ? 'Edytuj raport' : 'Nowy raport dzienny'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="date">Data</Label>
                <Input
                  id="date"
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="title">Tytuł / Klient</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="np. Jan Kowalski"
                  required
                />
              </div>
            </div>

            <div>
              <Label htmlFor="work_description">Wykonane Prace</Label>
              <Textarea
                id="work_description"
                value={formData.work_description}
                onChange={(e) => setFormData({ ...formData, work_description: e.target.value })}
                placeholder="Opisz wykonane prace..."
                rows={4}
                required
              />
            </div>

            <div>
              <Label htmlFor="materials_used">Zużyte Materiały</Label>
              <Textarea
                id="materials_used"
                value={formData.materials_used}
                onChange={(e) => setFormData({ ...formData, materials_used: e.target.value })}
                placeholder="Lista zużytych materiałów..."
                rows={4}
                required
              />
            </div>

            <div>
              <Label htmlFor="additional_info">Informacje Dodatkowe</Label>
              <Textarea
                id="additional_info"
                value={formData.additional_info}
                onChange={(e) => setFormData({ ...formData, additional_info: e.target.value })}
                placeholder="Dodatkowe uwagi..."
                rows={3}
              />
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setIsDialogOpen(false);
                  resetForm();
                }}
              >
                Anuluj
              </Button>
              <Button type="submit" className="bg-blue-500 hover:bg-blue-600">
                {editingReport ? 'Zapisz zmiany' : 'Dodaj raport'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Reports;
