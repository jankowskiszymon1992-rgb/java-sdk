import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Brain, TrendingUp, Lightbulb, AlertTriangle, RefreshCw, FileText, ArrowUp, ArrowDown, Minus, X, Trash2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AIAnalyst = () => {
  const [latestReport, setLatestReport] = useState(null);
  const [comparisonTable, setComparisonTable] = useState(null);
  const [trendAnalysis, setTrendAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [analyzingTrends, setAnalyzingTrends] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [reportsRes, tableRes, trendRes] = await Promise.all([
        axios.get(`${API}/ai-analyst/reports?limit=1`),
        axios.get(`${API}/ai-analyst/comparison-table`),
        axios.get(`${API}/ai-analyst/latest-trend-analysis`)
      ]);
      
      if (reportsRes.data.reports && reportsRes.data.reports.length > 0) {
        setLatestReport(reportsRes.data.reports[0]);
      }
      setComparisonTable(tableRes.data);
      if (trendRes.data && !trendRes.data.message) {
        setTrendAnalysis(trendRes.data);
      }
    } catch (error) {
      console.error('Błąd ładowania danych:', error);
      toast.error('Nie udało się załadować danych');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    setGenerating(true);
    toast.info('Generuję raport AI... To może potrwać 10-30 sekund');
    
    try {
      const response = await axios.post(`${API}/ai-analyst/generate-report`, null, {
        params: { report_type: 'on_demand' }
      });
      setLatestReport(response.data);
      toast.success('Raport wygenerowany!');
      loadData();
    } catch (error) {
      console.error('Błąd generowania raportu:', error);
      toast.error('Nie udało się wygenerować raportu');
    } finally {
      setGenerating(false);
    }
  };

  const handleAnalyzeTrends = async () => {
    setAnalyzingTrends(true);
    toast.info('GPT-5 analizuje trendy... To może potrwać 15-30 sekund');
    
    try {
      const response = await axios.post(`${API}/ai-analyst/trend-analysis`);
      setTrendAnalysis(response.data);
      toast.success('Analiza trendów gotowa!');
    } catch (error) {
      console.error('Błąd analizy trendów:', error);
      toast.error('Nie udało się przeanalizować trendów');
    } finally {
      setAnalyzingTrends(false);
    }
  };

  const startNewConversation = () => {
    setSessionId(null);
    setChatMessages([]);
    toast.success('Rozpoczęto nową rozmowę');
  };

  const loadSessions = async () => {
    console.log('🔍 [AI Analyst] loadSessions wywołana!'); // DEBUG
    try {
      // Cache busting - dodaj timestamp
      const cacheBuster = `?limit=50&_t=${Date.now()}`;
      console.log('📡 [AI Analyst] Wysyłam request do:', `${API}/ai-analyst/chat/sessions${cacheBuster}`); // DEBUG
      
      const response = await axios.get(`${API}/ai-analyst/chat/sessions${cacheBuster}`);
      console.log('✅ [AI Analyst] Odpowiedź:', response.data); // DEBUG
      
      setSessions(response.data.sessions || []);
      setShowHistory(true);
      console.log('✅ [AI Analyst] Historia załadowana, sessions:', response.data.sessions?.length); // DEBUG
      toast.success('Historia załadowana!'); // Potwierdzenie wizualne
    } catch (error) {
      console.error('❌ [AI Analyst] Błąd ładowania historii:', error); // DEBUG
      toast.error('Nie udało się załadować historii');
      alert('Błąd: ' + (error.response?.data?.detail || error.message)); // ALERT
    }
  };

  const loadSession = async (sid) => {
    try {
      console.log('📥 [AI Analyst] Ładuję sesję:', sid); // DEBUG
      // Cache busting dla pojedynczej sesji
      const response = await axios.get(`${API}/ai-analyst/chat/history?session_id=${sid}&_t=${Date.now()}`);
      
      console.log('📦 [AI Analyst] Odpowiedź z backendu:', response.data); // DEBUG
      const history = response.data.history || [];
      console.log('💬 [AI Analyst] Liczba wiadomości:', history.length); // DEBUG
      
      // Format messages poprawnie
      const loadedMessages = [];
      history.forEach(h => {
        loadedMessages.push({ role: 'user', content: h.user_message });
        loadedMessages.push({ role: 'assistant', content: h.ai_response });
      });
      
      console.log('✅ [AI Analyst] Załadowane wiadomości:', loadedMessages.length); // DEBUG
      setChatMessages(loadedMessages);
      setSessionId(sid);
      setShowHistory(false);
      toast.success('Wczytano rozmowę');
    } catch (error) {
      console.error('❌ [AI Analyst] Błąd ładowania rozmowy:', error);
      toast.error('Nie udało się wczytać rozmowy');
      alert('Błąd ładowania sesji: ' + (error.response?.data?.detail || error.message));
    }
  };

  const deleteSession = async (sid, event) => {
    event.stopPropagation(); // Zapobiegaj kliknięciu na sesję
    
    if (!window.confirm('Czy na pewno chcesz usunąć tę rozmowę?')) {
      return;
    }
    
    try {
      await axios.delete(`${API}/ai-analyst/chat/sessions/${sid}?_t=${Date.now()}`);
      // Odśwież listę sesji
      setSessions(prev => prev.filter(s => s.session_id !== sid));
      toast.success('Rozmowa usunięta');
      console.log('✅ [AI Analyst] Sesja usunięta:', sid); // DEBUG
    } catch (error) {
      console.error('❌ [AI Analyst] Błąd usuwania sesji:', error);
      toast.error('Nie udało się usunąć rozmowy');
      alert('Błąd usuwania: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;
    
    const userMessage = chatInput;
    setChatInput('');
    
    // Dodaj wiadomość użytkownika
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatLoading(true);
    
    try {
      const response = await axios.post(`${API}/ai-analyst/chat`, null, {
        params: { 
          message: userMessage,
          session_id: sessionId
        }
      });
      
      // Zapisz session_id
      if (!sessionId && response.data.session_id) {
        setSessionId(response.data.session_id);
      }
      
      // Dodaj odpowiedź AI
      setChatMessages(prev => [...prev, { role: 'assistant', content: response.data.response }]);
    } catch (error) {
      console.error('Błąd czatu:', error);
      toast.error('Nie udało się wysłać wiadomości');
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Przepraszam, wystąpił błąd. Spróbuj ponownie.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12">Ładowanie...</div>;
  }

  const usdTrendIcon = comparisonTable?.usd_trend === 'rising' ? ArrowUp : 
                       comparisonTable?.usd_trend === 'falling' ? ArrowDown : Minus;
  const usdTrendColor = comparisonTable?.usd_trend === 'rising' ? 'text-red-600' : 
                        comparisonTable?.usd_trend === 'falling' ? 'text-green-600' : 'text-gray-600';

  return (
    <div className="space-y-6">
      {/* Modal Historii Czatu */}
      <Dialog open={showHistory} onOpenChange={setShowHistory}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-purple-600" />
                Historia Czatu AI Analityk
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowHistory(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-3 mt-4">
            {sessions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Brain className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                <p>Brak zapisanych rozmów</p>
              </div>
            ) : (
              sessions.map((session, idx) => (
                <div
                  key={session.session_id || idx}
                  className="p-4 border rounded-lg hover:bg-purple-50 transition-colors relative group"
                >
                  <div 
                    onClick={() => loadSession(session.session_id)}
                    className="cursor-pointer"
                  >
                    <div className="flex justify-between items-start pr-8">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">
                          {session.title || `Analiza ${idx + 1}`}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1">
                          {session.message_count || 0} wiadomości
                        </p>
                        {session.last_message && (
                          <p className="text-xs text-gray-500 mt-2 line-clamp-2">
                            {session.last_message}
                          </p>
                        )}
                      </div>
                      <div className="text-xs text-gray-500">
                        {session.updated_at
                          ? new Date(session.updated_at).toLocaleDateString('pl-PL')
                          : 'Brak daty'}
                      </div>
                    </div>
                  </div>
                  
                  {/* Przycisk Usuń */}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => deleteSession(session.session_id, e)}
                    className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity text-red-600 hover:text-red-700 hover:bg-red-50"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))
            )}
          </div>

          <div className="mt-4 pt-4 border-t flex justify-end">
            <Button
              variant="outline"
              onClick={() => setShowHistory(false)}
            >
              Zamknij
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 flex items-center">
            <Brain className="h-8 w-8 mr-3 text-purple-600" />
            AI Analityk
          </h2>
          <p className="text-gray-600 mt-1">Inteligentna analiza rynku i rekomendacje</p>
        </div>
        <div className="flex gap-3">
          <Button 
            onClick={handleAnalyzeTrends} 
            disabled={analyzingTrends}
            className="bg-green-600 hover:bg-green-700"
          >
            {analyzingTrends ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Analizuję...
              </>
            ) : (
              <>
                <TrendingUp className="h-4 w-4 mr-2" />
                Analizuj Trendy (GPT-5)
              </>
            )}
          </Button>
          <Button 
            onClick={handleGenerateReport} 
            disabled={generating}
            className="bg-purple-600 hover:bg-purple-700"
          >
            {generating ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Generuję...
              </>
            ) : (
              <>
                <Brain className="h-4 w-4 mr-2" />
                Raport (Claude)
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Analiza Trendów GPT-5 */}
      {trendAnalysis && (
        <Card className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200">
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-6 w-6 mr-2 text-green-600" />
              Analiza Trendów - GPT-5
            </CardTitle>
            <p className="text-sm text-gray-600 mt-2">{trendAnalysis.summary}</p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {trendAnalysis.products?.map((product, idx) => (
                <div 
                  key={idx} 
                  className={`p-4 rounded-lg border-2 ${
                    product.rekomendacja === 'KUP_TERAZ' 
                      ? 'bg-green-50 border-green-300' 
                      : 'bg-yellow-50 border-yellow-300'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-semibold text-sm text-gray-900">{product.nazwa}</h4>
                    <span className={`text-xs px-2 py-1 rounded font-bold ${
                      product.rekomendacja === 'KUP_TERAZ'
                        ? 'bg-green-600 text-white'
                        : 'bg-yellow-600 text-white'
                    }`}>
                      {product.rekomendacja === 'KUP_TERAZ' ? '✅ KUP' : '⏳ CZEKAJ'}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`text-xs font-semibold ${
                      product.trend === 'DROŻEJE' ? 'text-red-600' :
                      product.trend === 'TANIEJE' ? 'text-green-600' :
                      'text-gray-600'
                    }`}>
                      {product.trend === 'DROŻEJE' && '📈 DROŻEJE'}
                      {product.trend === 'TANIEJE' && '📉 TANIEJE'}
                      {product.trend === 'STABILNY' && '➡️ STABILNY'}
                    </span>
                    <span className="text-xs text-gray-500">
                      ({product.confidence}% pewności)
                    </span>
                  </div>
                  
                  <p className="text-xs text-gray-700">{product.uzasadnienie}</p>
                </div>
              ))}
            </div>
            
            {trendAnalysis.key_insights && trendAnalysis.key_insights.length > 0 && (
              <div className="mt-6 p-4 bg-white rounded-lg border border-green-200">
                <h4 className="font-semibold text-gray-900 mb-3">Kluczowe Wnioski:</h4>
                <ul className="space-y-2">
                  {trendAnalysis.key_insights.map((insight, idx) => (
                    <li key={idx} className="flex items-start">
                      <span className="text-green-600 mr-2">•</span>
                      <span className="text-sm text-gray-800">{insight}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Chat z GPT-5 */}
      <Card className="border-2 border-blue-200">
        <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50">
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="flex items-center">
                <Brain className="h-5 w-5 mr-2 text-blue-600" />
                Zapytaj GPT-5 o Produkty i Ceny
              </CardTitle>
              <p className="text-sm text-gray-600 mt-2">
                Zadawaj pytania np: "Czy powinienem kupić przewody teraz?" lub "Co jest teraz najtańsze?"
              </p>
            </div>
            <div className="flex gap-2">
              <Button 
                onClick={() => {
                  console.log('🔘 [AI Analyst] Przycisk Historia kliknięty!'); // DEBUG
                  loadSessions();
                }} 
                variant="outline" 
                size="sm" 
                className="text-xs"
              >
                📜 Historia
              </Button>
              <Button onClick={startNewConversation} variant="outline" size="sm" className="text-xs">
                ➕ Nowa rozmowa
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Historia czatu */}
          <div className="space-y-3 mb-4 max-h-96 overflow-y-auto p-4 bg-gray-50 rounded-lg">
            {chatMessages.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Brain className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                <p>Zacznij rozmowę z GPT-5!</p>
                <p className="text-sm mt-2">Przykłady pytań:</p>
                <ul className="text-sm mt-2 space-y-1">
                  <li>"Które przewody są teraz najtańsze?"</li>
                  <li>"Czy ceny naświetlaczy rosną?"</li>
                  <li>"Od kogo kupić gniazdka Simon 54?"</li>
                </ul>
              </div>
            ) : (
              chatMessages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] p-3 rounded-lg ${
                    msg.role === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-white border border-gray-200 text-gray-900'
                  }`}>
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))
            )}
            {chatLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 p-3 rounded-lg">
                  <RefreshCw className="h-4 w-4 animate-spin text-blue-600" />
                </div>
              </div>
            )}
          </div>

          {/* Input czatu */}
          <div className="flex gap-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Wpisz pytanie..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={chatLoading}
            />
            <Button 
              onClick={handleSendMessage}
              disabled={chatLoading || !chatInput.trim()}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {chatLoading ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                'Wyślij'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Tabela Porównawcza z Obliczeniami */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
            Tabela Porównawcza z Analizą
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* USD Info */}
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <div className="flex justify-between items-center">
              <div>
                <span className="text-sm text-gray-600">Kurs USD/PLN:</span>
                <span className="ml-2 text-lg font-bold">
                  {comparisonTable?.usd_rate?.rate.toFixed(4)} PLN
                </span>
              </div>
              <div className={`flex items-center ${usdTrendColor}`}>
                {React.createElement(usdTrendIcon, { className: 'h-5 w-5 mr-1' })}
                <span className="font-semibold">
                  {comparisonTable?.usd_change_7d > 0 ? '+' : ''}
                  {comparisonTable?.usd_change_7d}% (7 dni)
                </span>
              </div>
            </div>
          </div>

          {/* Produkty */}
          <div className="space-y-4">
            {comparisonTable?.products?.map((product, idx) => (
              <div key={idx} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="font-semibold text-gray-900">{product._id}</h4>
                    {product.usd_sensitive && (
                      <span className="inline-block mt-1 px-2 py-0.5 text-xs bg-yellow-100 text-yellow-800 rounded">
                        Wrażliwy na USD
                      </span>
                    )}
                  </div>
                  <span className={`px-3 py-1 text-sm font-semibold rounded ${
                    product.competitiveness === 'high' ? 'bg-green-100 text-green-800' :
                    product.competitiveness === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {product.competitiveness === 'high' ? 'Wysoka konkurencja' :
                     product.competitiveness === 'medium' ? 'Średnia konkurencja' : 'Niska konkurencja'}
                  </span>
                </div>

                {/* Metryki */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4 p-3 bg-gray-50 rounded">
                  <div>
                    <span className="text-xs text-gray-500 block">Min cena</span>
                    <span className="font-bold text-green-600">{product.min_price?.toFixed(2)} PLN</span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500 block">Max cena</span>
                    <span className="font-bold text-red-600">{product.max_price?.toFixed(2)} PLN</span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500 block">Średnia</span>
                    <span className="font-bold">{product.avg_price?.toFixed(2)} PLN</span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500 block">Oszczędność</span>
                    <span className="font-bold text-purple-600">{product.savings_percent}%</span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500 block">Kwota</span>
                    <span className="font-bold text-purple-600">{product.savings_amount?.toFixed(2)} PLN</span>
                  </div>
                </div>

                {/* Rekomendacja */}
                {product.cheapest_supplier && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded flex items-start">
                    <Lightbulb className="h-5 w-5 text-green-600 mr-2 mt-0.5" />
                    <div className="text-sm">
                      <span className="font-semibold text-green-900">Najlepsza oferta:</span>
                      <span className="ml-2 text-green-800 capitalize">
                        {product.cheapest_supplier.replace('_', ' ')} - oszczędzasz {product.savings_amount?.toFixed(2)} PLN
                        ({product.savings_percent}%) vs najdroższy
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Raport AI */}
      {latestReport && (
        <>
          {/* Podsumowanie */}
          <Card className="bg-gradient-to-r from-purple-50 to-blue-50">
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2 text-purple-600" />
                {latestReport.title}
              </CardTitle>
              <p className="text-sm text-gray-600">
                Wygenerowano: {new Date(latestReport.created_at).toLocaleString('pl-PL')}
              </p>
            </CardHeader>
            <CardContent>
              <p className="text-gray-800 leading-relaxed">{latestReport.summary}</p>
            </CardContent>
          </Card>

          {/* Rekomendacje */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Lightbulb className="h-5 w-5 mr-2 text-yellow-600" />
                Rekomendacje AI
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {latestReport.recommendations?.map((rec, idx) => (
                  <li key={idx} className="flex items-start p-3 bg-yellow-50 border border-yellow-200 rounded">
                    <span className="flex-shrink-0 w-6 h-6 bg-yellow-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
                      {idx + 1}
                    </span>
                    <span className="text-gray-800">{rec}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Predykcje */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
                Predykcje
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {latestReport.predictions?.map((pred, idx) => (
                  <li key={idx} className="flex items-start p-3 bg-blue-50 border border-blue-200 rounded">
                    <TrendingUp className="h-5 w-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-800">{pred}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Kluczowe Wnioski */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <AlertTriangle className="h-5 w-5 mr-2 text-orange-600" />
                Kluczowe Wnioski
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {latestReport.key_insights?.map((insight, idx) => (
                  <li key={idx} className="flex items-start p-3 bg-orange-50 border border-orange-200 rounded">
                    <span className="flex-shrink-0 w-2 h-2 bg-orange-600 rounded-full mr-3 mt-2"></span>
                    <span className="text-gray-800">{insight}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Pełna Analiza */}
          <Card>
            <CardHeader>
              <CardTitle>Szczegółowa Analiza</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose prose-sm max-w-none">
                <pre className="whitespace-pre-wrap text-sm text-gray-800 leading-relaxed">
                  {latestReport.analysis}
                </pre>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {!latestReport && (
        <Card className="text-center py-12">
          <CardContent>
            <Brain className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Brak raportów</h3>
            <p className="text-gray-600 mb-6">
              Kliknij "Generuj Raport" aby AI przeanalizował aktualne dane rynkowe
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AIAnalyst;
