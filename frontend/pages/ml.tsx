import { useState } from 'react';
import Head from 'next/head';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import {
  CpuChipIcon,
  ClockIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  PlayIcon,
} from '@heroicons/react/24/outline';

import { api } from '../lib/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

// Validation schemas
const durationPredictionSchema = z.object({
  vehicle_model: z.string().min(1, 'Vehicle model is required'),
  battery_capacity_kwh: z.number().min(1, 'Battery capacity must be positive'),
  state_of_charge_start_percent: z.number().min(0).max(100),
  state_of_charge_target_percent: z.number().min(0).max(100),
  charger_type: z.enum(['Level 1', 'Level 2', 'DC Fast Charger']),
  temperature_celsius: z.number().min(-40).max(60),
  vehicle_age_years: z.number().min(0).max(50),
});

const costPredictionSchema = z.object({
  location: z.string().min(1, 'Location is required'),
  charger_type: z.enum(['Level 1', 'Level 2', 'DC Fast Charger']),
  energy_needed_kwh: z.number().min(0.1, 'Energy needed must be positive'),
  time_of_day: z.enum(['Morning', 'Afternoon', 'Evening', 'Night']),
  day_of_week: z.string().min(1, 'Day of week is required'),
  user_type: z.enum(['Commuter', 'Casual Driver', 'Long-Distance Traveler']),
  duration_hours: z.number().min(0.1).optional(),
});

type DurationFormData = z.infer<typeof durationPredictionSchema>;
type CostFormData = z.infer<typeof costPredictionSchema>;

export default function MLPredictions() {
  const [activeTab, setActiveTab] = useState<'duration' | 'cost'>('duration');
  const [durationResult, setDurationResult] = useState<any>(null);
  const [costResult, setCostResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const durationForm = useForm<DurationFormData>({
    resolver: zodResolver(durationPredictionSchema),
    defaultValues: {
      vehicle_model: 'Tesla Model 3',
      battery_capacity_kwh: 75,
      state_of_charge_start_percent: 20,
      state_of_charge_target_percent: 80,
      charger_type: 'Level 2',
      temperature_celsius: 20,
      vehicle_age_years: 2,
    },
  });

  const costForm = useForm<CostFormData>({
    resolver: zodResolver(costPredictionSchema),
    defaultValues: {
      location: 'Downtown Mall',
      charger_type: 'Level 2',
      energy_needed_kwh: 45,
      time_of_day: 'Evening',
      day_of_week: 'Monday',
      user_type: 'Commuter',
      duration_hours: 2.5,
    },
  });

  const onDurationSubmit = async (data: DurationFormData) => {
    setIsLoading(true);
    try {
      const response = await api.predictDuration(data);
      setDurationResult(response.data);
      toast.success('Duration prediction completed!');
    } catch (error) {
      toast.error('Failed to predict duration');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const onCostSubmit = async (data: CostFormData) => {
    setIsLoading(true);
    try {
      const response = await api.predictCost(data);
      setCostResult(response.data);
      toast.success('Cost prediction completed!');
    } catch (error) {
      toast.error('Failed to predict cost');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const tabs = [
    {
      id: 'duration',
      name: 'Duration Prediction',
      icon: ClockIcon,
      description: 'Predict charging session duration',
    },
    {
      id: 'cost',
      name: 'Cost Prediction',
      icon: CurrencyDollarIcon,
      description: 'Predict charging costs',
    },
  ];

  return (
    <>
      <Head>
        <title>ML Predictions - EV Charging Analytics</title>
      </Head>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center space-x-3">
          <CpuChipIcon className="w-8 h-8 text-primary-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Machine Learning Predictions
            </h1>
            <p className="text-gray-600 mt-1">
              Get AI-powered predictions for charging duration and costs
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as 'duration' | 'cost')}
                className={`group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon
                  className={`-ml-0.5 mr-2 h-5 w-5 ${
                    activeTab === tab.id
                      ? 'text-primary-500'
                      : 'text-gray-400 group-hover:text-gray-500'
                  }`}
                />
                <div className="text-left">
                  <div>{tab.name}</div>
                  <div className="text-xs text-gray-500">{tab.description}</div>
                </div>
              </button>
            ))}
          </nav>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">
                {activeTab === 'duration' ? 'Duration Prediction' : 'Cost Prediction'}
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Enter the parameters below to get a prediction
              </p>
            </div>

            <div className="card-body">
              {activeTab === 'duration' ? (
                <form onSubmit={durationForm.handleSubmit(onDurationSubmit)} className="space-y-4">
                  <div>
                    <label className="form-label">Vehicle Model</label>
                    <input
                      {...durationForm.register('vehicle_model')}
                      className="form-input"
                      placeholder="e.g., Tesla Model 3"
                    />
                    {durationForm.formState.errors.vehicle_model && (
                      <p className="form-error">
                        {durationForm.formState.errors.vehicle_model.message}
                      </p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="form-label">Battery Capacity (kWh)</label>
                      <input
                        type="number"
                        step="0.1"
                        {...durationForm.register('battery_capacity_kwh', { valueAsNumber: true })}
                        className="form-input"
                      />
                    </div>
                    <div>
                      <label className="form-label">Vehicle Age (years)</label>
                      <input
                        type="number"
                        step="0.1"
                        {...durationForm.register('vehicle_age_years', { valueAsNumber: true })}
                        className="form-input"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="form-label">Start SoC (%)</label>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        {...durationForm.register('state_of_charge_start_percent', { valueAsNumber: true })}
                        className="form-input"
                      />
                    </div>
                    <div>
                      <label className="form-label">Target SoC (%)</label>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        {...durationForm.register('state_of_charge_target_percent', { valueAsNumber: true })}
                        className="form-input"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="form-label">Charger Type</label>
                      <select {...durationForm.register('charger_type')} className="form-select">
                        <option value="Level 1">Level 1</option>
                        <option value="Level 2">Level 2</option>
                        <option value="DC Fast Charger">DC Fast Charger</option>
                      </select>
                    </div>
                    <div>
                      <label className="form-label">Temperature (°C)</label>
                      <input
                        type="number"
                        {...durationForm.register('temperature_celsius', { valueAsNumber: true })}
                        className="form-input"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="btn-primary w-full"
                  >
                    {isLoading ? (
                      <LoadingSpinner size="small" color="white" />
                    ) : (
                      <>
                        <PlayIcon className="w-4 h-4 mr-2" />
                        Predict Duration
                      </>
                    )}
                  </button>
                </form>
              ) : (
                <form onSubmit={costForm.handleSubmit(onCostSubmit)} className="space-y-4">
                  <div>
                    <label className="form-label">Location</label>
                    <input
                      {...costForm.register('location')}
                      className="form-input"
                      placeholder="e.g., Downtown Mall"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="form-label">Charger Type</label>
                      <select {...costForm.register('charger_type')} className="form-select">
                        <option value="Level 1">Level 1</option>
                        <option value="Level 2">Level 2</option>
                        <option value="DC Fast Charger">DC Fast Charger</option>
                      </select>
                    </div>
                    <div>
                      <label className="form-label">Energy Needed (kWh)</label>
                      <input
                        type="number"
                        step="0.1"
                        {...costForm.register('energy_needed_kwh', { valueAsNumber: true })}
                        className="form-input"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="form-label">Time of Day</label>
                      <select {...costForm.register('time_of_day')} className="form-select">
                        <option value="Morning">Morning</option>
                        <option value="Afternoon">Afternoon</option>
                        <option value="Evening">Evening</option>
                        <option value="Night">Night</option>
                      </select>
                    </div>
                    <div>
                      <label className="form-label">Day of Week</label>
                      <select {...costForm.register('day_of_week')} className="form-select">
                        <option value="Monday">Monday</option>
                        <option value="Tuesday">Tuesday</option>
                        <option value="Wednesday">Wednesday</option>
                        <option value="Thursday">Thursday</option>
                        <option value="Friday">Friday</option>
                        <option value="Saturday">Saturday</option>
                        <option value="Sunday">Sunday</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="form-label">User Type</label>
                      <select {...costForm.register('user_type')} className="form-select">
                        <option value="Commuter">Commuter</option>
                        <option value="Casual Driver">Casual Driver</option>
                        <option value="Long-Distance Traveler">Long-Distance Traveler</option>
                      </select>
                    </div>
                    <div>
                      <label className="form-label">Duration (hours)</label>
                      <input
                        type="number"
                        step="0.1"
                        {...costForm.register('duration_hours', { valueAsNumber: true })}
                        className="form-input"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="btn-primary w-full"
                  >
                    {isLoading ? (
                      <LoadingSpinner size="small" color="white" />
                    ) : (
                      <>
                        <PlayIcon className="w-4 h-4 mr-2" />
                        Predict Cost
                      </>
                    )}
                  </button>
                </form>
              )}
            </div>
          </div>

          {/* Results */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">
                Prediction Results
              </h3>
            </div>

            <div className="card-body">
              {activeTab === 'duration' && durationResult ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-4"
                >
                  <div className="text-center">
                    <div className="text-3xl font-bold text-primary-600">
                      {durationResult.predicted_duration_hours.toFixed(1)} hours
                    </div>
                    <div className="text-sm text-gray-600">
                      Predicted charging duration
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-gray-600">Confidence Score</div>
                      <div className="font-semibold">
                        {(durationResult.confidence_score * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-gray-600">Estimated Energy</div>
                      <div className="font-semibold">
                        {durationResult.estimated_energy_kwh.toFixed(1)} kWh
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">
                      Factor Analysis
                    </h4>
                    <div className="space-y-2">
                      {Object.entries(durationResult.factors_analysis || {})
                        .slice(0, 5)
                        .map(([factor, importance]: [string, any]) => (
                          <div key={factor} className="flex items-center justify-between">
                            <span className="text-sm text-gray-600 capitalize">
                              {factor.replace(/_/g, ' ')}
                            </span>
                            <div className="flex items-center space-x-2">
                              <div className="w-16 bg-gray-200 rounded-full h-2">
                                <div
                                  className="bg-primary-500 h-2 rounded-full"
                                  style={{ width: `${importance * 100}%` }}
                                />
                              </div>
                              <span className="text-xs text-gray-500 w-8">
                                {(importance * 100).toFixed(0)}%
                              </span>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                </motion.div>
              ) : activeTab === 'cost' && costResult ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-4"
                >
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">
                      ${costResult.predicted_cost_usd.toFixed(2)}
                    </div>
                    <div className="text-sm text-gray-600">
                      Predicted charging cost
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-gray-600">Cost per kWh</div>
                      <div className="font-semibold">
                        ${costResult.cost_per_kwh.toFixed(3)}
                      </div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-gray-600">Confidence Score</div>
                      <div className="font-semibold">
                        {(costResult.confidence_score * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">
                      Optimization Suggestions
                    </h4>
                    <ul className="space-y-1 text-sm text-gray-600">
                      {costResult.optimization_suggestions?.map((suggestion: string, index: number) => (
                        <li key={index} className="flex items-start">
                          <span className="text-primary-500 mr-2">•</span>
                          {suggestion}
                        </li>
                      ))}
                    </ul>
                  </div>
                </motion.div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <ChartBarIcon className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Run a prediction to see results here</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
