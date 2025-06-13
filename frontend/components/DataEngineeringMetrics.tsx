// Simple icons as components to avoid import issues
const DatabaseIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125S3.75 19.903 3.75 17.625V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18S3.75 16.153 3.75 13.875v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125S3.75 12.153 3.75 9.875v-3.75" />
  </svg>
);

const CpuChipIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 0 0 2.25-2.25V6.75a2.25 2.25 0 0 0-2.25-2.25H6.75A2.25 2.25 0 0 0 4.5 6.75v10.5a2.25 2.25 0 0 0 2.25 2.25Zm.75-12h9v9h-9v-9Z" />
  </svg>
);

const ClockIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
  </svg>
);

const CheckCircleIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
  </svg>
);

const ExclamationTriangleIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
  </svg>
);

const ArrowTrendingUpIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18 9 11.25l4.306 4.306a11.95 11.95 0 0 1 5.814-5.518l2.74-1.22m0 0-5.94-2.281m5.94 2.28-2.28 5.941" />
  </svg>
);

interface MetricCardProps {
  title: string;
  value: string;
  change?: string;
  status: 'good' | 'warning' | 'error';
  icon: React.ComponentType<any>;
  description: string;
}

function MetricCard({ title, value, change, status, icon: Icon, description }: MetricCardProps) {
  const statusColors = {
    good: 'text-green-600 bg-green-50 border-green-200',
    warning: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    error: 'text-red-600 bg-red-50 border-red-200',
  };

  const statusIcons = {
    good: CheckCircleIcon,
    warning: ExclamationTriangleIcon,
    error: ExclamationTriangleIcon,
  };

  const StatusIcon = statusIcons[status];

  return (
    <div className={`rounded-lg border p-4 ${statusColors[status]}`}>
      <div className="flex items-center justify-between mb-2">
        <Icon className="w-5 h-5" />
        <StatusIcon className="w-4 h-4" />
      </div>
      <div className="space-y-1">
        <div className="text-2xl font-bold">{value}</div>
        <div className="text-sm font-medium">{title}</div>
        <div className="text-xs opacity-75">{description}</div>
        {change && (
          <div className="flex items-center text-xs">
            <ArrowTrendingUpIcon className="w-3 h-3 mr-1" />
            {change}
          </div>
        )}
      </div>
    </div>
  );
}

export default function DataEngineeringMetrics() {
  const metrics = [
    {
      title: 'Data Pipeline Health',
      value: '98.5%',
      change: '+0.2% from yesterday',
      status: 'good' as const,
      icon: DatabaseIcon,
      description: 'Overall pipeline uptime',
    },
    {
      title: 'Processing Latency',
      value: '1.2s',
      change: '-0.3s improvement',
      status: 'good' as const,
      icon: ClockIcon,
      description: 'Avg data processing time',
    },
    {
      title: 'Data Quality Score',
      value: '95.2%',
      change: '+1.1% this week',
      status: 'good' as const,
      icon: CheckCircleIcon,
      description: 'Completeness & accuracy',
    },
    {
      title: 'Error Rate',
      value: '0.3%',
      change: '+0.1% from last hour',
      status: 'warning' as const,
      icon: ExclamationTriangleIcon,
      description: 'Failed processing jobs',
    },
    {
      title: 'Throughput',
      value: '1.2k/min',
      change: '+15% peak capacity',
      status: 'good' as const,
      icon: CpuChipIcon,
      description: 'Records processed/min',
    },
    {
      title: 'Storage Utilization',
      value: '73%',
      change: '+2% this month',
      status: 'good' as const,
      icon: DatabaseIcon,
      description: 'Data warehouse usage',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Data Engineering Metrics
          </h3>
          <p className="text-sm text-gray-600">
            Real-time monitoring of data pipeline performance
          </p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span>Live monitoring</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {metrics.map((metric, index) => (
          <div key={metric.title}>
            <MetricCard {...metric} />
          </div>
        ))}
      </div>

      {/* Data Flow Diagram */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h4 className="font-medium text-gray-900 mb-4">Data Flow Overview</h4>
        <div className="flex items-center justify-between">
          <div className="flex flex-col items-center space-y-2">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <DatabaseIcon className="w-6 h-6 text-blue-600" />
            </div>
            <span className="text-sm font-medium text-gray-700">Raw Data</span>
            <span className="text-xs text-gray-500">CSV, JSON</span>
          </div>
          
          <div className="flex-1 mx-4">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center">
                <span className="bg-white px-2 text-xs text-gray-500">ETL Pipeline</span>
              </div>
            </div>
          </div>
          
          <div className="flex flex-col items-center space-y-2">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <CpuChipIcon className="w-6 h-6 text-green-600" />
            </div>
            <span className="text-sm font-medium text-gray-700">Processing</span>
            <span className="text-xs text-gray-500">Validation</span>
          </div>
          
          <div className="flex-1 mx-4">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center">
                <span className="bg-white px-2 text-xs text-gray-500">Analytics</span>
              </div>
            </div>
          </div>
          
          <div className="flex flex-col items-center space-y-2">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <DatabaseIcon className="w-6 h-6 text-purple-600" />
            </div>
            <span className="text-sm font-medium text-gray-700">Data Warehouse</span>
            <span className="text-xs text-gray-500">PostgreSQL</span>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h4 className="font-medium text-gray-900 mb-4">Recent Pipeline Activity</h4>
        <div className="space-y-3">
          {[
            { time: '2 min ago', event: 'Batch processing completed', status: 'success', records: '1,247 records' },
            { time: '5 min ago', event: 'Data validation passed', status: 'success', records: '856 records' },
            { time: '8 min ago', event: 'Schema validation warning', status: 'warning', records: '12 records' },
            { time: '12 min ago', event: 'ETL job started', status: 'info', records: 'Processing...' },
          ].map((activity, index) => (
            <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
              <div className="flex items-center space-x-3">
                <div className={`w-2 h-2 rounded-full ${
                  activity.status === 'success' ? 'bg-green-500' :
                  activity.status === 'warning' ? 'bg-yellow-500' :
                  'bg-blue-500'
                }`}></div>
                <div>
                  <div className="text-sm font-medium text-gray-900">{activity.event}</div>
                  <div className="text-xs text-gray-500">{activity.time}</div>
                </div>
              </div>
              <div className="text-sm text-gray-600">{activity.records}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
