import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { FolderOpen, Mail, Bot, Construction, FileText, Eye, Download, Trash2, Calendar } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const MyFiles = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFolder, setSelectedFolder] = useState('all');
  const [viewingFile, setViewingFile] = useState(null);
  const [showViewer, setShowViewer] = useState(false);

  useEffect(() => {
    loadFiles();
  }, [selectedFolder]);

  const loadFiles = async () => {
    try {
      const folderParam = selectedFolder === 'all' ? '' : `?folder=${selectedFolder}`;
      const response = await axios.get(`${API}/api/saved-files${folderParam}`);
      setFiles(response.data);
    } catch (error) {
      console.error('Błąd ładowania plików:', error);
      toast.error('Nie udało się załadować plików');
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = async (fileId, filename) => {
    try {
      const response = await axios.get(`${API}/api/saved-files/${fileId}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Plik pobrany!');
    } catch (error) {
      toast.error('Nie udało się pobrać pliku');
    }
  };

  const viewFile = async (file) => {
    if (file.content_type === 'application/pdf') {
      setViewingFile(file);
      setShowViewer(true);
    } else {
      toast.info('Podgląd dostępny tylko dla PDF');
      downloadFile(file.id, file.filename);
    }
  };

  const deleteFile = async (fileId, filename) => {
    if (!window.confirm(`Usunąć plik "${filename}"?`)) return;
    
    try {
      await axios.delete(`${API}/api/saved-files/${fileId}`);
      toast.success('Plik usunięty');
      loadFiles();
    } catch (error) {
      toast.error('Nie udało się usunąć pliku');
    }
  };

  const getFileIcon = (filename, contentType) => {
    if (contentType === 'application/pdf') return '📄';
    if (contentType.includes('word')) return '📝';
    if (contentType.includes('excel') || contentType.includes('spreadsheet')) return '📊';
    if (contentType.includes('image')) return '🖼️';
    return '📎';
  };

  const getFolderIcon = (folder) => {
    switch (folder) {
      case 'email': return <Mail className="h-5 w-5" />;
      case 'ai': return <Bot className="h-5 w-5" />;
      case 'roboty': return <Construction className="h-5 w-5" />;
      case 'inne': return <FileText className="h-5 w-5" />;
      default: return <FolderOpen className="h-5 w-5" />;
    }
  };

  const getFolderLabel = (folder) => {
    switch (folder) {
      case 'email': return 'Z Emaili';
      case 'ai': return 'Z AI';
      case 'roboty': return 'Roboty';
      case 'inne': return 'Inne';
      default: return 'Wszystkie';
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

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const filteredFiles = files.filter(f => 
    selectedFolder === 'all' || f.folder === selectedFolder
  );

  const folders = [
    { id: 'all', label: 'Wszystkie', icon: <FolderOpen className="h-5 w-5" />, count: files.length },
    { id: 'email', label: 'Z Emaili', icon: <Mail className="h-5 w-5" />, count: files.filter(f => f.folder === 'email').length },
    { id: 'ai', label: 'Z AI', icon: <Bot className="h-5 w-5" />, count: files.filter(f => f.folder === 'ai').length },
    { id: 'roboty', label: 'Roboty', icon: <Construction className="h-5 w-5" />, count: files.filter(f => f.folder === 'roboty').length },
    { id: 'inne', label: 'Inne', icon: <FileText className="h-5 w-5" />, count: files.filter(f => f.folder === 'inne').length },
  ];

  if (loading) {
    return <div className="text-center py-12">Ładowanie...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <FolderOpen className="h-8 w-8 text-purple-600" />
          Moje Pliki
        </h2>
        <p className="text-gray-600 mt-1">Wszystkie zapisane pliki w jednym miejscu</p>
      </div>

      {/* Folder Tabs */}
      <Tabs value={selectedFolder} onValueChange={setSelectedFolder} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          {folders.map(folder => (
            <TabsTrigger key={folder.id} value={folder.id} className="flex items-center gap-2">
              {folder.icon}
              <span className="hidden md:inline">{folder.label}</span>
              <span className="text-xs bg-gray-200 px-2 py-0.5 rounded-full">{folder.count}</span>
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value={selectedFolder} className="mt-6">
          {filteredFiles.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <FolderOpen className="h-16 w-16 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600 text-lg mb-2">Brak plików</p>
                <p className="text-gray-500 text-sm">
                  {selectedFolder === 'all' ? 'Nie masz jeszcze żadnych zapisanych plików' : `Brak plików w folderze "${getFolderLabel(selectedFolder)}"`}
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredFiles.map(file => (
                <Card key={file.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-3xl">{getFileIcon(file.filename, file.content_type)}</span>
                        <div className="flex-1 min-w-0">
                          <CardTitle className="text-base truncate">{file.filename}</CardTitle>
                          <p className="text-xs text-gray-500 mt-1 flex items-center gap-2">
                            {getFolderIcon(file.folder)}
                            {getFolderLabel(file.folder)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      <p className="text-gray-600 truncate">
                        <span className="font-medium">Źródło:</span> {file.source}
                      </p>
                      <p className="text-gray-600">
                        <span className="font-medium">Rozmiar:</span> {formatSize(file.size)}
                      </p>
                      <p className="text-gray-600 flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formatDate(file.created_at)}
                      </p>
                    </div>
                    <div className="flex gap-2 mt-4">
                      {file.content_type === 'application/pdf' && (
                        <Button
                          onClick={() => viewFile(file)}
                          size="sm"
                          variant="outline"
                          className="flex-1"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          Podgląd
                        </Button>
                      )}
                      <Button
                        onClick={() => downloadFile(file.id, file.filename)}
                        size="sm"
                        className="flex-1 bg-blue-600 hover:bg-blue-700"
                      >
                        <Download className="h-4 w-4 mr-1" />
                        Pobierz
                      </Button>
                      <Button
                        onClick={() => deleteFile(file.id, file.filename)}
                        size="sm"
                        variant="ghost"
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* PDF Viewer Modal */}
      <Dialog open={showViewer} onOpenChange={setShowViewer}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center justify-between">
              <span>📄 {viewingFile?.filename}</span>
              <div className="flex gap-2">
                <Button
                  onClick={() => downloadFile(viewingFile?.id, viewingFile?.filename)}
                  size="sm"
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  ⬇️ Pobierz
                </Button>
              </div>
            </DialogTitle>
          </DialogHeader>
          {viewingFile && (
            <div className="flex-1 mt-4 overflow-hidden">
              <iframe
                src={`${API}/api/saved-files/${viewingFile.id}`}
                className="w-full h-full border-0 rounded"
                style={{ minHeight: '70vh' }}
                title="PDF Viewer"
              />
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default MyFiles;
