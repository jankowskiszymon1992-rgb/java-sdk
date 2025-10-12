import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';

const VoltageDropCalculator = () => {
  const [dropCurrent, setDropCurrent] = useState('');
  const [dropLength, setDropLength] = useState('');
  const [dropCrossSection, setDropCrossSection] = useState('');
  const [dropVoltage, setDropVoltage] = useState('230');
  const [dropResult, setDropResult] = useState(null);

  const calculateVoltageDrop = () => {
    const current = parseFloat(dropCurrent);
    const length = parseFloat(dropLength);
    const crossSection = parseFloat(dropCrossSection);
    const voltage = parseFloat(dropVoltage);

    if (!current || !length || !crossSection) return;

    const k = 56;
    const drop = (2 * current * length) / (k * crossSection);
    const dropPercent = (drop / voltage) * 100;

    setDropResult({
      voltageDrop: drop.toFixed(2),
      percentage: dropPercent.toFixed(2),
      acceptable: dropPercent <= 3
    });
  };

  return (
    <div className="space-y-4">
      <div className="space-y-3">
        <div>
          <Label htmlFor="drop-current" className="text-sm">Prąd (A)</Label>
          <Input
            id="drop-current"
            type="number"
            value={dropCurrent}
            onChange={(e) => setDropCurrent(e.target.value)}
            placeholder="16"
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="drop-length" className="text-sm">Długość (m)</Label>
          <Input
            id="drop-length"
            type="number"
            value={dropLength}
            onChange={(e) => setDropLength(e.target.value)}
            placeholder="25"
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="drop-cross" className="text-sm">Przekrój (mm²)</Label>
          <Input
            id="drop-cross"
            type="number"
            value={dropCrossSection}
            onChange={(e) => setDropCrossSection(e.target.value)}
            placeholder="2.5"
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="drop-voltage" className="text-sm">Napięcie</Label>
          <Select value={dropVoltage} onValueChange={setDropVoltage}>
            <SelectTrigger className="mt-1">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="230">230V</SelectItem>
              <SelectItem value="400">400V</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <Button onClick={calculateVoltageDrop} className="w-full bg-yellow-500 hover:bg-yellow-600">
        Oblicz
      </Button>
      {dropResult && (
        <Alert className={dropResult.acceptable ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}>
          <AlertDescription>
            <div className="space-y-1 text-sm">
              <p><strong>Spadek:</strong> {dropResult.voltageDrop} V</p>
              <p><strong>Procent:</strong> {dropResult.percentage}%</p>
              <p className={dropResult.acceptable ? 'text-green-700 font-bold' : 'text-red-700 font-bold'}>
                {dropResult.acceptable ? '✓ Akceptowalny' : '✗ Za duży!'}
              </p>
            </div>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default VoltageDropCalculator;