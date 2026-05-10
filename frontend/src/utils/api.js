import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Attach JWT to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handle 401 - auto-logout (but NOT 403 forbidden - that's a role error, not auth error)
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      // Only logout if it's a real auth failure, not just a role check
      const detail = err.response?.data?.detail || ''
      if (
        detail.includes('Invalid') ||
        detail.includes('expired') ||
        detail.includes('not found')
      ) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

// ─── Auth ─────────────────────────────────────────────────
export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
}

// ─── Photos ───────────────────────────────────────────────
export const photosApi = {
  list: (params) => api.get('/photos', { params }),
  get: (id) => api.get(`/photos/${id}`),
  upload: (formData) =>
    api.post('/photos/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  update: (id, data) => api.put(`/photos/${id}`, data),
  delete: (id) => api.delete(`/photos/${id}`),
  myPhotos: (params) => api.get('/photos/my', { params }),
}

// ─── Comments ─────────────────────────────────────────────
export const commentsApi = {
  list: (photoId) => api.get(`/comments/${photoId}`),
  add: (photoId, data) => api.post(`/comments/${photoId}`, data),
  delete: (commentId) => api.delete(`/comments/${commentId}`),
}

// ─── Ratings ──────────────────────────────────────────────
export const ratingsApi = {
  rate: (photoId, score) => api.post(`/ratings/${photoId}`, { score }),
  remove: (photoId) => api.delete(`/ratings/${photoId}`),
}

// ─── Search ───────────────────────────────────────────────
export const searchApi = {
  search: (params) => api.get('/search', { params }),
}

// ─── Admin ────────────────────────────────────────────────
export const adminApi = {
  seed: () => api.post('/admin/seed'),
  createCreator: (data) => api.post('/admin/creators', data),
  listUsers: () => api.get('/admin/users'),
  stats: () => api.get('/admin/stats'),
}

export default api
