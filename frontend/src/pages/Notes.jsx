import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Plus, Edit, Trash2, FileText, Clock, Mic, MicOff } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const Notes = () => {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingNote, setEditingNote] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
  });

  useEffect(() => {
    // Inicjalizuj Web Speech API
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = 'pl-PL';
      
      recognitionInstance.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          }
        }
        if (finalTranscript) {
          setFormData(prev => ({
            ...prev,
            content: prev.content + finalTranscript
          }));
        }
      };
      
      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
        toast.error('Błąd rozpoznawania mowy');
      };
      
      setRecognition(recognitionInstance);
    }
  }, []);

  const toggleRecording = () => {
    if (!recognition) {
      toast.error('Rozpoznawanie mowy nie jest dostępne w tej przeglądarce');
      return;
    }
    
    if (isRecording) {
      recognition.stop();
      setIsRecording(false);
      toast.success('Nagrywanie zatrzymane');
    } else {
      recognition.start();
      setIsRecording(true);
      toast.success('Mów teraz...');
    }
  };

  useEffect(() => {
    loadNotes();
  }, []);

  const loadNotes = async () => {
    try {
      const response = await axios.get(`${API}/api/notes`);
      setNotes(response.data);
    } catch (error) {
      console.error('Błąd ładowania notatek:', error);
      toast.error('Nie udało się załadować notatek');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.content.trim()) {
      toast.error('Treść notatki nie może być pusta');
      return;
    }

    try {
      if (editingNote) {
        await axios.put(`${API}/api/notes/${editingNote.id}`, formData);
        toast.success('Notatka zaktualizowana');
      } else {
        await axios.post(`${API}/api/notes`, formData);
        toast.success('Notatka dodana');
      }
      setDialogOpen(false);
      resetForm();
      loadNotes();
    } catch (error) {
      console.error('Błąd zapisywania notatki:', error);
      toast.error('Nie udało się zapisać notatki');
    }
  };

  const handleEdit = (note) => {
    setEditingNote(note);
    setFormData({
      title: note.title || '',
      content: note.content,
    });
    setDialogOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Czy na pewno chcesz usunąć tę notatkę?')) return;
    
    try {
      await axios.delete(`${API}/api/notes/${id}`);
      toast.success('Notatka usunięta');
      loadNotes();
    } catch (error) {
      console.error('Błąd usuwania notatki:', error);
      toast.error('Nie udało się usunąć notatki');
    }
  };

  const resetForm = () => {
    setFormData({ title: '', content: '' });
    setEditingNote(null);
  };

  const handleDialogChange = (open) => {
    setDialogOpen(open);
    if (!open) {
      resetForm();
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('pl-PL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  if (loading) {
    return <div className="text-center py-12">Ładowanie...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <FileText className="h-8 w-8 text-purple-600" />
            Notatnik
          </h2>
          <p className="text-gray-600 mt-1">Szybkie zapisywanie notatek</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={handleDialogChange}>
          <Button onClick={() => setDialogOpen(true)} className="bg-purple-600 hover:bg-purple-700">
            <Plus className="h-4 w-4 mr-2" />
            Nowa notatka
          </Button>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>{editingNote ? 'Edytuj notatkę' : 'Nowa notatka'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">
                  Tytuł (opcjonalny)
                </label>
                <Input
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Np. Lista zakupów"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">
                  Treść *
                </label>
                <Textarea
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  rows={10}
                  required
                  placeholder="Wpisz swoją notatkę..."
                  className="resize-none"
                />
              </div>
              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => handleDialogChange(false)}>
                  Anuluj
                </Button>
                <Button type="submit" className="bg-purple-600 hover:bg-purple-700">
                  {editingNote ? 'Zapisz' : 'Dodaj'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {notes.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <FileText className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 text-lg mb-2">Brak notatek</p>
            <p className="text-gray-500 text-sm mb-4">Dodaj swoją pierwszą notatkę</p>
            <Button onClick={() => setDialogOpen(true)} className="bg-purple-600 hover:bg-purple-700">
              <Plus className="h-4 w-4 mr-2" />
              Dodaj notatkę
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {notes.map((note) => (
            <Card key={note.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <CardTitle className="text-lg">
                    {note.title || 'Bez tytułu'}
                  </CardTitle>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEdit(note)}
                      className="h-8 w-8 p-0"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(note.id)}
                      className="h-8 w-8 p-0 text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <div className="flex items-center text-xs text-gray-500 mt-1">
                  <Clock className="h-3 w-3 mr-1" />
                  {formatDate(note.updated_at)}
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-700 whitespace-pre-wrap line-clamp-6">
                  {note.content}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default Notes;
