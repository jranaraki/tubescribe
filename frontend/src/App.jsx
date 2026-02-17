import React, { useState, useEffect } from 'react';
import { VideoForm } from './components/VideoForm';
import { CategoryFilter } from './components/CategoryFilter';
import { VideoCard } from './components/VideoCard';
import { useVideos, useCategories, useWebSocket } from './hooks/useVideos';

function App() {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [isAddingVideos, setIsAddingVideos] = useState(false);
  const [, forceUpdate] = useState(0);
  
  const { videos: fetchedVideos, loading, error, addVideos, deleteVideo, refetch } = useVideos(selectedCategory);
  const { categories } = useCategories();
  const { updates } = useWebSocket();

  // Force re-render when updates change
  useEffect(() => {
    if (updates && Object.keys(updates).length > 0) {
      console.log('🔄 Updates received, forcing re-render. Update keys:', Object.keys(updates));
      forceUpdate(prev => prev + 1);
    }
  }, [updates]);

  const handleAddVideos = async (urls) => {
    try {
      setIsAddingVideos(true);
      await addVideos(urls);
    } catch (err) {
      console.error('Error adding videos:', err);
      alert('Error adding videos. Please check the URLs and try again.');
    } finally {
      setIsAddingVideos(false);
    }
  };

  const handleDeleteVideo = async (id) => {
    if (window.confirm('Are you sure you want to delete this video?')) {
      try {
        await deleteVideo(id);
      } catch (err) {
        console.error('Error deleting video:', err);
        alert('Error deleting video. Please try again.');
      }
    }
  };

  // Helper to get video with latest updates
  const getVideoWithUpdates = (video) => {
    const update = updates[video.id];
    if (update) {
      console.log(`📝 Merging update into video ${video.id}:`, update);
      return { ...video, ...update };
    }
    return video;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <svg className="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            TubeScribe
          </h1>
          <p className="text-gray-600 mt-2">YouTube Video Transcription & Summarization Tool</p>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <VideoForm onSubmit={handleAddVideos} loading={isAddingVideos} />

        {categories && categories.length > 0 && (
          <CategoryFilter
            categories={categories}
            selectedCategory={selectedCategory}
            onSelect={setSelectedCategory}
          />
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6">
            {error}
          </div>
        )}

        {loading && !fetchedVideos?.length ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading videos...</p>
          </div>
        ) : !fetchedVideos?.length ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No videos yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Add some YouTube URLs above to get started
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {fetchedVideos.map((video) => {
              const updatedVideo = getVideoWithUpdates(video);
              const shouldShowProgress = 
                updatedVideo.status === 'processing' || 
                updatedVideo.status === 'queued';
              
              return (
                <VideoCard
                  key={video.id}
                  video={updatedVideo}
                  showProgress={shouldShowProgress}
                  onDelete={handleDeleteVideo}
                />
              );
            })}
          </div>
        )}
      </main>
      
      <footer className="bg-white border-t mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-600 text-sm">
            Powered by OpenAI Whisper, LangChain, and Ollama
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;