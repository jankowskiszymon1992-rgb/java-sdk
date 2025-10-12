import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Camera, Upload, Plus, Trash2, Image as ImageIcon, X } from 'lucide-react';
import { photosApi, projectsApi } from '../api/api';
import { toast } from 'sonner';

const Photos = () => {
  const [photos, setPhotos] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  const [viewerOpen, setViewerOpen] = useState(false);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const [formData, setFormData] = useState({
    project_id: '',
    title: '',
    description: '',
    image_data: '',
    taken_date: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [photosRes, projectsRes] = await Promise.all([
        photosApi.getAll(),
        projectsApi.getAll(),
      ]);
      setPhotos(photosRes.data);
      setProjects(projectsRes.data);
    } catch (error) {
      console.error('Błąd ładowania danych:', error);
      toast.error('Nie udało się załadować danych');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (e, source) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      toast.error('Proszę wybrać plik obrazu');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const imageData = event.target.result;
      setFormData({
        ...formData,
        image_data: imageData,
        title: formData.title || file.name.replace(/\.[^/.]+$/, ''),
      });
      setDialogOpen(true);
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.image_data) {
      toast.error('Proszę dodać zdjęcie');
      return;
    }

    try {
      await photosApi.create(formData);
      toast.success('Zdjęcie dodane pomyślnie');
      setDialogOpen(false);
      resetForm();
      loadData();
    } catch (error) {
      console.error('Błąd zapisywania zdjęcia:', error);
      toast.error('Nie udało się zapisać zdjęcia');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Czy na pewno chcesz usunąć to zdjęcie?')) {
      try {
        await photosApi.delete(id);
        toast.success('Zdjęcie usunięte pomyślnie');
        loadData();
      } catch (error) {
        console.error('Błąd usuwania zdjęcia:', error);
        toast.error('Nie udało się usunąć zdjęcia');
      }
    }
  };

  const resetForm = () => {
    setFormData({
      project_id: '',
      title: '',
      description: '',
      image_data: '',
      taken_date: new Date().toISOString().split('T')[0],
    });
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  const handleDialogChange = (open) => {
    setDialogOpen(open);
    if (!open) {
      resetForm();
    }
  };

  const openViewer = (photo) => {
    setSelectedPhoto(photo);
    setViewerOpen(true);
  };

  if (loading) {
    return <div className="text-center py-12">Ładowanie...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Zdjęcia</h2>
          <p className="text-gray-600 mt-1">Galeria zdjęć z prac</p>
        </div>
        <div className="flex space-x-2">
          {/* Camera button */}
          <Button
            onClick={() => cameraInputRef.current?.click()}
            className="bg-yellow-500 hover:bg-yellow-600"
            data-testid="camera-btn"
          >
            <Camera className="h-4 w-4 mr-2" />
            Zrób zdjęcie
          </Button>
          <input
            ref={cameraInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={(e) => handleFileUpload(e, 'camera')}
            className="hidden"
          />

          {/* Upload button */}
          <Button
            onClick={() => fileInputRef.current?.click()}
            variant="outline"
            data-testid="upload-btn"
          >
            <Upload className="h-4 w-4 mr-2" />
            Wybierz z galerii
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={(e) => handleFileUpload(e, 'upload')}
            className="hidden"
          />
        </div>
      </div>

      {/* Photo Form Dialog */}
      <Dialog open={dialogOpen} onOpenChange={handleDialogChange}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Dodaj zdjęcie</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Preview */}
            {formData.image_data && (
              <div className="relative">
                <img
                  src={formData.image_data}
                  alt="Preview"
                  className="w-full h-64 object-contain bg-gray-100 rounded-lg"
                />
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <Label htmlFor="title">Tytuł *</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="np. Rozdzielnia główna"
                  required
                  data-testid="photo-title-input"
                />
              </div>

              <div>
                <Label htmlFor="project">Zlecenie (opcjonalne)</Label>
                <Select
                  value={formData.project_id}
                  onValueChange={(value) => setFormData({ ...formData, project_id: value })}
                >
                  <SelectTrigger data-testid="photo-project-select">
                    <SelectValue placeholder="Wybierz zlecenie" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Brak przypisania</SelectItem>
                    {projects.map((project) => (
                      <SelectItem key={project.id} value={project.id}>
                        {project.title}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="taken_date">Data zdjęcia</Label>
                <Input
                  id="taken_date"
                  type="date"
                  value={formData.taken_date}
                  onChange={(e) => setFormData({ ...formData, taken_date: e.target.value })}
                  data-testid="photo-date-input"
                />
              </div>

              <div className="md:col-span-2">
                <Label htmlFor="description">Opis</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  placeholder="Dodaj opis zdjęcia..."
                  data-testid="photo-description-input"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={() => handleDialogChange(false)}>
                Anuluj
              </Button>
              <Button type="submit" className="bg-yellow-500 hover:bg-yellow-600" data-testid="photo-submit-btn">
                Zapisz
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Photo Viewer Dialog */}
      <Dialog open={viewerOpen} onOpenChange={setViewerOpen}>
        <DialogContent className="max-w-4xl">
          {selectedPhoto && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center justify-between">
                  <span>{selectedPhoto.title}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setViewerOpen(false)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <img
                  src={selectedPhoto.image_data}
                  alt={selectedPhoto.title}
                  className="w-full max-h-[70vh] object-contain bg-gray-100 rounded-lg"
                />
                {selectedPhoto.description && (
                  <p className="text-gray-700">{selectedPhoto.description}</p>
                )}
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>Data: {new Date(selectedPhoto.taken_date).toLocaleDateString('pl-PL')}</span>
                  {selectedPhoto.project && (
                    <span>Zlecenie: {selectedPhoto.project.title}</span>
                  )}
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Gallery */}
      {photos.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            <ImageIcon className="h-16 w-16 mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-medium mb-2">Brak zdjęć</p>
            <p className="text-sm">Dodaj pierwsze zdjęcie używając przycisku powyżej</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {photos.map((photo) => (
            <Card key={photo.id} className="overflow-hidden hover:shadow-lg transition-shadow">
              <div
                className="relative cursor-pointer group"
                onClick={() => openViewer(photo)}
              >
                <img
                  src={photo.image_data}
                  alt={photo.title}
                  className="w-full h-48 object-cover"
                />
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity flex items-center justify-center">
                  <ImageIcon className="h-8 w-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
              <CardContent className="p-4">
                <h3 className="font-semibold text-gray-900 truncate mb-1">{photo.title}</h3>
                {photo.description && (
                  <p className="text-sm text-gray-600 line-clamp-2 mb-2">{photo.description}</p>
                )}
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{new Date(photo.taken_date).toLocaleDateString('pl-PL')}</span>
                  {photo.project && (
                    <span className="truncate ml-2 max-w-[120px]">{photo.project.title}</span>
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(photo.id);
                  }}
                  className="w-full mt-2 text-red-500 hover:text-red-700 hover:bg-red-50"
                  data-testid={`delete-photo-${photo.id}`}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Usuń
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default Photos;
