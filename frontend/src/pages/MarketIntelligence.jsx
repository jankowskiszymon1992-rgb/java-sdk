import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TrendingUp, DollarSign, RefreshCw, Package, AlertCircle, Plus, Trash2, Search, X } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MarketIntelligence = () => {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [products, setProducts] = useState([]);
  const [showProductDialog, setShowProductDialog] = useState(false);
  const [newProduct, setNewProduct] = useState({
    name: '',
    category: 'przewody',
    usd_sensitive: false
  });
  const [productSearchQuery, setProductSearchQuery] = useState('');

  useEffect(() => {
    loadDashboard();
    loadProducts();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await axios.get(`${API}/market-intelligence/dashboard`);
      setDashboard(response.data);
    } catch (error) {
      console.error('Błąd ładowania dashboardu:', error);
      toast.error('Nie udało się załadować danych');
    } finally {
      setLoading(false);
    }
  };

  const loadProducts = async () => {
    try {
      const response = await axios.get(`${API}/market-intelligence/products`);
      setProducts(response.data.products || []);
    } catch (error) {
      console.error('Błąd ładowania produktów:', error);
    }
  };

  const handleAddProduct = async () => {
    if (!newProduct.name.trim()) {
      toast.error('Podaj nazwę produktu');
      return;
    }

    try {
      await axios.post(`${API}/market-intelligence/products`, newProduct);
      toast.success('Produkt dodany pomyślnie');
      setNewProduct({ name: '', category: 'przewody', usd_sensitive: false });
      setShowProductDialog(false);
      loadProducts();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Błąd dodawania produktu');
    }
  };

  const handleDeleteProduct = async (productId, productName) => {
    if (!window.confirm(`Czy na pewno usunąć produkt "${productName}"?`)) {
      return;
    }

    try {
      await axios.delete(`${API}/market-intelligence/products/${productId}`);
      toast.success('Produkt usunięty');
      loadProducts();
    } catch (error) {
      toast.error('Błąd usuwania produktu');
    }
  };

  const handleScrape = async () => {
    setScraping(true);
    toast.info('Rozpoczynam scraping cen...');
    
    try {
      const response = await axios.post(`${API}/market-intelligence/scrape`);
      toast.success(`Scraping zakończony! Pobrano ${response.data.total_suppliers} hurtowni`);
      loadDashboard();
    } catch (error) {
      console.error('Błąd scrapingu:', error);
      toast.error('Błąd podczas scrapingu');
    } finally {
      setScraping(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12">Ładowanie...</div>;
  }

  const usdRate = dashboard?.usd_rate;
  const priceComparison = dashboard?.price_comparison?.products || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Inteligencja Rynkowa</h2>
          <p className="text-gray-600 mt-1">Monitoring cen i trendów rynkowych</p>
        </div>
        <Button 
          onClick={handleScrape} 
          disabled={scraping}
          className="bg-blue-600 hover:bg-blue-700"
        >
          {scraping ? (
            <>
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              Pobieram dane...
            </>
          ) : (
            <>
              <RefreshCw className="h-4 w-4 mr-2" />
              Aktualizuj ceny
            </>
          )}
        </Button>
      </div>

      {/* Karty podsumowania */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Kurs USD */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Kurs USD/PLN</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {usdRate ? (
              <>
                <div className="text-2xl font-bold">{usdRate.rate.toFixed(4)} PLN</div>
                <p className="text-xs text-muted-foreground">
                  Data: {usdRate.date} (NBP)
                </p>
              </>
            ) : (
              <p className="text-sm text-gray-500">Brak danych</p>
            )}
          </CardContent>
        </Card>

        {/* Monitorowane produkty */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monitorowane produkty</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboard?.monitored_products || 0}</div>
            <p className="text-xs text-muted-foreground">
              Aktywne produkty
            </p>
          </CardContent>
        </Card>

        {/* Alerty */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Alerty cenowe</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboard?.unread_alerts || 0}</div>
            <p className="text-xs text-muted-foreground">
              Nieprzeczytane
            </p>
          </CardContent>
        </Card>
      </div>



      {/* Zarządzanie produktami */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center">
              <Package className="h-5 w-5 mr-2 text-blue-600" />
              Zarządzanie Produktami
            </CardTitle>
            <Dialog open={showProductDialog} onOpenChange={setShowProductDialog}>
              <DialogTrigger asChild>
                <Button size="sm" className="bg-green-600 hover:bg-green-700">
                  <Plus className="h-4 w-4 mr-2" />
                  Dodaj produkt
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Dodaj nowy produkt</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div>
                    <Label htmlFor="product-name">Nazwa produktu</Label>
                    <Input
                      id="product-name"
                      placeholder="np. Kabel YDYp 3x1.5mm"
                      value={newProduct.name}
                      onChange={(e) => setNewProduct({...newProduct, name: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label htmlFor="product-category">Kategoria</Label>
                    <Select
                      value={newProduct.category}
                      onValueChange={(value) => setNewProduct({...newProduct, category: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="przewody">Przewody</SelectItem>
                        <SelectItem value="gniazda">Gniazda i wtyczki</SelectItem>
                        <SelectItem value="lampy">Lampy LED</SelectItem>
                        <SelectItem value="wylaczniki">Wyłączniki</SelectItem>
                        <SelectItem value="puszki">Puszki i osprzęt</SelectItem>
                        <SelectItem value="narzedzia">Narzędzia</SelectItem>
                        <SelectItem value="inne">Inne</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="usd-sensitive"
                      checked={newProduct.usd_sensitive}
                      onChange={(e) => setNewProduct({...newProduct, usd_sensitive: e.target.checked})}
                      className="h-4 w-4"
                    />
                    <Label htmlFor="usd-sensitive">Wrażliwy na kurs USD (np. kable miedziane)</Label>
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setShowProductDialog(false)}>
                    Anuluj
                  </Button>
                  <Button onClick={handleAddProduct} className="bg-green-600 hover:bg-green-700">
                    Dodaj produkt
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          {products.length === 0 ? (
            <div className="text-center py-8">
              <Package className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600">Brak monitorowanych produktów</p>
              <p className="text-sm text-gray-500 mt-2">
                Kliknij "Dodaj produkt" aby rozpocząć monitorowanie cen
              </p>
            </div>
          ) : (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {products.map((product) => (
                <div
                  key={product.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{product.name}</h4>
                    <p className="text-sm text-gray-500">
                      Kategoria: {product.category}
                      {product.usd_sensitive && ' • Wrażliwy na USD'}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteProduct(product.id, product.name)}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Porównanie cen */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
            Porównanie Cen Produktów
          </CardTitle>
        </CardHeader>
        <CardContent>
          {priceComparison.length === 0 ? (
            <div className="text-center py-12">
              <Package className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600">Brak danych o cenach</p>
              <p className="text-sm text-gray-500 mt-2">
                Kliknij "Aktualizuj ceny" aby pobrać aktualne ceny z hurtowni
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {priceComparison.map((product, idx) => (
                <div key={idx} className="border rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-3">{product._id}</h4>
                  
                  {/* Statystyki */}
                  {product.min_price && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
                      <div>
                        <span className="text-gray-500">Min:</span>
                        <span className="ml-2 font-semibold text-green-600">
                          {product.min_price.toFixed(2)} PLN
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Max:</span>
                        <span className="ml-2 font-semibold text-red-600">
                          {product.max_price.toFixed(2)} PLN
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Średnia:</span>
                        <span className="ml-2 font-semibold">
                          {product.avg_price.toFixed(2)} PLN
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Rozpiętość:</span>
                        <span className="ml-2 font-semibold">
                          {product.spread_percent.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  )}
                  
                  {/* Tabela cen */}
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Hurtownia
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Cena
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Dostępność
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Ostatnia aktualizacja
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {product.prices.map((price, pidx) => (
                          <tr key={pidx} className="hover:bg-gray-50">
                            <td className="px-4 py-3 text-sm font-medium text-gray-900 capitalize">
                              {price.supplier.replace('_', ' ')}
                            </td>
                            <td className="px-4 py-3 text-sm">
                              <span className={`font-semibold ${
                                price.price === product.min_price ? 'text-green-600' :
                                price.price === product.max_price ? 'text-red-600' :
                                'text-gray-900'
                              }`}>
                                {price.price.toFixed(2)} PLN
                              </span>
                            </td>
                            <td className="px-4 py-3 text-sm">
                              {price.availability ? (
                                <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                                  Dostępny
                                </span>
                              ) : (
                                <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded">
                                  Niedostępny
                                </span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-500">
                              {price.scraped_at ? new Date(price.scraped_at).toLocaleString('pl-PL') : '-'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Info */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
            <div className="text-sm text-blue-900">
              <p className="font-medium mb-1">Informacje o systemie:</p>
              <ul className="list-disc list-inside space-y-1 text-blue-800">
                <li>System monitoruje ceny z 4 hurtowni: Kanlux, TME, Conrad, RS Components</li>
                <li>Automatyczna aktualizacja codziennie o 6:00 rano</li>
                <li>Kurs USD pobierany z API NBP</li>
                <li>Alerty o zmianach cen powyżej 5%</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MarketIntelligence;
