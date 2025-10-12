import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calculator, Zap } from 'lucide-react';
import BasicCalculator from '../components/BasicCalculator';
import ElectricalCalculators from '../components/ElectricalCalculators';

const Calculators = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Kalkulatory</h2>
        <p className="text-gray-600 mt-1">Narzędzia do obliczeń i planowania</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Basic Calculator Card */}
        <Card className="hover:shadow-xl transition-shadow">
          <CardHeader className="bg-gradient-to-r from-blue-50 to-blue-100 border-b">
            <CardTitle className="flex items-center space-x-2 text-blue-900">
              <Calculator className="h-6 w-6" />
              <span>Kalkulator Podstawowy</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <BasicCalculator />
          </CardContent>
        </Card>

        {/* Electrical Calculators Card */}
        <Card className="hover:shadow-xl transition-shadow">
          <CardHeader className="bg-gradient-to-r from-yellow-50 to-yellow-100 border-b">
            <CardTitle className="flex items-center space-x-2 text-yellow-900">
              <Zap className="h-6 w-6" />
              <span>Kalkulatory Elektryczne</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <ElectricalCalculators />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Calculators;
