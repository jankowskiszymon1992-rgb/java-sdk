import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calculator, Cable, TrendingDown, Shield, Zap, Power, Lightbulb } from 'lucide-react';
import BasicCalculator from '../components/BasicCalculator';
import WireCalculator from '../components/calculators/WireCalculator';
import VoltageDropCalculator from '../components/calculators/VoltageDropCalculator';
import BreakerCalculator from '../components/calculators/BreakerCalculator';
import OhmLawCalculator from '../components/calculators/OhmLawCalculator';
import PowerCalculator from '../components/calculators/PowerCalculator';
import ElectricalTips from '../components/calculators/ElectricalTips';

const Calculators = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Kalkulatory</h2>
        <p className="text-gray-600 mt-1">Narzędzia do obliczeń i planowania</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {/* Basic Calculator */}
        <Card className="hover:shadow-xl transition-shadow">
          <CardHeader className="bg-gradient-to-r from-blue-50 to-blue-100 border-b">
            <CardTitle className="flex items-center space-x-2 text-blue-900">
              <Calculator className="h-5 w-5" />
              <span className="text-base">Kalkulator Podstawowy</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <BasicCalculator />
          </CardContent>
        </Card>

        {/* Wire Calculator */}
        <Card className="hover:shadow-xl transition-shadow">
          <CardHeader className="bg-gradient-to-r from-yellow-50 to-yellow-100 border-b">
            <CardTitle className="flex items-center space-x-2 text-yellow-900">
              <Cable className="h-5 w-5" />
              <span className="text-base">Dobór Przewodów</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <WireCalculator />
          </CardContent>
        </Card>

        {/* Voltage Drop Calculator */}
        <Card className="hover:shadow-xl transition-shadow">
          <CardHeader className="bg-gradient-to-r from-red-50 to-red-100 border-b">
            <CardTitle className="flex items-center space-x-2 text-red-900">
              <TrendingDown className="h-5 w-5" />
              <span className="text-base">Spadek Napięcia</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <VoltageDropCalculator />
          </CardContent>
        </Card>

        {/* Breaker Calculator */}
        <Card className="hover:shadow-xl transition-shadow">
          <CardHeader className="bg-gradient-to-r from-green-50 to-green-100 border-b">
            <CardTitle className="flex items-center space-x-2 text-green-900">
              <Shield className="h-5 w-5" />
              <span className="text-base">Dobór Bezpieczników</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <BreakerCalculator />
          </CardContent>
        </Card>

        {/* Ohm Law Calculator */}
        <Card className="hover:shadow-xl transition-shadow">
          <CardHeader className="bg-gradient-to-r from-purple-50 to-purple-100 border-b">
            <CardTitle className="flex items-center space-x-2 text-purple-900">
              <Zap className="h-5 w-5" />
              <span className="text-base">Prawo Ohma</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <OhmLawCalculator />
          </CardContent>
        </Card>

        {/* Power Calculator */}
        <Card className="hover:shadow-xl transition-shadow">
          <CardHeader className="bg-gradient-to-r from-orange-50 to-orange-100 border-b">
            <CardTitle className="flex items-center space-x-2 text-orange-900">
              <Power className="h-5 w-5" />
              <span className="text-base">Kalkulator Mocy</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <PowerCalculator />
          </CardContent>
        </Card>

        {/* Electrical Tips */}
        <Card className="hover:shadow-xl transition-shadow">
          <CardHeader className="bg-gradient-to-r from-indigo-50 to-indigo-100 border-b">
            <CardTitle className="flex items-center space-x-2 text-indigo-900">
              <Lightbulb className="h-5 w-5" />
              <span className="text-base">Wskazówki i Normy</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <ElectricalTips />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Calculators;
