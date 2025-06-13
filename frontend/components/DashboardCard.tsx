import { motion } from 'framer-motion';
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid';

interface DashboardCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<any>;
  color: 'blue' | 'green' | 'yellow' | 'purple' | 'pink' | 'indigo';
  trend?: {
    value: number;
    isPositive: boolean;
  };
  subtitle?: string;
  onClick?: () => void;
}

const colorClasses = {
  blue: {
    bg: 'bg-blue-50',
    icon: 'text-blue-600',
    trend: 'text-blue-600',
  },
  green: {
    bg: 'bg-green-50',
    icon: 'text-green-600',
    trend: 'text-green-600',
  },
  yellow: {
    bg: 'bg-yellow-50',
    icon: 'text-yellow-600',
    trend: 'text-yellow-600',
  },
  purple: {
    bg: 'bg-purple-50',
    icon: 'text-purple-600',
    trend: 'text-purple-600',
  },
  pink: {
    bg: 'bg-pink-50',
    icon: 'text-pink-600',
    trend: 'text-pink-600',
  },
  indigo: {
    bg: 'bg-indigo-50',
    icon: 'text-indigo-600',
    trend: 'text-indigo-600',
  },
};

export default function DashboardCard({
  title,
  value,
  icon: Icon,
  color,
  trend,
  subtitle,
  onClick,
}: DashboardCardProps) {
  const colors = colorClasses[color];

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`card p-6 cursor-pointer transition-all hover:shadow-medium ${
        onClick ? 'hover:bg-gray-50' : ''
      }`}
      onClick={onClick}
    >
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <div className={`w-12 h-12 rounded-lg ${colors.bg} flex items-center justify-center`}>
            <Icon className={`w-6 h-6 ${colors.icon}`} />
          </div>
        </div>
        
        <div className="ml-4 flex-1">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{title}</p>
              <p className="text-2xl font-bold text-gray-900">{value}</p>
              {subtitle && (
                <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
              )}
            </div>
            
            {trend && (
              <div className="flex items-center space-x-1">
                {trend.isPositive ? (
                  <ArrowUpIcon className="w-4 h-4 text-green-500" />
                ) : (
                  <ArrowDownIcon className="w-4 h-4 text-red-500" />
                )}
                <span
                  className={`text-sm font-medium ${
                    trend.isPositive ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {Math.abs(trend.value)}%
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
