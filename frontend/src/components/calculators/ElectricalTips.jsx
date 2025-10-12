import { Alert, AlertDescription } from '@/components/ui/alert';

const ElectricalTips = () => {
  return (
    <div className="space-y-3">
      <Alert className="bg-yellow-50 border-yellow-200">
        <AlertDescription className="text-xs">
          <p className="font-bold mb-1">Przekroje:</p>
          <p>1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95 mm²</p>
        </AlertDescription>
      </Alert>
      
      <Alert className="bg-blue-50 border-blue-200">
        <AlertDescription className="text-xs">
          <p className="font-bold mb-1">Bezpieczniki:</p>
          <p>6, 10, 13, 16, 20, 25, 32, 40, 50, 63 A</p>
        </AlertDescription>
      </Alert>

      <Alert className="bg-green-50 border-green-200">
        <AlertDescription className="text-xs">
          <p className="font-bold mb-1">Spadek U:</p>
          <p>Oświetlenie: max 3%</p>
          <p>Inne: max 5%</p>
        </AlertDescription>
      </Alert>

      <Alert className="bg-red-50 border-red-200">
        <AlertDescription className="text-xs">
          <p className="font-bold mb-1">Obciążenia:</p>
          <p>Gniazdko: 16A</p>
          <p>Kuchenka: 32A</p>
          <p>Bojler: 16A</p>
        </AlertDescription>
      </Alert>

      <Alert className="bg-purple-50 border-purple-200">
        <AlertDescription className="text-xs">
          <p className="font-bold mb-1">Kolory:</p>
          <p>L: Brąz/Czarny</p>
          <p>N: Niebieski</p>
          <p>PE: Żółto-zielony</p>
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default ElectricalTips;