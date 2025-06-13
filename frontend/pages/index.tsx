import { useState, useEffect } from 'react';
import Head from 'next/head';
import useSWR from 'swr';
import { motion } from 'framer-motion';
import {
  ChartBarIcon,
  BoltIcon,
  CurrencyDollarIcon,
  ClockIcon,
  MapPinIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';

import DashboardCard from '../components/DashboardCard';
import ChargingPatternsChart from '../components/charts/ChargingPatternsChart';
import CostAnalysisChart from '../components/charts/CostAnalysisChart';
import LocationUsageMap from '../components/charts/LocationUsageMap';
import UsageHeatmap from '../components/charts/UsageHeatmap';
import DataEngineeringMetrics from '../components/DataEngineeringMetrics';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

interface AnalyticsOverview {
  overall_metrics: {
    total_sessions: number;
    total_energy_kwh: number;
    total_cost_usd: number;
    avg_duration_hours: number;
    avg_cost_per_session: number;
    avg_energy_per_session: number;
  };
  location_breakdown: Array<{
    location: string;
    session_count: number;
    total_energy_kwh: number;
    avg_cost_usd: number;
    utilization_rate: number;
  }>;
  daily_trends: Array<{
    timestamp: string;
    value: number;
    label?: string;
  }>;
  peak_hours: Array<{
    hour: number;
    session_count: number;
    avg_cost: number;
  }>;
  user_type_distribution: Record<string, number>;
  charger_type_usage: Record<string, number>;
}

export default function DataAnalyticsDashboard() {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
    end: new Date(),
  });

  const { data: analytics, error, isLoading } = useSWR<AnalyticsOverview>(
    `/api/v1/analytics/overview?start_date=${dateRange.start.toISOString()}&end_date=${dateRange.end.toISOString()}`
  );

  if (error) {
    return <ErrorMessage message="Failed to load dashboard data" />;
  }

  if (isLoading || !analytics) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  const { overall_metrics, location_breakdown, daily_trends, peak_hours, user_type_distribution, charger_type_usage } = analytics;

  return (
    <>
      <Head>
        <title>Data Analytics Dashboard - EV Charging</title>
      </Head>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Data Analytics Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Electric Vehicle Charging Data Analysis & Engineering
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <select
              className="rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              onChange={(e) => {
                const days = parseInt(e.target.value);
                setDateRange({
                  start: new Date(Date.now() - days * 24 * 60 * 60 * 1000),
                  end: new Date(),
                });
              }}
            >
              <option value="7">Last 7 days</option>
              <option value="30" selected>Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="365">Last year</option>
            </select>
          </div>
        </div>

        {/* Data Quality Metrics */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                Data Quality Overview
              </h3>
              <p className="text-sm text-gray-600">
                Current data health and processing status
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <span className="text-xs text-gray-600">
                Data Pipeline Active
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Data Completeness</span>
                <span className="text-sm font-medium text-green-600">95.2%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '95.2%' }} />
              </div>
            </div>

            <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Processing Rate</span>
                <span className="text-sm font-medium text-blue-600">1.2k/min</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: '78%' }} />
              </div>
            </div>

            <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Data Freshness</span>
                <span className="text-sm font-medium text-purple-600">2 min ago</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-purple-500 h-2 rounded-full" style={{ width: '92%' }} />
              </div>
            </div>

            <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Error Rate</span>
                <span className="text-sm font-medium text-yellow-600">0.3%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '3%' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Key Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <DashboardCard
              title="Total Sessions"
              value={overall_metrics.total_sessions.toLocaleString()}
              icon={ChartBarIcon}
              color="blue"
              trend={{ value: 12.5, isPositive: true }}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <DashboardCard
              title="Total Energy"
              value={`${(overall_metrics.total_energy_kwh / 1000).toFixed(1)}MWh`}
              icon={BoltIcon}
              color="yellow"
              trend={{ value: 8.3, isPositive: true }}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <DashboardCard
              title="Total Cost"
              value={`$${overall_metrics.total_cost_usd.toLocaleString()}`}
              icon={CurrencyDollarIcon}
              color="green"
              trend={{ value: 15.2, isPositive: true }}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <DashboardCard
              title="Avg Duration"
              value={`${overall_metrics.avg_duration_hours.toFixed(1)}h`}
              icon={ClockIcon}
              color="purple"
              trend={{ value: -2.1, isPositive: false }}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <DashboardCard
              title="Avg Cost/Session"
              value={`$${overall_metrics.avg_cost_per_session.toFixed(2)}`}
              icon={CurrencyDollarIcon}
              color="indigo"
              trend={{ value: 5.7, isPositive: true }}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <DashboardCard
              title="Active Locations"
              value={location_breakdown.length.toString()}
              icon={MapPinIcon}
              color="pink"
              trend={{ value: 3, isPositive: true }}
            />
          </motion.div>
        </div>

        {/* Usage Heatmap */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.7 }}
          className="bg-white rounded-xl shadow-soft p-6"
        >
          <UsageHeatmap />
        </motion.div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Charging Patterns */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.8 }}
            className="bg-white rounded-xl shadow-soft p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Daily Charging Trends
            </h3>
            <ChargingPatternsChart data={daily_trends} />
          </motion.div>

          {/* Cost Analysis */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.9 }}
            className="bg-white rounded-xl shadow-soft p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Cost Distribution by Location
            </h3>
            <CostAnalysisChart data={location_breakdown} />
          </motion.div>
        </div>

        {/* Data Engineering Metrics - Temporarily disabled */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 1.0 }}
          className="bg-white rounded-xl shadow-soft p-6"
        >
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Data Engineering Metrics
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="text-2xl font-bold text-green-600">98.5%</div>
                <div className="text-sm font-medium text-green-800">Pipeline Health</div>
                <div className="text-xs text-green-600">Overall uptime</div>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-600">1.2s</div>
                <div className="text-sm font-medium text-blue-800">Processing Latency</div>
                <div className="text-xs text-blue-600">Average response time</div>
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-600">1.2k/min</div>
                <div className="text-sm font-medium text-purple-800">Throughput</div>
                <div className="text-xs text-purple-600">Records processed</div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Location Usage Map */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 1.2 }}
          className="bg-white rounded-xl shadow-soft p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Location Usage Overview
          </h3>
          <LocationUsageMap data={location_breakdown} />
        </motion.div>
      </div>
    </>
  );
}
