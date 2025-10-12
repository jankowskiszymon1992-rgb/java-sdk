import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Delete } from 'lucide-react';

const BasicCalculator = () => {
  const [display, setDisplay] = useState('0');
  const [previousValue, setPreviousValue] = useState(null);
  const [operation, setOperation] = useState(null);
  const [newNumber, setNewNumber] = useState(true);

  const handleNumber = (num) => {
    if (newNumber) {
      setDisplay(num.toString());
      setNewNumber(false);
    } else {
      setDisplay(display === '0' ? num.toString() : display + num);
    }
  };

  const handleDecimal = () => {
    if (newNumber) {
      setDisplay('0.');
      setNewNumber(false);
    } else if (!display.includes('.')) {
      setDisplay(display + '.');
    }
  };

  const handleOperation = (op) => {
    const current = parseFloat(display);
    
    if (previousValue === null) {
      setPreviousValue(current);
    } else if (operation) {
      const result = calculate(previousValue, current, operation);
      setDisplay(result.toString());
      setPreviousValue(result);
    }
    
    setOperation(op);
    setNewNumber(true);
  };

  const calculate = (a, b, op) => {
    switch (op) {
      case '+':
        return a + b;
      case '-':
        return a - b;
      case '×':
        return a * b;
      case '÷':
        return b !== 0 ? a / b : 0;
      default:
        return b;
    }
  };

  const handleEquals = () => {
    if (operation && previousValue !== null) {
      const current = parseFloat(display);
      const result = calculate(previousValue, current, operation);
      setDisplay(result.toString());
      setPreviousValue(null);
      setOperation(null);
      setNewNumber(true);
    }
  };

  const handleClear = () => {
    setDisplay('0');
    setPreviousValue(null);
    setOperation(null);
    setNewNumber(true);
  };

  const handleBackspace = () => {
    if (display.length > 1) {
      setDisplay(display.slice(0, -1));
    } else {
      setDisplay('0');
      setNewNumber(true);
    }
  };

  const buttonClass = "h-16 text-xl font-bold transition-all hover:scale-105 flex items-center justify-center";
  const numberButtonClass = `${buttonClass} bg-white hover:bg-gray-100 border-2 border-gray-300 text-gray-900`;
  const operationButtonClass = `${buttonClass} bg-yellow-500 hover:bg-yellow-600 text-white border-0`;
  const equalsButtonClass = `${buttonClass} bg-green-600 hover:bg-green-700 text-white border-0`;
  const clearButtonClass = `${buttonClass} bg-red-500 hover:bg-red-600 text-white border-0`;

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Kalkulator Podstawowy</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Display */}
          <div className="bg-gray-900 text-white rounded-lg p-6 text-right">
            <div className="text-sm text-gray-400 h-6">
              {previousValue !== null && operation ? `${previousValue} ${operation}` : ''}
            </div>
            <div className="text-4xl font-bold break-all" data-testid="calculator-display">
              {display}
            </div>
          </div>

          {/* Buttons */}
          <div className="grid grid-cols-4 gap-2">
            {/* Row 1 */}
            <Button onClick={handleClear} className={clearButtonClass}>
              C
            </Button>
            <Button onClick={handleBackspace} className={numberButtonClass}>
              <Delete className="h-5 w-5" />
            </Button>
            <Button onClick={() => handleOperation('÷')} className={operationButtonClass}>
              ÷
            </Button>
            <Button onClick={() => handleOperation('×')} className={operationButtonClass}>
              ×
            </Button>

            {/* Row 2 */}
            <Button onClick={() => handleNumber(7)} className={numberButtonClass}>
              7
            </Button>
            <Button onClick={() => handleNumber(8)} className={numberButtonClass}>
              8
            </Button>
            <Button onClick={() => handleNumber(9)} className={numberButtonClass}>
              9
            </Button>
            <Button onClick={() => handleOperation('-')} className={operationButtonClass}>
              -
            </Button>

            {/* Row 3 */}
            <Button onClick={() => handleNumber(4)} className={numberButtonClass}>
              4
            </Button>
            <Button onClick={() => handleNumber(5)} className={numberButtonClass}>
              5
            </Button>
            <Button onClick={() => handleNumber(6)} className={numberButtonClass}>
              6
            </Button>
            <Button onClick={() => handleOperation('+')} className={operationButtonClass}>
              +
            </Button>

            {/* Row 4 */}
            <Button onClick={() => handleNumber(1)} className={numberButtonClass}>
              1
            </Button>
            <Button onClick={() => handleNumber(2)} className={numberButtonClass}>
              2
            </Button>
            <Button onClick={() => handleNumber(3)} className={numberButtonClass}>
              3
            </Button>
            <Button onClick={handleEquals} className={`${equalsButtonClass} row-span-2`}>
              =
            </Button>

            {/* Row 5 */}
            <Button onClick={() => handleNumber(0)} className={`${numberButtonClass} col-span-2`}>
              0
            </Button>
            <Button onClick={handleDecimal} className={numberButtonClass}>
              .
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default BasicCalculator;
