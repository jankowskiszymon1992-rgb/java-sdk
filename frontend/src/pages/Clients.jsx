import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Plus, Edit, Trash2, Phone, Mail, MapPin, Camera } from 'lucide-react';
import { clientsApi } from '../api/api';
import { toast } from 'sonner';
import QRScanner from '../components/QRScanner';

const Clients = () => {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [clientToDelete, setClientToDelete] = useState(null);
  const [editingClient, setEditingClient] = useState(null);
  const [showQRScanner, setShowQRScanner] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    address: '',
    city: '',
    postal_code: '',
    notes: '',
  });

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      const response = await clientsApi.getAll();
      setClients(response.data);
    } catch (error) {
      console.error('Błąd ładowania klientów:', error);
      toast.error('Nie udało się załadować klientów');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingClient) {
        await clientsApi.update(editingClient.id, formData);
        toast.success('Klient zaktualizowany pomyślnie');
      } else {
        await clientsApi.create(formData);
        toast.success('Klient dodany pomyślnie');
      }
      setDialogOpen(false);
      resetForm();
      loadClients();
    } catch (error) {
      console.error('Błąd zapisywania klienta:', error);
      toast.error('Nie udało się zapisać klienta');
    }
  };

  const handleEdit = (client) => {
    setEditingClient(client);
    setFormData({
      name: client.name,
      phone: client.phone,
      email: client.email || '',
      address: client.address,
      city: client.city,
      postal_code: client.postal_code,
      notes: client.notes || '',
    });
    setDialogOpen(true);
  };

  const handleDelete = async (id) => {
    setClientToDelete(id);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (clientToDelete) {
      try {
        await clientsApi.delete(clientToDelete);
        toast.success('Klient usunięty pomyślnie');
        loadClients();
      } catch (error) {
        console.error('Błąd usuwania klienta:', error);
        toast.error('Nie udało się usunąć klienta');
      } finally {
        setDeleteDialogOpen(false);
        setClientToDelete(null);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      phone: '',
      email: '',
      address: '',
      city: '',
      postal_code: '',
      notes: '',
    });
    setEditingClient(null);
  };

  const handleDialogChange = (open) => {
    setDialogOpen(open);
    if (!open) {
      resetForm();
    }
  };

  const handleQRScan = (decodedText) => {
    try {
      // Próbuj parsować jako JSON (vCard lub JSON)
      let data = {};
      
      if (decodedText.startsWith('BEGIN:VCARD')) {
        // Format vCard (wizytówka)
        const lines = decodedText.split('\n');
        lines.forEach(line => {
          if (line.startsWith('FN:')) data.name = line.substring(3).trim();
          if (line.startsWith('TEL:')) data.phone = line.substring(4).trim();
          if (line.startsWith('EMAIL:')) data.email = line.substring(6).trim();
          if (line.startsWith('ADR:')) {
            const parts = line.substring(4).split(';');
            data.address = parts[2] || '';
            data.city = parts[3] || '';
            data.postal_code = parts[5] || '';
          }
        });
      } else {
        try {
          // Spróbuj jako JSON
          data = JSON.parse(decodedText);
        } catch {
          // Jeśli nie JSON, może być po prostu tekst (np. numer telefonu)
          if (/^\d{9,}$/.test(decodedText)) {
            data.phone = decodedText;
          } else {
            data.notes = decodedText;
          }
        }
      }
      
      // Ustaw dane w formularzu
      setFormData(prev => ({
        ...prev,
        ...data
      }));
      
      setDialogOpen(true); // Otwórz formularz z wypełnionymi danymi
      toast.success('Dane z QR kodu wczytane!');
    } catch (error) {
      console.error('Błąd parsowania QR:', error);
      toast.error('Nie udało się odczytać danych z QR kodu');
    }
  };

  if (loading) {
    return <div className="text-center py-12">Ładowanie...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Klienci</h2>
          <p className="text-gray-600 mt-1">Zarządzaj listą klientów</p>
        </div>
        <div className="flex gap-2">
          <Button 
            onClick={() => setShowQRScanner(true)}
            className="bg-purple-600 hover:bg-purple-700"
          >
            <Camera className="h-4 w-4 mr-2" />
            Skanuj QR
          </Button>
          <Dialog open={dialogOpen} onOpenChange={handleDialogChange}>
            <DialogTrigger asChild>
              <Button className="bg-yellow-500 hover:bg-yellow-600" data-testid="add-client-btn">
                <Plus className="h-4 w-4 mr-2" />
                Dodaj klienta
              </Button>
            </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{editingClient ? 'Edytuj klienta' : 'Nowy klient'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <Label htmlFor="name">Nazwa / Imię i nazwisko *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    data-testid="client-name-input"
                  />
                </div>
                <div>
                  <Label htmlFor="phone">Telefon *</Label>
                  <Input
                    id="phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    required
                    data-testid="client-phone-input"
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    data-testid="client-email-input"
                  />
                </div>
                <div className="col-span-2">
                  <Label htmlFor="address">Adres *</Label>
                  <Input
                    id="address"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    required
                    data-testid="client-address-input"
                  />
                </div>
                <div>
                  <Label htmlFor="city">Miasto *</Label>
                  <Input
                    id="city"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    required
                    data-testid="client-city-input"
                  />
                </div>
                <div>
                  <Label htmlFor="postal_code">Kod pocztowy *</Label>
                  <Input
                    id="postal_code"
                    value={formData.postal_code}
                    onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                    required
                    data-testid="client-postal-input"
                  />
                </div>
                <div className="col-span-2">
                  <Label htmlFor="notes">Notatki</Label>
                  <Textarea
                    id="notes"
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    rows={3}
                    data-testid="client-notes-input"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => handleDialogChange(false)}>
                  Anuluj
                </Button>
                <Button type="submit" className="bg-yellow-500 hover:bg-yellow-600" data-testid="client-submit-btn">
                  {editingClient ? 'Zapisz' : 'Dodaj'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent className="p-0">
          {clients.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              Brak klientów. Dodaj pierwszego klienta!
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nazwa</TableHead>
                  <TableHead>Kontakt</TableHead>
                  <TableHead>Adres</TableHead>
                  <TableHead className="text-right">Akcje</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {clients.map((client) => (
                  <TableRow key={client.id}>
                    <TableCell className="font-medium">{client.name}</TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="flex items-center text-sm">
                          <Phone className="h-3 w-3 mr-2 text-gray-400" />
                          {client.phone}
                        </div>
                        {client.email && (
                          <div className="flex items-center text-sm text-gray-600">
                            <Mail className="h-3 w-3 mr-2 text-gray-400" />
                            {client.email}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-start text-sm">
                        <MapPin className="h-3 w-3 mr-2 mt-1 text-gray-400 flex-shrink-0" />
                        <span>{client.address}, {client.postal_code} {client.city}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(client)}
                        data-testid={`edit-client-${client.id}`}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(client.id)}
                        data-testid={`delete-client-${client.id}`}
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

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Potwierdź usunięcie</DialogTitle>
          </DialogHeader>
          <p className="text-gray-600">Czy na pewno chcesz usunąć tego klienta? Ta operacja jest nieodwracalna.</p>
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

      {/* QR Scanner */}
      <QRScanner
        isOpen={showQRScanner}
        onClose={() => setShowQRScanner(false)}
        onScan={handleQRScan}
        title="Skanuj wizytówkę klienta"
      />
    </div>
  );
};

export default Clients;
