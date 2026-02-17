import { useState, useEffect, useCallback } from 'react';
import { io } from 'socket.io-client';
import { videosApi, categoriesApi } from '../services/api';

export function useVideos(categoryId = null) {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchVideos = useCallback(async () => {
    try {
      setLoading(true);
      const response = await videosApi.getAll(categoryId);
      setVideos(response.data);
      console.log(`📦 Fetched ${response.data.length} videos from server`);
      setError(null);
    } catch (err) {
      console.error('Error fetching videos:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [categoryId]);

  const addVideos = async (urls) => {
    try {
      console.log(`🎬 Adding ${urls.length} video URLs`);
      const response = await videosApi.add(urls);
      await fetchVideos();
      console.log(`✅ Videos added successfully:`, response.data.videos.map(v => v.id));
      return response.data.videos;
    } catch (err) {
      console.error('Error adding videos:', err);
      throw err;
    }
  };

  const deleteVideo = async (id) => {
    try {
      await videosApi.delete(id);
      setVideos(prev => prev.filter(v => v.id !== id));
      console.log(`🗑️ Video ${id} deleted`);
    } catch (err) {
      console.error('Error deleting video:', err);
      throw err;
    }
  };

  useEffect(() => {
    fetchVideos();
  }, [fetchVideos]);

  return { videos, loading, error, addVideos, deleteVideo, refetch: fetchVideos };
}

export function useCategories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const response = await categoriesApi.getAll();
      setCategories(response.data);
    } catch (err) {
      console.error('Error fetching categories:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  return { categories, loading, refetch: fetchCategories };
}

export function useWebSocket() {
  const [updates, setUpdates] = useState({});
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const SOCKET_URL = 'http://localhost:5000';
    console.log('Initializing WebSocket connection to:', SOCKET_URL);
    
    const newSocket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    });

    newSocket.on('connect', () => {
      console.log('✅ WebSocket connected successfully');
      setIsConnected(true);
    });

    newSocket.on('video_progress', (data) => {
      console.log('📊 Video progress update received:', data);
      if (data && data.video_id) {
        setUpdates((prev) => ({
          ...prev,
          [data.video_id]: data,
        }));
      } else {
        console.warn('Invalid video_progress data:', data);
      }
    });

    newSocket.on('all_updates', (data) => {
      console.log('📢 All updates received:', data);
      if (data && data.video_id) {
        const updateData = data.data || data;
        setUpdates((prev) => ({
          ...prev,
          [data.video_id]: updateData,
        }));
      } else {
        console.warn('Invalid all_updates data:', data);
      }
    });

    newSocket.on('connect_error', (error) => {
      console.error('❌ WebSocket connection error:', error);
      setIsConnected(false);
    });

    newSocket.on('disconnect', () => {
      console.log('🔌 WebSocket disconnected');
      setIsConnected(false);
    });

    setSocket(newSocket);

    return () => {
      console.log('Cleaning up WebSocket connection');
      newSocket.disconnect();
      newSocket.off('connect');
      newSocket.off('video_progress');
      newSocket.off('all_updates');
      newSocket.off('connect_error');
      newSocket.off('disconnect');
    };
  }, []);

  return { updates, socket, isConnected };
}