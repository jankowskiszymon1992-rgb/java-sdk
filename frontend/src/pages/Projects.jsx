import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Plus, Edit, Trash2, MapPin, Calendar, FileText } from 'lucide-react';
import { projectsApi, clientsApi } from '../api/api';
import { toast } from 'sonner';
import MaterialsNotesModal from '../components/MaterialsNotesModal';

const statusLabels = {
  new: { label: 'Nowe', color: 'bg-blue-100 text-blue-800' },
  in_progress: { label: 'W trakcie', color: 'bg-yellow-100 text-yellow-800' },
  completed: { label: 'Zakończone', color: 'bg-green-100 text-green-800' },
  cancelled: { label: 'Anulowane', color: 'bg-red-100 text-red-800' },
};

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState(null);
  const [editingProject, setEditingProject] = useState(null);
  const [activeTab, setActiveTab] = useState('all');
  const [materialsModalOpen, setMaterialsModalOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [formData, setFormData] = useState({
    client_id: '',
    title: '',
    description: '',
    status: 'new',
    start_date: '',
    end_date: '',
    location: '',
    estimated_hours: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [projectsRes, clientsRes] = await Promise.all([
        projectsApi.getAll(),
        clientsApi.getAll(),
      ]);
      setProjects(projectsRes.data);
      setClients(clientsRes.data);
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
        estimated_hours: formData.estimated_hours ? parseFloat(formData.estimated_hours) : null,
      };
      
      if (editingProject) {
        await projectsApi.update(editingProject.id, data);
        toast.success('Projekt zaktualizowany pomyślnie');
      } else {
        await projectsApi.create(data);
        toast.success('Projekt dodany pomyślnie');
      }
      setDialogOpen(false);
      resetForm();
      loadData();
    } catch (error) {
      console.error('Błąd zapisywania projektu:', error);
      toast.error('Nie udało się zapisać projektu');
    }
  };

  const handleEdit = (project) => {
    setEditingProject(project);
    setFormData({
      client_id: project.client_id,
      title: project.title,
      description: project.description,
      status: project.status,
      start_date: project.start_date,
      end_date: project.end_date || '',
      location: project.location,
      estimated_hours: project.estimated_hours || '',
    });
    setDialogOpen(true);
  };

  const handleDelete = async (id) => {
    setProjectToDelete(id);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (projectToDelete) {
      try {
        await projectsApi.delete(projectToDelete);
        toast.success('Projekt usunięty pomyślnie');
        loadData();
      } catch (error) {
        console.error('Błąd usuwania projektu:', error);
        toast.error('Nie udało się usunąć projektu');
      } finally {
        setDeleteDialogOpen(false);
        setProjectToDelete(null);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      client_id: '',
      title: '',
      description: '',
      status: 'new',
      start_date: '',
      end_date: '',
      location: '',
      estimated_hours: '',
    });
    setEditingProject(null);
  };

  const handleDialogChange = (open) => {
    setDialogOpen(open);
    if (!open) {
      resetForm();
    }
  };

  const handleOpenMaterials = (project) => {
    setSelectedProject(project);
    setMaterialsModalOpen(true);
  };

  const filteredProjects = activeTab === 'all' 
    ? projects 
    : projects.filter(p => p.status === activeTab);

  if (loading) {
    return <div className="text-center py-12">Ładowanie...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Projekty</h2>
          <p className="text-gray-600 mt-1">Zarządzaj swoimi projektami</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={handleDialogChange}>
          <DialogTrigger asChild>
            <Button className="bg-yellow-500 hover:bg-yellow-600" data-testid="add-project-btn">
              <Plus className="h-4 w-4 mr-2" />
              Nowe zlecenie
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{editingProject ? 'Edytuj zlecenie' : 'Nowe zlecenie'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <Label htmlFor="client_id">Klient *</Label>
                  <Select
                    value={formData.client_id}
                    onValueChange={(value) => setFormData({ ...formData, client_id: value })}
                    required
                  >
                    <SelectTrigger data-testid="project-client-select">
                      <SelectValue placeholder="Wybierz klienta" />
                    </SelectTrigger>
                    <SelectContent>
                      {clients.map((client) => (
                        <SelectItem key={client.id} value={client.id}>
                          {client.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="col-span-2">
                  <Label htmlFor="title">Tytuł zlecenia *</Label>
                  <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    required
                    data-testid="project-title-input"
                  />
                </div>
                <div className="col-span-2">
                  <Label htmlFor="description">Opis *</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={3}
                    required
                    data-testid="project-description-input"
                  />
                </div>
                <div className="col-span-2">
                  <Label htmlFor="location">Lokalizacja *</Label>
                  <Input
                    id="location"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    required
                    data-testid="project-location-input"
                  />
                </div>
                <div>
                  <Label htmlFor="status">Status</Label>
                  <Select
                    value={formData.status}
                    onValueChange={(value) => setFormData({ ...formData, status: value })}
                  >
                    <SelectTrigger data-testid="project-status-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(statusLabels).map(([key, value]) => (
                        <SelectItem key={key} value={key}>
                          {value.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="estimated_hours">Szacowane godziny</Label>
                  <Input
                    id="estimated_hours"
                    type="number"
                    step="0.5"
                    value={formData.estimated_hours}
                    onChange={(e) => setFormData({ ...formData, estimated_hours: e.target.value })}
                    data-testid="project-hours-input"
                  />
                </div>
                <div>
                  <Label htmlFor="start_date">Data rozpoczęcia *</Label>
                  <Input
                    id="start_date"
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    required
                    data-testid="project-start-date-input"
                  />
                </div>
                <div>
                  <Label htmlFor="end_date">Data zakończenia</Label>
                  <Input
                    id="end_date"
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                    data-testid="project-end-date-input"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => handleDialogChange(false)}>
                  Anuluj
                </Button>
                <Button type="submit" className="bg-yellow-500 hover:bg-yellow-600" data-testid="project-submit-btn">
                  {editingProject ? 'Zapisz' : 'Dodaj'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="all">Wszystkie</TabsTrigger>
          <TabsTrigger value="new">Nowe</TabsTrigger>
          <TabsTrigger value="in_progress">W trakcie</TabsTrigger>
          <TabsTrigger value="completed">Zakończone</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-4">
          <Card>
            <CardContent className="p-0">
              {filteredProjects.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  Brak zleceń w tej kategorii.
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Zlecenie</TableHead>
                      <TableHead>Klient</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Daty</TableHead>
                      <TableHead className="text-right">Akcje</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredProjects.map((project) => (
                      <TableRow key={project.id}>
                        <TableCell>
                          <div>
                            <p className="font-medium">{project.title}</p>
                            <div className="flex items-center text-sm text-gray-600 mt-1">
                              <MapPin className="h-3 w-3 mr-1" />
                              {project.location}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          {project.client ? project.client.name : 'Brak'}
                        </TableCell>
                        <TableCell>
                          <Badge className={statusLabels[project.status].color}>
                            {statusLabels[project.status].label}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">
                            <div className="flex items-center">
                              <Calendar className="h-3 w-3 mr-1 text-gray-400" />
                              {new Date(project.start_date).toLocaleDateString('pl-PL')}
                            </div>
                            {project.end_date && (
                              <div className="text-gray-600 mt-1">
                                do {new Date(project.end_date).toLocaleDateString('pl-PL')}
                              </div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleOpenMaterials(project)}
                            title="Notatka materiałów"
                            data-testid={`materials-project-${project.id}`}
                          >
                            <FileText className="h-4 w-4 text-blue-600" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEdit(project)}
                            title="Edytuj"
                            data-testid={`edit-project-${project.id}`}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(project.id)}
                            title="Usuń"
                            data-testid={`delete-project-${project.id}`}
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Materials Notes Modal */}
      <MaterialsNotesModal
        open={materialsModalOpen}
        onOpenChange={setMaterialsModalOpen}
        project={selectedProject}
        onSave={loadData}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Potwierdź usunięcie</DialogTitle>
          </DialogHeader>
          <p className="text-gray-600">Czy na pewno chcesz usunąć to zlecenie? Ta operacja jest nieodwracalna.</p>
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

export default Projects;
