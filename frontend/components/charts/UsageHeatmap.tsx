import { useMemo } from 'react';

interface CorrelationData {
  variable1: string;
  variable2: string;
  correlation: number;
}

interface CorrelationHeatmapProps {
  data?: CorrelationData[];
}

// EV Charging related variables for correlation analysis
const VARIABLES = [
  'Energy Consumed',
  'Charging Duration',
  'Battery Capacity',
  'Temperature',
  'Distance Driven',
  'Vehicle Age',
  'Charging Cost',
  'State of Charge',
  'Charging Rate',
  'Session Count',
  'Peak Hours',
  'Weekend Usage'
];

// Generate sample correlation data
const generateCorrelationData = (): CorrelationData[] => {
  const data: CorrelationData[] = [];

  // Generate correlation matrix
  VARIABLES.forEach((var1, i) => {
    VARIABLES.forEach((var2, j) => {
      let correlation: number;

      if (i === j) {
        // Perfect correlation with itself
        correlation = 1.0;
      } else {
        // Generate realistic correlations based on EV charging relationships
        if ((var1 === 'Energy Consumed' && var2 === 'Charging Duration') ||
            (var1 === 'Charging Duration' && var2 === 'Energy Consumed')) {
          correlation = 0.85; // Strong positive correlation
        } else if ((var1 === 'Battery Capacity' && var2 === 'Energy Consumed') ||
                   (var1 === 'Energy Consumed' && var2 === 'Battery Capacity')) {
          correlation = 0.72; // Strong positive correlation
        } else if ((var1 === 'Temperature' && var2 === 'Charging Duration') ||
                   (var1 === 'Charging Duration' && var2 === 'Temperature')) {
          correlation = -0.45; // Negative correlation (cold weather = longer charging)
        } else if ((var1 === 'Vehicle Age' && var2 === 'Charging Duration') ||
                   (var1 === 'Charging Duration' && var2 === 'Vehicle Age')) {
          correlation = 0.35; // Weak positive correlation
        } else if ((var1 === 'Charging Cost' && var2 === 'Energy Consumed') ||
                   (var1 === 'Energy Consumed' && var2 === 'Charging Cost')) {
          correlation = 0.78; // Strong positive correlation
        } else if ((var1 === 'Peak Hours' && var2 === 'Charging Cost') ||
                   (var1 === 'Charging Cost' && var2 === 'Peak Hours')) {
          correlation = 0.42; // Moderate positive correlation
        } else if ((var1 === 'Weekend Usage' && var2 === 'Peak Hours') ||
                   (var1 === 'Peak Hours' && var2 === 'Weekend Usage')) {
          correlation = -0.38; // Negative correlation
        } else {
          // Random correlations for other pairs
          correlation = (Math.random() - 0.5) * 1.6; // Range from -0.8 to 0.8
          correlation = Math.max(-0.95, Math.min(0.95, correlation)); // Clamp values
        }
      }

      data.push({
        variable1: var1,
        variable2: var2,
        correlation: Math.round(correlation * 100) / 100 // Round to 2 decimal places
      });
    });
  });

  return data;
};

export default function CorrelationHeatmap({ data }: CorrelationHeatmapProps) {
  const correlationData = useMemo(() => data || generateCorrelationData(), [data]);

  const getCorrelationColor = (correlation: number) => {
    const absCorr = Math.abs(correlation);

    if (correlation > 0) {
      // Positive correlations - green scale
      if (absCorr >= 0.8) return 'bg-green-800';
      if (absCorr >= 0.6) return 'bg-green-600';
      if (absCorr >= 0.4) return 'bg-green-400';
      if (absCorr >= 0.2) return 'bg-green-200';
      return 'bg-green-100';
    } else {
      // Negative correlations - red/orange scale
      if (absCorr >= 0.8) return 'bg-red-800';
      if (absCorr >= 0.6) return 'bg-red-600';
      if (absCorr >= 0.4) return 'bg-orange-500';
      if (absCorr >= 0.2) return 'bg-orange-300';
      return 'bg-orange-100';
    }
  };

  const getTextColor = (correlation: number) => {
    const absCorr = Math.abs(correlation);
    return absCorr >= 0.5 ? 'text-white' : 'text-gray-800';
  };

  const getCorrelation = (var1: string, var2: string) => {
    const item = correlationData.find(d => d.variable1 === var1 && d.variable2 === var2);
    return item ? item.correlation : 0;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
        EV Charging Variables Correlation Heatmap
      </h3>

      <div className="overflow-x-auto">
        <div className="min-w-[900px]">
          {/* Variable labels (top) */}
          <div className="flex mb-4">
            <div className="w-32"></div>
            {VARIABLES.map((variable, index) => (
              <div
                key={variable}
                className="w-20 text-xs text-center text-gray-600"
                style={{ height: '80px', display: 'flex', alignItems: 'end', justifyContent: 'center' }}
              >
                <span
                  className="whitespace-nowrap transform -rotate-45 origin-bottom-left"
                  style={{ transformOrigin: 'bottom left' }}
                >
                  {variable}
                </span>
              </div>
            ))}
          </div>

          {/* Correlation matrix */}
          {VARIABLES.map((rowVariable, rowIndex) => (
            <div key={rowVariable} className="flex items-center mb-1">
              <div className="w-32 text-xs text-gray-700 pr-2 text-right font-medium">
                {rowVariable}
              </div>
              {VARIABLES.map((colVariable, colIndex) => {
                const correlation = getCorrelation(rowVariable, colVariable);

                return (
                  <div
                    key={`${rowVariable}-${colVariable}`}
                    className={`w-20 h-8 flex items-center justify-center text-xs font-medium border border-gray-200 cursor-pointer ${getCorrelationColor(correlation)} ${getTextColor(correlation)}`}
                    title={`${rowVariable} vs ${colVariable}: ${correlation.toFixed(2)}`}
                  >
                    {correlation.toFixed(2)}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-6 flex items-center justify-center">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">Correlation Scale:</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="text-xs text-gray-500">-1.0</span>
            <div className="flex space-x-0.5">
              <div className="w-4 h-4 bg-red-800 rounded-sm"></div>
              <div className="w-4 h-4 bg-red-600 rounded-sm"></div>
              <div className="w-4 h-4 bg-orange-500 rounded-sm"></div>
              <div className="w-4 h-4 bg-orange-300 rounded-sm"></div>
              <div className="w-4 h-4 bg-orange-100 rounded-sm"></div>
              <div className="w-4 h-4 bg-green-100 rounded-sm"></div>
              <div className="w-4 h-4 bg-green-200 rounded-sm"></div>
              <div className="w-4 h-4 bg-green-400 rounded-sm"></div>
              <div className="w-4 h-4 bg-green-600 rounded-sm"></div>
              <div className="w-4 h-4 bg-green-800 rounded-sm"></div>
            </div>
            <span className="text-xs text-gray-500">+1.0</span>
          </div>
          <div className="text-xs text-gray-500">
            <span className="text-red-600">Negative</span> | <span className="text-green-600">Positive</span>
          </div>
        </div>
      </div>
    </div>
  );
}
