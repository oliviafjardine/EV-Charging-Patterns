import { useState, useCallback } from 'react';
import Head from 'next/head';
import { motion } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import useSWR from 'swr';
import toast from 'react-hot-toast';
import {
  CloudArrowUpIcon,
  DocumentChartBarIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowDownTrayIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';

import { api } from '../lib/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

interface UploadResult {
  filename: string;
  records_processed: number;
  records_created: number;
  records_updated: number;
  records_failed: number;
  message: string;
}

interface ValidationResult {
  filename: string;
  total_rows: number;
  total_columns: number;
  columns: string[];
  missing_values: Record<string, number>;
  validation_errors: string[];
  warnings: string[];
  is_valid: boolean;
}

export default function DataManagement() {
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);

  // Fetch data statistics
  const { data: statistics, error: statsError } = useSWR('/api/v1/data/statistics');
  const { data: qualityReport, error: qualityError } = useSWR('/api/v1/data/quality-report');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file first
    setIsValidating(true);
    try {
      const response = await api.validateData(file);
      setValidationResult(response.data);
      
      if (response.data.is_valid) {
        toast.success('File validation passed!');
      } else {
        toast.error('File validation failed. Please check the errors below.');
      }
    } catch (error) {
      toast.error('Failed to validate file');
      console.error(error);
    } finally {
      setIsValidating(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const handleUpload = async () => {
    if (!validationResult || !validationResult.is_valid) {
      toast.error('Please validate the file first');
      return;
    }

    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = fileInput?.files?.[0];
    
    if (!file) {
      toast.error('No file selected');
      return;
    }

    setIsUploading(true);
    try {
      const response = await api.uploadData(file);
      setUploadResult(response.data);
      toast.success('Data uploaded successfully!');
      
      // Refresh statistics
      // mutate('/api/v1/data/statistics');
    } catch (error) {
      toast.error('Failed to upload data');
      console.error(error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleExport = async (format: string) => {
    try {
      const response = await api.exportData({ format });
      const { download_url } = response.data;
      
      // Create download link
      const link = document.createElement('a');
      link.href = download_url;
      link.download = response.data.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast.success('Export started!');
    } catch (error) {
      toast.error('Failed to export data');
      console.error(error);
    }
  };

  return (
    <>
      <Head>
        <title>Data Management - EV Charging Analytics</title>
      </Head>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center space-x-3">
          <CloudArrowUpIcon className="w-8 h-8 text-primary-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Data Management
            </h1>
            <p className="text-gray-600 mt-1">
              Upload, validate, and manage charging session data
            </p>
          </div>
        </div>

        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <DocumentChartBarIcon className="w-8 h-8 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Sessions</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {statistics.total_sessions.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <DocumentChartBarIcon className="w-8 h-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Users</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {statistics.total_users.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <DocumentChartBarIcon className="w-8 h-8 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Stations</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {statistics.total_stations.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <DocumentChartBarIcon className="w-8 h-8 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Energy</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {(statistics.total_energy_kwh / 1000).toFixed(1)} MWh
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* File Upload */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">
                Upload Data
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Upload CSV files with charging session data
              </p>
            </div>

            <div className="card-body">
              {/* Dropzone */}
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-primary-400 bg-primary-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <input {...getInputProps()} />
                <CloudArrowUpIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                {isDragActive ? (
                  <p className="text-primary-600">Drop the file here...</p>
                ) : (
                  <div>
                    <p className="text-gray-600 mb-2">
                      Drag and drop a CSV file here, or click to select
                    </p>
                    <p className="text-sm text-gray-500">
                      Maximum file size: 50MB
                    </p>
                  </div>
                )}
              </div>

              {/* Validation Results */}
              {isValidating && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center">
                    <LoadingSpinner size="small" />
                    <span className="ml-2 text-sm text-blue-700">
                      Validating file...
                    </span>
                  </div>
                </div>
              )}

              {validationResult && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 space-y-4"
                >
                  {/* Validation Summary */}
                  <div className={`p-4 rounded-lg ${
                    validationResult.is_valid 
                      ? 'bg-green-50 border border-green-200' 
                      : 'bg-red-50 border border-red-200'
                  }`}>
                    <div className="flex items-center">
                      {validationResult.is_valid ? (
                        <CheckCircleIcon className="w-5 h-5 text-green-500 mr-2" />
                      ) : (
                        <ExclamationTriangleIcon className="w-5 h-5 text-red-500 mr-2" />
                      )}
                      <span className={`font-medium ${
                        validationResult.is_valid ? 'text-green-800' : 'text-red-800'
                      }`}>
                        {validationResult.is_valid ? 'Validation Passed' : 'Validation Failed'}
                      </span>
                    </div>
                  </div>

                  {/* File Info */}
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">File Information</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Filename:</span>
                        <span className="ml-2 font-medium">{validationResult.filename}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Rows:</span>
                        <span className="ml-2 font-medium">{validationResult.total_rows.toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Columns:</span>
                        <span className="ml-2 font-medium">{validationResult.total_columns}</span>
                      </div>
                    </div>
                  </div>

                  {/* Validation Errors */}
                  {validationResult.validation_errors.length > 0 && (
                    <div className="bg-red-50 p-4 rounded-lg">
                      <h4 className="font-medium text-red-800 mb-2">Validation Errors</h4>
                      <ul className="text-sm text-red-700 space-y-1">
                        {validationResult.validation_errors.map((error, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-red-500 mr-2">•</span>
                            {error}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Warnings */}
                  {validationResult.warnings.length > 0 && (
                    <div className="bg-yellow-50 p-4 rounded-lg">
                      <h4 className="font-medium text-yellow-800 mb-2">Warnings</h4>
                      <ul className="text-sm text-yellow-700 space-y-1">
                        {validationResult.warnings.map((warning, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-yellow-500 mr-2">•</span>
                            {warning}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Upload Button */}
                  {validationResult.is_valid && (
                    <button
                      onClick={handleUpload}
                      disabled={isUploading}
                      className="btn-primary w-full"
                    >
                      {isUploading ? (
                        <LoadingSpinner size="small" color="white" />
                      ) : (
                        <>
                          <CloudArrowUpIcon className="w-4 h-4 mr-2" />
                          Upload Data
                        </>
                      )}
                    </button>
                  )}
                </motion.div>
              )}

              {/* Upload Results */}
              {uploadResult && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 bg-green-50 p-4 rounded-lg border border-green-200"
                >
                  <div className="flex items-center mb-2">
                    <CheckCircleIcon className="w-5 h-5 text-green-500 mr-2" />
                    <span className="font-medium text-green-800">Upload Completed</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-green-700">Records Processed:</span>
                      <span className="ml-2 font-medium">{uploadResult.records_processed}</span>
                    </div>
                    <div>
                      <span className="text-green-700">Records Created:</span>
                      <span className="ml-2 font-medium">{uploadResult.records_created}</span>
                    </div>
                    <div>
                      <span className="text-green-700">Records Updated:</span>
                      <span className="ml-2 font-medium">{uploadResult.records_updated}</span>
                    </div>
                    <div>
                      <span className="text-green-700">Records Failed:</span>
                      <span className="ml-2 font-medium">{uploadResult.records_failed}</span>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </div>

          {/* Data Quality Report */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">
                Data Quality Report
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Current data quality metrics and recommendations
              </p>
            </div>

            <div className="card-body">
              {qualityError && (
                <ErrorMessage message="Failed to load data quality report" />
              )}

              {qualityReport && (
                <div className="space-y-4">
                  {/* Overall Score */}
                  <div className="text-center">
                    <div className="text-3xl font-bold text-primary-600">
                      {qualityReport.overall_score.toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">Overall Quality Score</div>
                  </div>

                  {/* Quality Metrics */}
                  <div className="space-y-3">
                    {qualityReport.metrics.map((metric: any, index: number) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">{metric.metric_name}</span>
                        <div className="flex items-center space-x-2">
                          <span className={`text-sm font-medium ${
                            metric.status === 'good' ? 'text-green-600' : 'text-yellow-600'
                          }`}>
                            {typeof metric.value === 'number' ? metric.value.toFixed(1) : metric.value}
                          </span>
                          <div className={`w-3 h-3 rounded-full ${
                            metric.status === 'good' ? 'bg-green-500' : 'bg-yellow-500'
                          }`} />
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Recommendations */}
                  {qualityReport.recommendations.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Recommendations</h4>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {qualityReport.recommendations.map((rec: string, index: number) => (
                          <li key={index} className="flex items-start">
                            <span className="text-primary-500 mr-2">•</span>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Export Data */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">
              Export Data
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Download charging session data in various formats
            </p>
          </div>

          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={() => handleExport('csv')}
                className="btn-outline flex items-center justify-center"
              >
                <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
                Export as CSV
              </button>
              
              <button
                onClick={() => handleExport('json')}
                className="btn-outline flex items-center justify-center"
              >
                <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
                Export as JSON
              </button>
              
              <button
                onClick={() => handleExport('parquet')}
                className="btn-outline flex items-center justify-center"
              >
                <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
                Export as Parquet
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
