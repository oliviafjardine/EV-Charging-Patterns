import { useMemo } from 'react';
import { motion } from 'framer-motion';

interface LocationUsageMapProps {
  data: Array<{
    location: string;
    session_count: number;
    total_energy_kwh: number;
    avg_cost_usd: number;
    utilization_rate: number;
  }>;
}

export default function LocationUsageMap({ data }: LocationUsageMapProps) {
  const maxSessions = useMemo(() => 
    Math.max(...data.map(item => item.session_count)), 
    [data]
  );

  const maxEnergy = useMemo(() => 
    Math.max(...data.map(item => item.total_energy_kwh)), 
    [data]
  );

  const getUtilizationColor = (rate: number) => {
    if (rate >= 0.8) return 'bg-green-500';
    if (rate >= 0.6) return 'bg-yellow-500';
    if (rate >= 0.4) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getUtilizationText = (rate: number) => {
    if (rate >= 0.8) return 'High';
    if (rate >= 0.6) return 'Medium';
    if (rate >= 0.4) return 'Low';
    return 'Very Low';
  };

  return (
    <div className="space-y-4">
      {/* Legend */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <div className="flex items-center space-x-4">
          <span>Utilization:</span>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span>High (80%+)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span>Medium (60-80%)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
            <span>Low (40-60%)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span>Very Low (&lt;40%)</span>
          </div>
        </div>
      </div>

      {/* Location Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.map((location, index) => (
          <motion.div
            key={location.location}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-medium transition-shadow"
          >
            {/* Location Header */}
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium text-gray-900 truncate">
                {location.location}
              </h4>
              <div className="flex items-center space-x-2">
                <div 
                  className={`w-3 h-3 rounded-full ${getUtilizationColor(location.utilization_rate)}`}
                  title={`${(location.utilization_rate * 100).toFixed(1)}% utilization`}
                />
                <span className="text-xs text-gray-500">
                  {getUtilizationText(location.utilization_rate)}
                </span>
              </div>
            </div>

            {/* Metrics */}
            <div className="space-y-3">
              {/* Sessions */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Sessions</span>
                  <span className="font-medium">{location.session_count}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <motion.div
                    className="bg-blue-500 h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ 
                      width: `${(location.session_count / maxSessions) * 100}%` 
                    }}
                    transition={{ delay: index * 0.1 + 0.3, duration: 0.8 }}
                  />
                </div>
              </div>

              {/* Energy */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Energy (kWh)</span>
                  <span className="font-medium">
                    {location.total_energy_kwh.toFixed(1)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <motion.div
                    className="bg-green-500 h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ 
                      width: `${(location.total_energy_kwh / maxEnergy) * 100}%` 
                    }}
                    transition={{ delay: index * 0.1 + 0.4, duration: 0.8 }}
                  />
                </div>
              </div>

              {/* Average Cost */}
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Avg Cost</span>
                <span className="font-medium text-green-600">
                  ${location.avg_cost_usd.toFixed(2)}
                </span>
              </div>

              {/* Utilization Rate */}
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Utilization</span>
                <span className="font-medium">
                  {(location.utilization_rate * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="mt-4 pt-3 border-t border-gray-100">
              <div className="grid grid-cols-2 gap-2 text-xs text-gray-500">
                <div>
                  <span className="block">Cost/kWh</span>
                  <span className="font-medium text-gray-700">
                    ${(location.avg_cost_usd / (location.total_energy_kwh / location.session_count)).toFixed(3)}
                  </span>
                </div>
                <div>
                  <span className="block">Avg/Session</span>
                  <span className="font-medium text-gray-700">
                    {(location.total_energy_kwh / location.session_count).toFixed(1)} kWh
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">Summary</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="block text-gray-600">Total Locations</span>
            <span className="text-lg font-semibold text-gray-900">
              {data.length}
            </span>
          </div>
          <div>
            <span className="block text-gray-600">Total Sessions</span>
            <span className="text-lg font-semibold text-gray-900">
              {data.reduce((sum, item) => sum + item.session_count, 0).toLocaleString()}
            </span>
          </div>
          <div>
            <span className="block text-gray-600">Total Energy</span>
            <span className="text-lg font-semibold text-gray-900">
              {(data.reduce((sum, item) => sum + item.total_energy_kwh, 0) / 1000).toFixed(1)} MWh
            </span>
          </div>
          <div>
            <span className="block text-gray-600">Avg Utilization</span>
            <span className="text-lg font-semibold text-gray-900">
              {(data.reduce((sum, item) => sum + item.utilization_rate, 0) / data.length * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
