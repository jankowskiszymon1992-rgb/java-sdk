import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MapPin, Calendar, User, Clock } from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const statusLabels = {
  new: { label: 'Nowe', color: 'bg-blue-100 text-blue-800' },
  in_progress: { label: 'W trakcie', color: 'bg-yellow-100 text-yellow-800' },
  completed: { label: 'Zakończone', color: 'bg-green-100 text-green-800' },
  cancelled: { label: 'Anulowane', color: 'bg-red-100 text-red-800' },
};

const ProjectShare = () => {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProject();
  }, [projectId]);

  const loadProject = async () => {
    try {
      const response = await axios.get(`${API}/api/projects/${projectId}`);
      setProject(response.data);
    } catch (error) {
      setError('Nie udało się załadować projektu');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
        <p className="text-xl">Ładowanie...</p>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="text-center py-12">
            <p className="text-xl text-red-600">{error || 'Projekt nie znaleziony'}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-12 px-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Elektron</h1>
          <p className="text-gray-600">Status Projektu</p>
        </div>

        {/* Project Card */}
        <Card className="shadow-xl">
          <CardHeader className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
            <CardTitle className="text-2xl">{project.title}</CardTitle>
            <Badge className={`${statusLabels[project.status].color} mt-2 w-fit`}>
              {statusLabels[project.status].label}
            </Badge>
          </CardHeader>
          <CardContent className="space-y-6 pt-6">
            {/* Client Info */}
            {project.client && (
              <div className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg">
                <User className="h-5 w-5 text-blue-600 mt-1" />
                <div>
                  <p className="font-semibold text-gray-900">Klient</p>
                  <p className="text-gray-700">{project.client.name}</p>
                </div>
              </div>
            )}

            {/* Description */}
            <div>
              <p className="font-semibold text-gray-900 mb-2">Opis projektu:</p>
              <p className="text-gray-700 whitespace-pre-wrap">{project.description}</p>
            </div>

            {/* Location */}
            {project.location && (
              <div className="flex items-start gap-3">
                <MapPin className="h-5 w-5 text-blue-600 mt-1" />
                <div>
                  <p className="font-semibold text-gray-900">Lokalizacja</p>
                  <p className="text-gray-700">{project.location}</p>
                </div>
              </div>
            )}

            {/* Dates */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-blue-600 mt-1" />
                <div>
                  <p className="font-semibold text-gray-900">Data rozpoczęcia</p>
                  <p className="text-gray-700">
                    {project.start_date ? new Date(project.start_date).toLocaleDateString('pl-PL') : 'Brak'}
                  </p>
                </div>
              </div>
              {project.end_date && (
                <div className="flex items-start gap-3">
                  <Clock className="h-5 w-5 text-blue-600 mt-1" />
                  <div>
                    <p className="font-semibold text-gray-900">Data zakończenia</p>
                    <p className="text-gray-700">
                      {new Date(project.end_date).toLocaleDateString('pl-PL')}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Notes */}
            {project.notes && (
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="font-semibold text-gray-900 mb-2">Notatki:</p>
                <p className="text-gray-700 whitespace-pre-wrap">{project.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center text-gray-600 text-sm">
          <p>Powered by Elektron © 2025</p>
        </div>
      </div>
    </div>
  );
};

export default ProjectShare;
