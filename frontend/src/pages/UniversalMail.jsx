import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Mail, Plus, Trash2, RefreshCw, Send, Inbox, Paperclip, X, Eye, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL || '';

const UniversalMail = () => {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [folders, setFolders] = useState(['INBOX']);
  const [selectedFolder, setSelectedFolder] = useState('INBOX');
  
  // Modals
  const [showAddAccount, setShowAddAccount] = useState(false);
  const [showCompose, setShowCompose] = useState(false);
  const [showEmailDetail, setShowEmailDetail] = useState(false);
  
  // Forms
  const [newAccount, setNewAccount] = useState({ email: '', password: '' });
  const [composeData, setComposeData] = useState({ to: '', subject: '', body: '' });

  useEffect(() => {
    loadAccounts();
  }, []);

  useEffect(() => {
    if (selectedAccount) {
      loadFolders();
    }
  }, [selectedAccount]);

  const loadAccounts = async () => {
    try {
      const response = await fetch(`${API}/api/email/accounts`);
      const data = await response.json();
      setAccounts(data.accounts || []);
      
      if (data.accounts && data.accounts.length > 0 && !selectedAccount) {
        setSelectedAccount(data.accounts[0]);
      }
    } catch (error) {
      console.error('Error loading accounts:', error);
      toast.error('Nie udało się wczytać kont');
    }
  };

  const addAccount = async () => {
    if (!newAccount.email || !newAccount.password) {
      toast.error('Wypełnij wszystkie pola');
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/email/accounts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newAccount)
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Błąd dodawania konta');
      }
      
      toast.success('Konto dodane pomyślnie!');
      setShowAddAccount(false);
      setNewAccount({ email: '', password: '' });
      loadAccounts();
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteAccount = async (accountId) => {
    if (!window.confirm('Czy na pewno chcesz usunąć to konto?')) return;
    
    try {
      await fetch(`${API}/api/email/accounts/${accountId}`, {
        method: 'DELETE'
      });
      
      toast.success('Konto usunięte');
      if (selectedAccount?.id === accountId) {
        setSelectedAccount(null);
        setEmails([]);
      }
      loadAccounts();
    } catch (error) {
      toast.error('Nie udało się usunąć konta');
    }
  };

  const loadFolders = async () => {
    if (!selectedAccount) return;
    
    try {
      const response = await fetch(`${API}/api/email/folders/${selectedAccount.id}`);
      const data = await response.json();
      
      // Mapuj foldery na przyjazne nazwy
      const folderMap = {
        'INBOX': 'Odebrane',
        'Sent': 'Wysłane',
        'Sent Items': 'Wysłane',
        'Drafts': 'Robocze',
        'Trash': 'Kosz',
        'Spam': 'Spam',
        'Junk': 'Spam'
      };
      
      const mappedFolders = (data.folders || ['INBOX']).map(f => ({
        name: f,
        label: folderMap[f] || f
      }));
      
      setFolders(mappedFolders);
    } catch (error) {
      console.error('Error loading folders:', error);
      setFolders([{name: 'INBOX', label: 'Odebrane'}]);
    }
  };

  const loadInbox = async (folder = selectedFolder) => {
    if (!selectedAccount) {
      toast.error('Wybierz konto');
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/email/inbox?account_id=${selectedAccount.id}&folder=${folder}&limit=50`);
      const data = await response.json();
      setEmails(data.emails || []);
      setSelectedFolder(folder);
      toast.success(`Wczytano ${data.count} emaili z ${folder}`);
    } catch (error) {
      toast.error('Nie udało się wczytać emaili');
    } finally {
      setLoading(false);
    }
  };

  const openEmail = async (email) => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/email/message/${selectedAccount.id}/${email.id}`);
      const data = await response.json();
      setSelectedEmail(data);
      setShowEmailDetail(true);
    } catch (error) {
      toast.error('Nie udało się wczytać emaila');
    } finally {
      setLoading(false);
    }
  };

  const sendEmail = async () => {
    if (!composeData.to || !composeData.subject || !composeData.body) {
      toast.error('Wypełnij wszystkie pola');
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/email/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          account_id: selectedAccount.id,
          ...composeData
        })
      });
      
      if (!response.ok) throw new Error('Błąd wysyłania');
      
      toast.success('Email wysłany!');
      setShowCompose(false);
      setComposeData({ to: '', subject: '', body: '' });
    } catch (error) {
      toast.error('Nie udało się wysłać emaila');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Mail className="h-8 w-8 text-blue-600" />
            Poczta Uniwersalna
          </h2>
          <p className="text-gray-600 mt-1">WP.pl, Gmail, O2, Onet, Interia i więcej</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowAddAccount(true)} className="bg-green-600 hover:bg-green-700">
            <Plus className="h-4 w-4 mr-2" />
            Dodaj konto
          </Button>
          {selectedAccount && (
            <>
              <Button onClick={loadInbox} disabled={loading}>
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Odśwież
              </Button>
              <Button onClick={() => setShowCompose(true)} className="bg-blue-600 hover:bg-blue-700">
                <Send className="h-4 w-4 mr-2" />
                Nowy email
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Konta */}
      <Card>
        <CardHeader>
          <CardTitle>Twoje konta email</CardTitle>
        </CardHeader>
        <CardContent>
          {accounts.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Mail className="h-12 w-12 mx-auto mb-3 text-gray-400" />
              <p>Brak kont email</p>
              <p className="text-sm mt-2">Dodaj swoje konto WP.pl lub Gmail</p>
              <Button onClick={() => setShowAddAccount(true)} className="mt-4">
                Dodaj pierwsze konto
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {accounts.map(account => (
                <div
                  key={account.id}
                  onClick={() => setSelectedAccount(account)}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    selectedAccount?.id === account.id
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-400'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold text-gray-900">{account.email}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {account.email.split('@')[1]}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteAccount(account.id);
                      }}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Skrzynka odbiorcza */}
      {selectedAccount && (
        <>
          {/* Foldery */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Inbox className="h-5 w-5" />
                Foldery
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                {folders.map(folder => (
                  <Button
                    key={folder.name}
                    onClick={() => loadInbox(folder.name)}
                    variant={selectedFolder === folder.name ? "default" : "outline"}
                    className="w-full"
                  >
                    {folder.label}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Lista emaili */}
          <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Inbox className="h-5 w-5" />
              {folders.find(f => f.name === selectedFolder)?.label || selectedFolder}: {selectedAccount.email}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {emails.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Inbox className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                <p>Brak emaili</p>
                <Button onClick={loadInbox} className="mt-4">
                  Wczytaj skrzynkę
                </Button>
              </div>
            ) : (
              <div className="space-y-2">
                {emails.map(email => (
                  <div
                    key={email.id}
                    onClick={() => openEmail(email)}
                    className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <p className="font-semibold text-gray-900">{email.subject}</p>
                          {email.has_attachments && (
                            <Paperclip className="h-4 w-4 text-gray-400" />
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{email.from}</p>
                        <p className="text-xs text-gray-500 mt-2 line-clamp-2">{email.body}</p>
                      </div>
                      <div className="text-xs text-gray-500 ml-4">
                        {email.date}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
        </>
      )}

      {/* Modal: Dodaj konto */}
      <Dialog open={showAddAccount} onOpenChange={setShowAddAccount}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Dodaj konto email</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 mt-4">
            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <Input
                type="email"
                placeholder="twoj@wp.pl lub twoj@gmail.com"
                value={newAccount.email}
                onChange={(e) => setNewAccount({ ...newAccount, email: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Hasło aplikacji</label>
              <Input
                type="password"
                placeholder="Hasło do konta email"
                value={newAccount.password}
                onChange={(e) => setNewAccount({ ...newAccount, password: e.target.value })}
              />
              <p className="text-xs text-gray-500 mt-1">
                Dla Gmail: użyj hasła aplikacji z myaccount.google.com/apppasswords
              </p>
            </div>
            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={() => setShowAddAccount(false)}>
                Anuluj
              </Button>
              <Button onClick={addAccount} disabled={loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Dodaj'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal: Napisz email */}
      <Dialog open={showCompose} onOpenChange={setShowCompose}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Nowa wiadomość</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 mt-4">
            <div>
              <label className="block text-sm font-medium mb-2">Do</label>
              <Input
                type="email"
                placeholder="odbiorca@example.com"
                value={composeData.to}
                onChange={(e) => setComposeData({ ...composeData, to: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Temat</label>
              <Input
                placeholder="Temat wiadomości"
                value={composeData.subject}
                onChange={(e) => setComposeData({ ...composeData, subject: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Treść</label>
              <Textarea
                rows={10}
                placeholder="Treść wiadomości..."
                value={composeData.body}
                onChange={(e) => setComposeData({ ...composeData, body: e.target.value })}
              />
            </div>
            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={() => setShowCompose(false)}>
                Anuluj
              </Button>
              <Button onClick={sendEmail} disabled={loading} className="bg-blue-600 hover:bg-blue-700">
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Send className="h-4 w-4 mr-2" />}
                Wyślij
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal: Szczegóły emaila */}
      <Dialog open={showEmailDetail} onOpenChange={setShowEmailDetail}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                {selectedEmail?.subject}
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowEmailDetail(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </DialogTitle>
          </DialogHeader>
          
          {selectedEmail && (
            <div className="space-y-4 mt-4">
              <div className="border-b pb-4">
                <p className="text-sm text-gray-600">Od: <span className="font-medium text-gray-900">{selectedEmail.from}</span></p>
                <p className="text-sm text-gray-600 mt-1">Do: <span className="font-medium text-gray-900">{selectedEmail.to}</span></p>
                <p className="text-sm text-gray-600 mt-1">Data: <span className="font-medium text-gray-900">{selectedEmail.date}</span></p>
              </div>
              
              {selectedEmail.attachments && selectedEmail.attachments.length > 0 && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm font-medium mb-2 flex items-center gap-2">
                    <Paperclip className="h-4 w-4" />
                    Załączniki ({selectedEmail.attachments.length})
                  </p>
                  {selectedEmail.attachments.map((att, idx) => (
                    <div key={idx} className="text-sm text-gray-700 mt-1">
                      📎 {att.filename} ({(att.size / 1024).toFixed(1)} KB)
                    </div>
                  ))}
                </div>
              )}
              
              <div className="bg-white border rounded-lg p-4">
                <div className="whitespace-pre-wrap text-sm text-gray-900 font-sans break-words">
                  {selectedEmail.body_text || 'Brak treści'}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default UniversalMail;
