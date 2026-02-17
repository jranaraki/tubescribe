import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const videosApi = {
  getAll: (categoryId = null) => {
    const params = categoryId ? { category_id: categoryId } : {};
    return api.get('/videos', { params });
  },
  
  getById: (id) => api.get(`/videos/${id}`),
  
  add: (urls) => api.post('/videos', { urls }),
  
  delete: (id) => api.delete(`/videos/${id}`),
};

export const categoriesApi = {
  getAll: () => api.get('/categories'),
  
  create: (name, description = '', color = '#3B82F6') => 
    api.post('/categories', { name, description, color }),
};

export const statsApi = {
  get: () => api.get('/stats'),
};

export default api;