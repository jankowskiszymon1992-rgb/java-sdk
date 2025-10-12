import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Cable, Shield, TrendingDown, Zap, Power, Lightbulb } from 'lucide-react';

const ElectricalCalculators = () => {
  // Wire size calculator
  const [wireCurrent, setWireCurrent] = useState('');
  const [wireLength, setWireLength] = useState('');
  const [wireVoltage, setWireVoltage] = useState('230');
  const [wireType, setWireType] = useState('copper');
  const [wireResult, setWireResult] = useState(null);

  // Voltage drop calculator
  const [dropCurrent, setDropCurrent] = useState('');
  const [dropLength, setDropLength] = useState('');
  const [dropCrossSection, setDropCrossSection] = useState('');
  const [dropVoltage, setDropVoltage] = useState('230');
  const [dropResult, setDropResult] = useState(null);

  // Breaker calculator
  const [breakerPower, setBreakerPower] = useState('');
  const [breakerVoltage, setBreakerVoltage] = useState('230');
  const [breakerPhases, setBreakerPhases] = useState('1');
  const [breakerResult, setBreakerResult] = useState(null);

  // Ohm's Law calculator
  const [ohmVoltage, setOhmVoltage] = useState('');
  const [ohmCurrent, setOhmCurrent] = useState('');
  const [ohmResistance, setOhmResistance] = useState('');
  const [ohmPower, setOhmPower] = useState('');

  // Power calculator
  const [powerVoltage, setPowerVoltage] = useState('');
  const [powerCurrent, setPowerCurrent] = useState('');
  const [powerPF, setPowerPF] = useState('1');
  const [powerResult, setPowerResult] = useState(null);

  // Wire size calculation
  const calculateWireSize = () => {
    const current = parseFloat(wireCurrent);
    const length = parseFloat(wireLength);
    const voltage = parseFloat(wireVoltage);

    if (!current || !length) return;

    // Simplified wire sizing based on current and length
    // For copper wire at 230V with 3% voltage drop
    const k = wireType === 'copper' ? 56 : 35; // Conductivity
    const maxDrop = voltage * 0.03; // 3% voltage drop
    
    // A = (2 * I * L * cosφ) / (κ * ΔU)
    const crossSection = (2 * current * length) / (k * maxDrop);

    // Standard wire sizes
    const standardSizes = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240];
    const recommendedSize = standardSizes.find(size => size >= crossSection) || standardSizes[standardSizes.length - 1];

    // Maximum current for recommended size (approximate)
    const maxCurrentMap = {
      1.5: 16, 2.5: 21, 4: 27, 6: 35, 10: 46, 16: 61, 25: 80,
      35: 100, 50: 125, 70: 160, 95: 195, 120: 230, 150: 265,
      185: 310, 240: 375
    };

    setWireResult({
      calculated: crossSection.toFixed(2),
      recommended: recommendedSize,
      maxCurrent: maxCurrentMap[recommendedSize] || 'N/A',
      type: wireType === 'copper' ? 'miedź' : 'aluminium'
    });
  };

  // Voltage drop calculation
  const calculateVoltageDrop = () => {
    const current = parseFloat(dropCurrent);
    const length = parseFloat(dropLength);
    const crossSection = parseFloat(dropCrossSection);
    const voltage = parseFloat(dropVoltage);

    if (!current || !length || !crossSection) return;

    const k = 56; // Copper conductivity
    const drop = (2 * current * length) / (k * crossSection);
    const dropPercent = (drop / voltage) * 100;

    setDropResult({
      voltageDrop: drop.toFixed(2),
      percentage: dropPercent.toFixed(2),
      acceptable: dropPercent <= 3
    });
  };

  // Breaker calculation
  const calculateBreaker = () => {
    const power = parseFloat(breakerPower);
    const voltage = parseFloat(breakerVoltage);
    const phases = parseInt(breakerPhases);

    if (!power || !voltage) return;

    let current;
    if (phases === 1) {
      current = power / voltage;
    } else {
      current = power / (Math.sqrt(3) * voltage);
    }

    // Standard breaker sizes
    const standardBreakers = [6, 10, 13, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125];
    const recommended = standardBreakers.find(b => b >= current * 1.25) || standardBreakers[standardBreakers.length - 1];

    setBreakerResult({
      current: current.toFixed(2),
      recommended: recommended,
      type: phases === 1 ? 'jednofazowy' : 'trójfazowy'
    });
  };

  // Ohm's Law calculations
  const calculateOhmsLaw = (type) => {
    const V = parseFloat(ohmVoltage);
    const I = parseFloat(ohmCurrent);
    const R = parseFloat(ohmResistance);
    const P = parseFloat(ohmPower);

    switch(type) {
      case 'voltage':
        if (I && R) setOhmVoltage((I * R).toFixed(2));
        else if (P && I) setOhmVoltage((P / I).toFixed(2));
        break;
      case 'current':
        if (V && R) setOhmCurrent((V / R).toFixed(2));
        else if (P && V) setOhmCurrent((P / V).toFixed(2));
        break;
      case 'resistance':
        if (V && I) setOhmResistance((V / I).toFixed(2));
        break;
      case 'power':
        if (V && I) setOhmPower((V * I).toFixed(2));
        else if (I && R) setOhmPower((I * I * R).toFixed(2));
        break;
      default:
        break;
    }
  };

  // Power calculation
  const calculatePower = () => {
    const voltage = parseFloat(powerVoltage);
    const current = parseFloat(powerCurrent);
    const pf = parseFloat(powerPF);

    if (!voltage || !current) return;

    const apparentPower = voltage * current;
    const activePower = apparentPower * pf;
    const reactivePower = Math.sqrt(apparentPower * apparentPower - activePower * activePower);

    setPowerResult({
      apparent: apparentPower.toFixed(2),
      active: activePower.toFixed(2),
      reactive: reactivePower.toFixed(2),
      powerFactor: pf
    });
  };

  return (
    <div className="space-y-6">
      <Tabs defaultValue="wire" className="w-full">
        <TabsList className="grid w-full grid-cols-3 lg:grid-cols-6">
          <TabsTrigger value="wire">Przewody</TabsTrigger>
          <TabsTrigger value="drop">Spadek U</TabsTrigger>
          <TabsTrigger value="breaker">Bezpieczniki</TabsTrigger>
          <TabsTrigger value="ohm">Prawo Ohma</TabsTrigger>
          <TabsTrigger value="power">Moc</TabsTrigger>
          <TabsTrigger value="tips">Wskazówki</TabsTrigger>
        </TabsList>

        {/* Wire Size Calculator */}
        <TabsContent value="wire">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Cable className="h-5 w-5 text-yellow-600" />
                <span>Dobór przekroju przewodu</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="wire-current">Prąd obciążenia (A)</Label>
                  <Input
                    id="wire-current"
                    type="number"
                    value={wireCurrent}
                    onChange={(e) => setWireCurrent(e.target.value)}
                    placeholder="np. 16"
                  />
                </div>
                <div>
                  <Label htmlFor="wire-length">Długość trasy (m)</Label>
                  <Input
                    id="wire-length"
                    type="number"
                    value={wireLength}
                    onChange={(e) => setWireLength(e.target.value)}
                    placeholder="np. 25"
                  />
                </div>
                <div>
                  <Label htmlFor="wire-voltage">Napięcie (V)</Label>
                  <Select value={wireVoltage} onValueChange={setWireVoltage}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="230">230V (jednofazowe)</SelectItem>
                      <SelectItem value="400">400V (trójfazowe)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="wire-type">Materiał</Label>
                  <Select value={wireType} onValueChange={setWireType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="copper">Miedź (Cu)</SelectItem>
                      <SelectItem value="aluminum">Aluminium (Al)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <Button onClick={calculateWireSize} className="bg-yellow-500 hover:bg-yellow-600 w-full">
                Oblicz przekrój
              </Button>
              {wireResult && (
                <Alert className="bg-green-50 border-green-200">
                  <AlertDescription>
                    <div className="space-y-2">
                      <p className="font-bold text-lg">Wyniki:</p>
                      <p>• Obliczony przekrój: <strong>{wireResult.calculated} mm²</strong></p>
                      <p>• Zalecany przekrój: <strong className="text-green-700">{wireResult.recommended} mm²</strong></p>
                      <p>• Maksymalny prąd: <strong>{wireResult.maxCurrent} A</strong></p>
                      <p>• Materiał: {wireResult.type}</p>
                    </div>
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Voltage Drop Calculator */}
        <TabsContent value="drop">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingDown className="h-5 w-5 text-red-600" />
                <span>Spadek napięcia</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="drop-current">Prąd (A)</Label>
                  <Input
                    id="drop-current"
                    type="number"
                    value={dropCurrent}
                    onChange={(e) => setDropCurrent(e.target.value)}
                    placeholder="np. 16"
                  />
                </div>
                <div>
                  <Label htmlFor="drop-length">Długość (m)</Label>
                  <Input
                    id="drop-length"
                    type="number"
                    value={dropLength}
                    onChange={(e) => setDropLength(e.target.value)}
                    placeholder="np. 25"
                  />
                </div>
                <div>
                  <Label htmlFor="drop-cross">Przekrój (mm²)</Label>
                  <Input
                    id="drop-cross"
                    type="number"
                    value={dropCrossSection}
                    onChange={(e) => setDropCrossSection(e.target.value)}
                    placeholder="np. 2.5"
                  />
                </div>
                <div>
                  <Label htmlFor="drop-voltage">Napięcie (V)</Label>
                  <Select value={dropVoltage} onValueChange={setDropVoltage}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="230">230V</SelectItem>
                      <SelectItem value="400">400V</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <Button onClick={calculateVoltageDrop} className="bg-yellow-500 hover:bg-yellow-600 w-full">
                Oblicz spadek
              </Button>
              {dropResult && (
                <Alert className={dropResult.acceptable ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}>
                  <AlertDescription>
                    <div className="space-y-2">
                      <p className="font-bold text-lg">Wyniki:</p>
                      <p>• Spadek napięcia: <strong>{dropResult.voltageDrop} V</strong></p>
                      <p>• Procent spadku: <strong>{dropResult.percentage}%</strong></p>
                      <p className={dropResult.acceptable ? 'text-green-700 font-bold' : 'text-red-700 font-bold'}>
                        {dropResult.acceptable ? '✔ Akceptowalny (do 3%)' : '⚠ Za duży! (powyej 3%)'}
                      </p>
                    </div>
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Breaker Calculator */}
        <TabsContent value="breaker">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-blue-600" />
                <span>Dobór zabezpieczeń</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="breaker-power">Moc (W)</Label>
                  <Input
                    id="breaker-power"
                    type="number"
                    value={breakerPower}
                    onChange={(e) => setBreakerPower(e.target.value)}
                    placeholder="np. 3500"
                  />
                </div>
                <div>
                  <Label htmlFor="breaker-voltage">Napięcie (V)</Label>
                  <Select value={breakerVoltage} onValueChange={setBreakerVoltage}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="230">230V</SelectItem>
                      <SelectItem value="400">400V</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="md:col-span-2">
                  <Label htmlFor="breaker-phases">Liczba faz</Label>
                  <Select value={breakerPhases} onValueChange={setBreakerPhases}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Jednofazowy</SelectItem>
                      <SelectItem value="3">Trójfazowy</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <Button onClick={calculateBreaker} className="bg-yellow-500 hover:bg-yellow-600 w-full">
                Dobierz bezpiecznik
              </Button>
              {breakerResult && (
                <Alert className="bg-blue-50 border-blue-200">
                  <AlertDescription>
                    <div className="space-y-2">
                      <p className="font-bold text-lg">Wyniki:</p>
                      <p>• Obliczony prąd: <strong>{breakerResult.current} A</strong></p>
                      <p>• Zalecany bezpiecznik: <strong className="text-blue-700">{breakerResult.recommended} A</strong></p>
                      <p>• Typ: {breakerResult.type}</p>
                      <p className="text-sm text-gray-600 mt-2">
                        💡 Wskazówka: Bezpiecznik powinien być o 25% większy od prądu nominalnego
                      </p>
                    </div>
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Ohm's Law Calculator */}
        <TabsContent value="ohm">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="h-5 w-5 text-purple-600" />
                <span>Prawo Ohma (U = I × R)</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="ohm-voltage">Napięcie (V)</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="ohm-voltage"
                      type="number"
                      value={ohmVoltage}
                      onChange={(e) => setOhmVoltage(e.target.value)}
                      placeholder="np. 230"
                    />
                    <Button onClick={() => calculateOhmsLaw('voltage')} size="sm" variant="outline">
                      Oblicz
                    </Button>
                  </div>
                </div>
                <div>
                  <Label htmlFor="ohm-current">Prąd (A)</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="ohm-current"
                      type="number"
                      value={ohmCurrent}
                      onChange={(e) => setOhmCurrent(e.target.value)}
                      placeholder="np. 10"
                    />
                    <Button onClick={() => calculateOhmsLaw('current')} size="sm" variant="outline">
                      Oblicz
                    </Button>
                  </div>
                </div>
                <div>
                  <Label htmlFor="ohm-resistance">Rezystancja (Ω)</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="ohm-resistance"
                      type="number"
                      value={ohmResistance}
                      onChange={(e) => setOhmResistance(e.target.value)}
                      placeholder="np. 23"
                    />
                    <Button onClick={() => calculateOhmsLaw('resistance')} size="sm" variant="outline">
                      Oblicz
                    </Button>
                  </div>
                </div>
                <div>
                  <Label htmlFor="ohm-power">Moc (W)</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="ohm-power"
                      type="number"
                      value={ohmPower}
                      onChange={(e) => setOhmPower(e.target.value)}
                      placeholder="np. 2300"
                    />
                    <Button onClick={() => calculateOhmsLaw('power')} size="sm" variant="outline">
                      Oblicz
                    </Button>
                  </div>
                </div>
              </div>
              <Alert className="bg-purple-50 border-purple-200">
                <AlertDescription>
                  <p className="font-semibold mb-2">Podstawowe wzory:</p>
                  <div className="space-y-1 text-sm">
                    <p>• U = I × R (napięcie)</p>
                    <p>• I = U / R (prąd)</p>
                    <p>• R = U / I (rezystancja)</p>
                    <p>• P = U × I (moc)</p>
                  </div>
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Power Calculator */}
        <TabsContent value="power">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Power className="h-5 w-5 text-orange-600" />
                <span>Kalkulator mocy</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="power-voltage">Napięcie (V)</Label>
                  <Input
                    id="power-voltage"
                    type="number"
                    value={powerVoltage}
                    onChange={(e) => setPowerVoltage(e.target.value)}
                    placeholder="np. 230"
                  />
                </div>
                <div>
                  <Label htmlFor="power-current">Prąd (A)</Label>
                  <Input
                    id="power-current"
                    type="number"
                    value={powerCurrent}
                    onChange={(e) => setPowerCurrent(e.target.value)}
                    placeholder="np. 10"
                  />
                </div>
                <div className="md:col-span-2">
                  <Label htmlFor="power-pf">Współczynnik mocy (cosφ)</Label>
                  <Input
                    id="power-pf"
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={powerPF}
                    onChange={(e) => setPowerPF(e.target.value)}
                    placeholder="np. 0.85"
                  />
                </div>
              </div>
              <Button onClick={calculatePower} className="bg-yellow-500 hover:bg-yellow-600 w-full">
                Oblicz moc
              </Button>
              {powerResult && (
                <Alert className="bg-orange-50 border-orange-200">
                  <AlertDescription>
                    <div className="space-y-2">
                      <p className="font-bold text-lg">Wyniki:</p>
                      <p>• Moc pozorna (S): <strong>{powerResult.apparent} VA</strong></p>
                      <p>• Moc czynna (P): <strong className="text-orange-700">{powerResult.active} W</strong></p>
                      <p>• Moc bierna (Q): <strong>{powerResult.reactive} VAr</strong></p>
                      <p>• Współczynnik mocy: {powerResult.powerFactor}</p>
                    </div>
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tips */}
        <TabsContent value="tips">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Lightbulb className="h-5 w-5 text-yellow-600" />
                <span>Wskazówki i normy</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="border-l-4 border-yellow-500 pl-4 py-2">
                  <h3 className="font-bold mb-2">Standardowe przekroje przewodów:</h3>
                  <p className="text-sm">1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240 mm²</p>
                </div>
                
                <div className="border-l-4 border-blue-500 pl-4 py-2">
                  <h3 className="font-bold mb-2">Standardowe wartości bezpieczników:</h3>
                  <p className="text-sm">6, 10, 13, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125 A</p>
                </div>

                <div className="border-l-4 border-green-500 pl-4 py-2">
                  <h3 className="font-bold mb-2">Dopuszczalny spadek napięcia:</h3>
                  <p className="text-sm">• Instalacje oświetleniowe: max 3%</p>
                  <p className="text-sm">• Inne obwody: max 5%</p>
                </div>

                <div className="border-l-4 border-red-500 pl-4 py-2">
                  <h3 className="font-bold mb-2">Typowe obciążenia:</h3>
                  <p className="text-sm">• Gniazdko 230V: 16A (3,7 kW)</p>
                  <p className="text-sm">• Kuchenka elektryczna: 32A (7,4 kW)</p>
                  <p className="text-sm">• Bojler: 16A (3,7 kW)</p>
                  <p className="text-sm">• Oświetlenie LED: 10A (2,3 kW)</p>
                </div>

                <div className="border-l-4 border-purple-500 pl-4 py-2">
                  <h3 className="font-bold mb-2">Kolory przewodów:</h3>
                  <p className="text-sm">• L (Faza): Brązowy, Czarny, Szary</p>
                  <p className="text-sm">• N (Neutralny): Niebieski</p>
                  <p className="text-sm">• PE (Ochronny): Żółto-zielony</p>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-sm">
                    <strong>⚠ Ważne:</strong> Wszystkie obliczenia są orientacyjne. 
                    Zawsze sprówdź wyniki zgodnie z aktualnymi normami i przepisami. 
                    W przypadku wątpliwości skonsultuj się z doświadczonym elektrykiem.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ElectricalCalculators;
