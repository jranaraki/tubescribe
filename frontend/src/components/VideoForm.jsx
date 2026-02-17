import React, { useState } from 'react';

export function VideoForm({ onSubmit, loading }) {
  const [urls, setUrls] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (urls.trim()) {
      const urlList = urls.split('\n').filter(url => url.trim());
      onSubmit(urlList);
      setUrls('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Add YouTube Videos</h2>
      <div>
        <label
          htmlFor="videoUrls"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          YouTube URLs (one per line)
        </label>
        <textarea
          id="videoUrls"
          rows={4}
          value={urls}
          onChange={(e) => setUrls(e.target.value)}
          placeholder="https://www.youtube.com/watch?v=..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={loading}
        />
      </div>
      <button
        type="submit"
        disabled={loading || !urls.trim()}
        className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Processing...' : 'Add Videos'}
      </button>
    </form>
  );
}