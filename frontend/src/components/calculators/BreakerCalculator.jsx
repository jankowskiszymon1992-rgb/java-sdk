import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';

const BreakerCalculator = () => {
  const [breakerPower, setBreakerPower] = useState('');
  const [breakerVoltage, setBreakerVoltage] = useState('230');
  const [breakerPhases, setBreakerPhases] = useState('1');
  const [breakerResult, setBreakerResult] = useState(null);

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

    const standardBreakers = [6, 10, 13, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125];
    const recommended = standardBreakers.find(b => b >= current * 1.25) || standardBreakers[standardBreakers.length - 1];

    setBreakerResult({
      current: current.toFixed(2),
      recommended: recommended,
      type: phases === 1 ? 'jednofazowy' : 'trójfazowy'
    });
  };

  return (
    <div className="space-y-4">
      <div className="space-y-3">
        <div>
          <Label htmlFor="breaker-power" className="text-sm">Moc (W)</Label>
          <Input
            id="breaker-power"
            type="number"
            value={breakerPower}
            onChange={(e) => setBreakerPower(e.target.value)}
            placeholder="3500"
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="breaker-voltage" className="text-sm">Napięcie</Label>
          <Select value={breakerVoltage} onValueChange={setBreakerVoltage}>
            <SelectTrigger className="mt-1">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="230">230V</SelectItem>
              <SelectItem value="400">400V</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label htmlFor="breaker-phases" className="text-sm">Fazy</Label>
          <Select value={breakerPhases} onValueChange={setBreakerPhases}>
            <SelectTrigger className="mt-1">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">Jednofazowy</SelectItem>
              <SelectItem value="3">Trójfazowy</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <Button onClick={calculateBreaker} className="w-full bg-yellow-500 hover:bg-yellow-600">
        Oblicz
      </Button>
      {breakerResult && (
        <Alert className="bg-blue-50 border-blue-200">
          <AlertDescription>
            <div className="space-y-1 text-sm">
              <p><strong>Prąd:</strong> {breakerResult.current} A</p>
              <p><strong>Zalecany:</strong> {breakerResult.recommended} A</p>
              <p><strong>Typ:</strong> {breakerResult.type}</p>
            </div>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default BreakerCalculator;