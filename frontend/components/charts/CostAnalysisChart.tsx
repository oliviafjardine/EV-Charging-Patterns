import { useEffect, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface CostAnalysisChartProps {
  data: Array<{
    location: string;
    session_count: number;
    total_energy_kwh: number;
    avg_cost_usd: number;
    utilization_rate: number;
  }>;
  height?: number;
}

export default function CostAnalysisChart({ 
  data, 
  height = 300 
}: CostAnalysisChartProps) {
  const chartRef = useRef<ChartJS<'bar'>>(null);

  const chartData = {
    labels: data.map(item => item.location),
    datasets: [
      {
        label: 'Average Cost ($)',
        data: data.map(item => item.avg_cost_usd),
        backgroundColor: 'rgba(34, 197, 94, 0.8)',
        borderColor: 'rgb(34, 197, 94)',
        borderWidth: 1,
        borderRadius: 4,
        borderSkipped: false,
      },
      {
        label: 'Session Count',
        data: data.map(item => item.session_count),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
        borderRadius: 4,
        borderSkipped: false,
        yAxisID: 'y1',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12,
          },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(59, 130, 246, 0.5)',
        borderWidth: 1,
        cornerRadius: 8,
        callbacks: {
          title: (context: any) => {
            return context[0].label;
          },
          label: (context: any) => {
            const datasetLabel = context.dataset.label;
            const value = context.parsed.y;
            
            if (datasetLabel === 'Average Cost ($)') {
              return `${datasetLabel}: $${value.toFixed(2)}`;
            } else {
              return `${datasetLabel}: ${value}`;
            }
          },
          afterBody: (context: any) => {
            const index = context[0].dataIndex;
            const item = data[index];
            return [
              `Total Energy: ${item.total_energy_kwh.toFixed(1)} kWh`,
              `Utilization: ${(item.utilization_rate * 100).toFixed(1)}%`
            ];
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: '#6B7280',
          font: {
            size: 11,
          },
          maxRotation: 45,
        },
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        beginAtZero: true,
        grid: {
          color: 'rgba(107, 114, 128, 0.1)',
        },
        ticks: {
          color: '#6B7280',
          font: {
            size: 12,
          },
          callback: function(value: any) {
            return '$' + value.toFixed(0);
          },
        },
        title: {
          display: true,
          text: 'Average Cost ($)',
          color: '#6B7280',
          font: {
            size: 12,
          },
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        beginAtZero: true,
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          color: '#6B7280',
          font: {
            size: 12,
          },
          callback: function(value: any) {
            return Math.round(value);
          },
        },
        title: {
          display: true,
          text: 'Session Count',
          color: '#6B7280',
          font: {
            size: 12,
          },
        },
      },
    },
    interaction: {
      intersect: false,
      mode: 'index' as const,
    },
  };

  return (
    <div style={{ height: `${height}px` }} className="relative">
      <Bar ref={chartRef} data={chartData} options={options} />
    </div>
  );
}
