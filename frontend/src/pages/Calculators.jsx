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
  const calculators = [
    {
      id: 'basic',
      title: 'Kalkulator Podstawowy',
      icon: Calculator,
      component: BasicCalculator,
      bgColor: 'from-blue-50 to-blue-100',
      textColor: 'text-blue-900',
    },
    {
      id: 'wire',
      title: 'Dobór Przewodów',
      icon: Cable,
      component: WireCalculator,
      bgColor: 'from-yellow-50 to-yellow-100',
      textColor: 'text-yellow-900',
    },
    {
      id: 'voltage-drop',
      title: 'Spadek Napięcia',
      icon: TrendingDown,
      component: VoltageDropCalculator,
      bgColor: 'from-red-50 to-red-100',
      textColor: 'text-red-900',
    },
    {
      id: 'breaker',
      title: 'Dobór Bezpieczników',
      icon: Shield,
      component: BreakerCalculator,
      bgColor: 'from-green-50 to-green-100',
      textColor: 'text-green-900',
    },
    {
      id: 'ohm',
      title: 'Prawo Ohma',
      icon: Zap,
      component: OhmLawCalculator,
      bgColor: 'from-purple-50 to-purple-100',
      textColor: 'text-purple-900',
    },
    {
      id: 'power',
      title: 'Kalkulator Mocy',
      icon: Power,
      component: PowerCalculator,
      bgColor: 'from-orange-50 to-orange-100',
      textColor: 'text-orange-900',
    },
    {
      id: 'tips',
      title: 'Wskazówki i Normy',
      icon: Lightbulb,
      component: ElectricalTips,
      bgColor: 'from-indigo-50 to-indigo-100',
      textColor: 'text-indigo-900',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Kalkulatory</h2>
        <p className="text-gray-600 mt-1">Narzędzia do obliczeń i planowania</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {calculators.map((calc) => {
          const Component = calc.component;
          return (
            <Card key={calc.id} className="hover:shadow-xl transition-shadow">
              <CardHeader className={`bg-gradient-to-r ${calc.bgColor} border-b`}>
                <CardTitle className={`flex items-center space-x-2 ${calc.textColor}`}>
                  <calc.icon className="h-5 w-5" />
                  <span className="text-base">{calc.title}</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                <Component />
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default Calculators;
