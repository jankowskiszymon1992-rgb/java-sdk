import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';

const OhmLawCalculator = () => {
  const [ohmVoltage, setOhmVoltage] = useState('');
  const [ohmCurrent, setOhmCurrent] = useState('');
  const [ohmResistance, setOhmResistance] = useState('');
  const [ohmPower, setOhmPower] = useState('');

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

  return (
    <div className="space-y-4">
      <div className="space-y-3">
        <div>
          <Label htmlFor="ohm-voltage" className="text-sm">Napięcie (V)</Label>
          <div className="flex gap-2 mt-1">
            <Input
              id="ohm-voltage"
              type="number"
              value={ohmVoltage}
              onChange={(e) => setOhmVoltage(e.target.value)}
              placeholder="230"
            />
            <Button onClick={() => calculateOhmsLaw('voltage')} size="sm" variant="outline">
              =
            </Button>
          </div>
        </div>
        <div>
          <Label htmlFor="ohm-current" className="text-sm">Prąd (A)</Label>
          <div className="flex gap-2 mt-1">
            <Input
              id="ohm-current"
              type="number"
              value={ohmCurrent}
              onChange={(e) => setOhmCurrent(e.target.value)}
              placeholder="10"
            />
            <Button onClick={() => calculateOhmsLaw('current')} size="sm" variant="outline">
              =
            </Button>
          </div>
        </div>
        <div>
          <Label htmlFor="ohm-resistance" className="text-sm">Rezystancja (Ω)</Label>
          <div className="flex gap-2 mt-1">
            <Input
              id="ohm-resistance"
              type="number"
              value={ohmResistance}
              onChange={(e) => setOhmResistance(e.target.value)}
              placeholder="23"
            />
            <Button onClick={() => calculateOhmsLaw('resistance')} size="sm" variant="outline">
              =
            </Button>
          </div>
        </div>
        <div>
          <Label htmlFor="ohm-power" className="text-sm">Moc (W)</Label>
          <div className="flex gap-2 mt-1">
            <Input
              id="ohm-power"
              type="number"
              value={ohmPower}
              onChange={(e) => setOhmPower(e.target.value)}
              placeholder="2300"
            />
            <Button onClick={() => calculateOhmsLaw('power')} size="sm" variant="outline">
              =
            </Button>
          </div>
        </div>
      </div>
      <Alert className="bg-purple-50 border-purple-200">
        <AlertDescription className="text-xs">
          <p className="font-semibold mb-1">Wzory:</p>
          <p>U = I × R | I = U / R</p>
          <p>R = U / I | P = U × I</p>
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default OhmLawCalculator;