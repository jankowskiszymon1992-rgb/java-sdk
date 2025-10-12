import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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

      <Tabs defaultValue="basic" className="w-full">
        <TabsList className="grid w-full grid-cols-2 max-w-md">
          <TabsTrigger value="basic" className="flex items-center space-x-2">
            <Calculator className="h-4 w-4" />
            <span>Podstawowy</span>
          </TabsTrigger>
          <TabsTrigger value="electrical" className="flex items-center space-x-2">
            <Zap className="h-4 w-4" />
            <span>Elektryczny</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="basic" className="mt-6">
          <BasicCalculator />
        </TabsContent>

        <TabsContent value="electrical" className="mt-6">
          <ElectricalCalculators />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Calculators;
