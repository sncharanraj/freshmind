// src/api/client.js — all API calls to Flask
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// Auto-attach JWT token
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('fm_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// Auto-logout on 401
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('fm_token')
      localStorage.removeItem('fm_user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── AUTH ──
export const authAPI = {
  login:    (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  me:       ()     => api.get('/auth/me'),
}

// ── PANTRY ──
export const pantryAPI = {
  getAll:     ()              => api.get('/pantry/items'),
  getExpiring:(days)          => api.get(`/pantry/expiring/${days}`),
  add:        (data)          => api.post('/pantry/items', data),
  update:     (id, data)      => api.put(`/pantry/items/${id}`, data),
  delete:     (id, wasted=true) => api.delete(`/pantry/items/${id}`, { data:{ wasted } }),
  markUsed:   (id)            => api.post(`/pantry/items/${id}/use`),
  getHistory: ()              => api.get('/pantry/history'),
}

// ── AI ──
export const aiAPI = {
  getRecipes: (prefs)            => api.post('/ai/recipes', { preferences: prefs }),
  chat:       (message, history) => api.post('/ai/chat', { message, history }),
}

// ── IMAGE ──
export const imageAPI = {
  fetch: (name) => api.get(`/image/fetch?name=${encodeURIComponent(name)}`),
}

// ── WEATHER ──
export const weatherAPI = {
  get: () => api.get('/weather'),
}

// ── USER ──
export const usersAPI = {
  changePassword: (data) => api.put('/users/password', data),
  myLoginHistory: ()     => api.get('/me/login-history'),
}

// ── ADMIN (admin role only) ──
export const adminAPI = {
  getUsers:        ()          => api.get('/admin/users'),
  getLoginHistory: (limit=100) => api.get(`/admin/login-history?limit=${limit}`),
  getLoginStats:   ()          => api.get('/admin/login-stats'),
}

export default api