import React from 'react';
import { LoadingStep } from './LoadingStep';

export function VideoCard({ video, showProgress, onDelete }) {
  const { status, currentStep, progress, error_message, current_step } = video;

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'queued':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      {video.thumbnail_url && (
        <div className="relative aspect-video bg-gray-200">
          <img
            src={video.thumbnail_url}
            alt={video.title}
            className="w-full h-full object-cover"
          />
          {video.category && (
            <div
              className="absolute top-2 right-2 px-2 py-1 text-xs font-medium rounded-full text-white"
              style={{ backgroundColor: video.category.color }}
            >
              {video.category.name}
            </div>
          )}
        </div>
      )}
      
      <div className="p-4">
        <div className="flex items-start justify-between gap-2 mb-2">
          <h3 className="font-semibold text-gray-800 line-clamp-2 text-sm">
            {video.title}
          </h3>
          <span
            className={`px-2 py-1 text-xs font-medium rounded-full whitespace-nowrap ${getStatusColor(status)}`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </span>
        </div>

        {(status === 'processing' || status === 'queued') && showProgress && (
          <LoadingStep
            status={status}
            currentStep={current_step || currentStep}
            progress={progress || 0}
          />
        )}

        {status === 'error' && (
          <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-600">
            {error_message || 'An error occurred'}
          </div>
        )}

        {status === 'completed' && video.summary && (
          <div className="mt-3 p-3 bg-gray-50 rounded">
            <h4 className="font-medium text-gray-700 text-sm mb-2">Summary:</h4>
            <p className="text-sm text-gray-600 whitespace-pre-wrap leading-relaxed">
              {video.summary}
            </p>
          </div>
        )}

        <div className="mt-4 flex gap-2">
          <a
            href={video.youtube_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 bg-red-600 text-white py-2 px-3 rounded text-sm font-medium hover:bg-red-700 transition-colors text-center"
          >
            Watch on YouTube
          </a>
          <button
            onClick={() => onDelete(video.id)}
            className="px-3 py-2 bg-gray-200 text-gray-700 rounded text-sm font-medium hover:bg-gray-300 transition-colors"
            disabled={status === 'processing'}
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}