import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';

const PowerCalculator = () => {
  const [powerVoltage, setPowerVoltage] = useState('');
  const [powerCurrent, setPowerCurrent] = useState('');
  const [powerPF, setPowerPF] = useState('1');
  const [powerResult, setPowerResult] = useState(null);

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
    <div className="space-y-4">
      <div className="space-y-3">
        <div>
          <Label htmlFor="power-voltage" className="text-sm">Napięcie (V)</Label>
          <Input
            id="power-voltage"
            type="number"
            value={powerVoltage}
            onChange={(e) => setPowerVoltage(e.target.value)}
            placeholder="230"
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="power-current" className="text-sm">Prąd (A)</Label>
          <Input
            id="power-current"
            type="number"
            value={powerCurrent}
            onChange={(e) => setPowerCurrent(e.target.value)}
            placeholder="10"
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="power-pf" className="text-sm">Wsp. mocy (cosφ)</Label>
          <Input
            id="power-pf"
            type="number"
            step="0.01"
            min="0"
            max="1"
            value={powerPF}
            onChange={(e) => setPowerPF(e.target.value)}
            className="mt-1"
          />
        </div>
      </div>
      <Button onClick={calculatePower} className="w-full bg-yellow-500 hover:bg-yellow-600">
        Oblicz
      </Button>
      {powerResult && (
        <Alert className="bg-orange-50 border-orange-200">
          <AlertDescription>
            <div className="space-y-1 text-sm">
              <p><strong>S:</strong> {powerResult.apparent} VA</p>
              <p><strong>P:</strong> {powerResult.active} W</p>
              <p><strong>Q:</strong> {powerResult.reactive} VAr</p>
              <p><strong>cosφ:</strong> {powerResult.powerFactor}</p>
            </div>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default PowerCalculator;