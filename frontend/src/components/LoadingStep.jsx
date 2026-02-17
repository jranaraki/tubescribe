import React, { useEffect } from 'react';

export function LoadingStep({ status, currentStep, progress }) {
  const steps = [
    { key: 'queued', label: 'Waiting', icon: '⏳' },
    { key: 'downloading', label: 'Downloading', icon: '⬇️' },
    { key: 'transcribing', label: 'Transcribing', icon: '🎤' },
    { key: 'summarizing', label: 'Summarizing', icon: '🤖' },
    { key: 'categorizing', label: 'Categorizing', icon: '📂' },
    { key: 'completed', label: 'Complete', icon: '✅' },
  ];

  const currentStepIndex = steps.findIndex(s => currentStep?.toLowerCase().includes(s.key) || status === s.key);

  return (
    <div className="mt-3 p-3 bg-gray-50 rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-700">
          {currentStep || 'Initializing...'}
        </span>
        <span className="text-sm text-gray-500">{progress}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="flex justify-between mt-2 text-xs text-gray-500">
        {steps.map((step, index) => (
          <div
            key={step.key}
            className={`flex items-center gap-1 transition-colors duration-300 ${
              index <= currentStepIndex ? 'text-blue-600' : 'text-gray-300'
            }`}
          >
            <span>{step.icon}</span>
          </div>
        ))}
      </div>
    </div>
  );
}