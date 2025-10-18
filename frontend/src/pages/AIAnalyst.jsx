import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Brain, TrendingUp, Lightbulb, AlertTriangle, RefreshCw, FileText, ArrowUp, ArrowDown, Minus } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AIAnalyst = () => {
  const [latestReport, setLatestReport] = useState(null);
  const [comparisonTable, setComparisonTable] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [reportsRes, tableRes] = await Promise.all([
        axios.get(`${API}/ai-analyst/reports?limit=1`),
        axios.get(`${API}/ai-analyst/comparison-table`)
      ]);
      
      if (reportsRes.data.reports && reportsRes.data.reports.length > 0) {
        setLatestReport(reportsRes.data.reports[0]);
      }
      setComparisonTable(tableRes.data);
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

  if (loading) {
    return <div className="text-center py-12">Ładowanie...</div>;
  }

  const usdTrendIcon = comparisonTable?.usd_trend === 'rising' ? ArrowUp : 
                       comparisonTable?.usd_trend === 'falling' ? ArrowDown : Minus;
  const usdTrendColor = comparisonTable?.usd_trend === 'rising' ? 'text-red-600' : 
                        comparisonTable?.usd_trend === 'falling' ? 'text-green-600' : 'text-gray-600';

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 flex items-center">
            <Brain className="h-8 w-8 mr-3 text-purple-600" />
            AI Analityk
          </h2>
          <p className="text-gray-600 mt-1">Inteligentna analiza rynku i rekomendacje</p>
        </div>
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
              Generuj Raport
            </>
          )}
        </Button>
      </div>

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
