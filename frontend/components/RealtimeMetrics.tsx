import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BoltIcon, 
  ClockIcon, 
  CurrencyDollarIcon,
  SignalIcon 
} from '@heroicons/react/24/outline';
import { useWebSocket } from '../contexts/WebSocketContext';

interface RealtimeMetric {
  id: string;
  label: string;
  value: string;
  change: number;
  icon: React.ComponentType<any>;
  color: string;
}

export default function RealtimeMetrics() {
  const { isConnected, subscribe, unsubscribe } = useWebSocket();
  const [metrics, setMetrics] = useState<RealtimeMetric[]>([
    {
      id: 'active_sessions',
      label: 'Active Sessions',
      value: '127',
      change: 5.2,
      icon: BoltIcon,
      color: 'text-blue-600',
    },
    {
      id: 'avg_duration',
      label: 'Avg Duration',
      value: '2.3h',
      change: -1.8,
      icon: ClockIcon,
      color: 'text-purple-600',
    },
    {
      id: 'current_cost',
      label: 'Current Rate',
      value: '$0.28/kWh',
      change: 3.1,
      icon: CurrencyDollarIcon,
      color: 'text-green-600',
    },
    {
      id: 'network_status',
      label: 'Network Health',
      value: '98.5%',
      change: 0.2,
      icon: SignalIcon,
      color: 'text-emerald-600',
    },
  ]);

  useEffect(() => {
    if (isConnected) {
      subscribe('realtime_metrics');
    }

    return () => {
      unsubscribe('realtime_metrics');
    };
  }, [isConnected, subscribe, unsubscribe]);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => prev.map(metric => ({
        ...metric,
        change: (Math.random() - 0.5) * 10, // Random change between -5 and 5
      })));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Real-time Metrics
          </h3>
          <p className="text-sm text-gray-600">
            Live data from charging network
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-xs text-gray-600">
            {isConnected ? 'Live' : 'Offline'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <AnimatePresence>
          {metrics.map((metric, index) => (
            <motion.div
              key={metric.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-lg p-4 shadow-sm border border-gray-100"
            >
              <div className="flex items-center justify-between mb-2">
                <metric.icon className={`w-5 h-5 ${metric.color}`} />
                <motion.span
                  key={metric.change}
                  initial={{ scale: 1.2, color: metric.change >= 0 ? '#10B981' : '#EF4444' }}
                  animate={{ scale: 1, color: '#6B7280' }}
                  transition={{ duration: 0.3 }}
                  className={`text-xs font-medium ${
                    metric.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {metric.change >= 0 ? '+' : ''}{metric.change.toFixed(1)}%
                </motion.span>
              </div>
              
              <div>
                <motion.div
                  key={metric.value}
                  initial={{ scale: 1.1 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.2 }}
                  className="text-lg font-bold text-gray-900"
                >
                  {metric.value}
                </motion.div>
                <div className="text-xs text-gray-600">
                  {metric.label}
                </div>
              </div>

              {/* Pulse animation for active metrics */}
              {isConnected && (
                <motion.div
                  className="absolute inset-0 rounded-lg border-2 border-blue-200"
                  initial={{ opacity: 0, scale: 1 }}
                  animate={{ 
                    opacity: [0, 0.3, 0], 
                    scale: [1, 1.02, 1] 
                  }}
                  transition={{ 
                    duration: 2, 
                    repeat: Infinity,
                    delay: index * 0.5 
                  }}
                />
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Mini trend indicators */}
      <div className="mt-4 flex items-center justify-center space-x-1">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="w-1 bg-blue-300 rounded-full"
            animate={{
              height: [4, Math.random() * 16 + 4, 4],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: i * 0.1,
            }}
          />
        ))}
      </div>
    </div>
  );
}
