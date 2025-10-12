import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';

const WireCalculator = () => {
  const [wireCurrent, setWireCurrent] = useState('');
  const [wireLength, setWireLength] = useState('');
  const [wireVoltage, setWireVoltage] = useState('230');
  const [wireType, setWireType] = useState('copper');
  const [wireResult, setWireResult] = useState(null);

  const calculateWireSize = () => {
    const current = parseFloat(wireCurrent);
    const length = parseFloat(wireLength);
    const voltage = parseFloat(wireVoltage);

    if (!current || !length) return;

    const k = wireType === 'copper' ? 56 : 35;
    const maxDrop = voltage * 0.03;
    const crossSection = (2 * current * length) / (k * maxDrop);

    const standardSizes = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240];
    const recommendedSize = standardSizes.find(size => size >= crossSection) || standardSizes[standardSizes.length - 1];

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

  return (
    <div className="space-y-4">
      <div className="space-y-3">
        <div>
          <Label htmlFor="wire-current" className="text-sm">Prąd (A)</Label>
          <Input
            id="wire-current"
            type="number"
            value={wireCurrent}
            onChange={(e) => setWireCurrent(e.target.value)}
            placeholder="16"
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="wire-length" className="text-sm">Długość (m)</Label>
          <Input
            id="wire-length"
            type="number"
            value={wireLength}
            onChange={(e) => setWireLength(e.target.value)}
            placeholder="25"
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="wire-voltage" className="text-sm">Napięcie</Label>
          <Select value={wireVoltage} onValueChange={setWireVoltage}>
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
          <Label htmlFor="wire-type" className="text-sm">Materiał</Label>
          <Select value={wireType} onValueChange={setWireType}>
            <SelectTrigger className="mt-1">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="copper">Miedź</SelectItem>
              <SelectItem value="aluminum">Aluminium</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <Button onClick={calculateWireSize} className="w-full bg-yellow-500 hover:bg-yellow-600">
        Oblicz
      </Button>
      {wireResult && (
        <Alert className="bg-green-50 border-green-200">
          <AlertDescription>
            <div className="space-y-1 text-sm">
              <p><strong>Obliczony:</strong> {wireResult.calculated} mm²</p>
              <p><strong>Zalecany:</strong> {wireResult.recommended} mm²</p>
              <p><strong>Max prąd:</strong> {wireResult.maxCurrent} A</p>
            </div>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default WireCalculator;