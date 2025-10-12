import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Mail, RefreshCw, Send, Loader2, CheckCircle, AlertCircle, MailOpen, Inbox } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MailPage = () => {
  const [connected, setConnected] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  const [loading, setLoading] = useState(true);
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [composeForm, setComposeForm] = useState({
    to: '',
    subject: '',
    body: ''
  });

  useEffect(() => {
    checkConnection();
    
    // Check if redirected after OAuth
    const params = new URLSearchParams(window.location.search);
    if (params.get('connected') === 'true') {
      window.history.replaceState({}, '', '/mail');
      checkConnection();
      fetchEmails();
    }
  }, []);

  const checkConnection = async () => {
    try {
      const response = await axios.get(`${API}/gmail/status`);
      setConnected(response.data.connected);
      setUserEmail(response.data.email || '');
    } catch (error) {
      console.error('Error checking connection:', error);
    } finally {
      setLoading(false);
    }
  };

  const connectGmail = async () => {
    try {
      const response = await axios.get(`${API}/gmail/auth/start`);
      window.location.href = response.data.authorization_url;
    } catch (error) {
      console.error('Error connecting Gmail:', error);
      setError('Nie udało się połączyć z Gmail');
    }
  };

  const fetchEmails = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/gmail/emails?max_results=20`);
      setEmails(response.data.emails);
    } catch (error) {
      console.error('Error fetching emails:', error);
      setError('Nie udało się pobrać emaili');
    } finally {
      setLoading(false);
    }
  };

  const openEmail = async (email) => {
    try {
      const response = await axios.get(`${API}/gmail/emails/${email.id}`);
      setSelectedEmail(response.data);
      
      // Mark as read if unread
      if (email.unread) {
        await axios.post(`${API}/gmail/emails/${email.id}/read`);
        // Update local state
        setEmails(emails.map(e => 
          e.id === email.id ? { ...e, unread: false } : e
        ));
      }
    } catch (error) {
      console.error('Error opening email:', error);
      setError('Nie udało się otworzyć emaila');
    }
  };

  const sendEmail = async (e) => {
    e.preventDefault();
    try {
      setSending(true);
      await axios.post(`${API}/gmail/send`, composeForm);
      setIsComposeOpen(false);
      setComposeForm({ to: '', subject: '', body: '' });
      alert('Email wysłany pomyślnie!');
    } catch (error) {
      console.error('Error sending email:', error);
      setError('Nie udało się wysłać emaila');
    } finally {
      setSending(false);
    }
  };

  const disconnect = async () => {
    if (!window.confirm('Czy na pewno chcesz odłączyć Gmail?')) return;
    
    try {
      await axios.delete(`${API}/gmail/disconnect`);
      setConnected(false);
      setUserEmail('');
      setEmails([]);
    } catch (error) {
      console.error('Error disconnecting:', error);
      setError('Nie udało się odłączyć Gmail');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!connected) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader className="bg-gradient-to-r from-blue-50 to-blue-100 border-b">
            <CardTitle className="flex items-center gap-2 text-blue-900">
              <Mail className="h-6 w-6" />
              Poczta Email
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <Mail className="h-16 w-16 mx-auto text-gray-400" />
              <h3 className="text-xl font-semibold">Połącz swoje konto Gmail</h3>
              <p className="text-gray-600">
                Aby korzystać z poczty w aplikacji, połącz swoje konto Gmail
              </p>
              <Button
                onClick={connectGmail}
                className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-6 text-lg"
              >
                <Mail className="h-5 w-5 mr-2" />
                Połącz Gmail
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Poczta</h2>
          <p className="text-gray-600 mt-1">Połączono: {userEmail}</p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={fetchEmails}
            variant="outline"
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Odśwież
          </Button>
          <Button
            onClick={() => setIsComposeOpen(true)}
            className="bg-green-500 hover:bg-green-600"
          >
            <Send className="h-4 w-4 mr-2" />
            Nowy email
          </Button>
          <Button
            onClick={disconnect}
            variant="outline"
            className="text-red-600 hover:bg-red-50"
          >
            Odłącz
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid md:grid-cols-3 gap-6">
        {/* Email List */}
        <div className="md:col-span-1">
          <Card>
            <CardHeader className="bg-gradient-to-r from-blue-50 to-blue-100 border-b">
              <CardTitle className="flex items-center gap-2 text-blue-900 text-base">
                <Inbox className="h-5 w-5" />
                Skrzynka odbiorcza
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {emails.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  Brak wiadomości
                </div>
              ) : (
                <div className="divide-y">
                  {emails.map((email) => (
                    <div
                      key={email.id}
                      onClick={() => openEmail(email)}
                      className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                        email.unread ? 'bg-blue-50' : ''
                      } ${selectedEmail?.id === email.id ? 'bg-blue-100' : ''}`}
                    >
                      <div className="flex items-start gap-2">
                        {email.unread && (
                          <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                        )}
                        <div className="flex-1 min-w-0">
                          <div className={`text-sm truncate ${email.unread ? 'font-semibold' : ''}`}>
                            {email.from.split('<')[0].trim()}
                          </div>
                          <div className={`text-sm truncate ${email.unread ? 'font-medium' : 'text-gray-600'}`}>
                            {email.subject}
                          </div>
                          <div className="text-xs text-gray-500 truncate mt-1">
                            {email.snippet}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Email Content */}
        <div className="md:col-span-2">
          {selectedEmail ? (
            <Card>
              <CardHeader className="bg-gradient-to-r from-gray-50 to-gray-100 border-b">
                <CardTitle className="text-lg">{selectedEmail.subject}</CardTitle>
                <div className="text-sm text-gray-600 space-y-1 mt-2">
                  <div><strong>Od:</strong> {selectedEmail.from}</div>
                  <div><strong>Do:</strong> {selectedEmail.to}</div>
                  <div><strong>Data:</strong> {selectedEmail.date}</div>
                </div>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="prose max-w-none whitespace-pre-wrap">
                  {selectedEmail.body}
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-20 text-center">
                <MailOpen className="h-16 w-16 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-500">Wybierz email aby go przeczytać</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Compose Dialog */}
      <Dialog open={isComposeOpen} onOpenChange={setIsComposeOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Nowy email</DialogTitle>
          </DialogHeader>
          <form onSubmit={sendEmail} className="space-y-4">
            <div>
              <Label htmlFor="to">Do</Label>
              <Input
                id="to"
                type="email"
                value={composeForm.to}
                onChange={(e) => setComposeForm({ ...composeForm, to: e.target.value })}
                placeholder="adres@email.com"
                required
              />
            </div>
            <div>
              <Label htmlFor="subject">Temat</Label>
              <Input
                id="subject"
                value={composeForm.subject}
                onChange={(e) => setComposeForm({ ...composeForm, subject: e.target.value })}
                placeholder="Temat wiadomości"
                required
              />
            </div>
            <div>
              <Label htmlFor="body">Treść</Label>
              <Textarea
                id="body"
                value={composeForm.body}
                onChange={(e) => setComposeForm({ ...composeForm, body: e.target.value })}
                placeholder="Wpisz treść wiadomości..."
                rows={10}
                required
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsComposeOpen(false)}
              >
                Anuluj
              </Button>
              <Button
                type="submit"
                disabled={sending}
                className="bg-green-500 hover:bg-green-600"
              >
                {sending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Wysyłanie...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Wyślij
                  </>
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default MailPage;
