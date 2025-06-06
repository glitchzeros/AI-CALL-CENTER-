import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('aetherium_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('aetherium_token')
      localStorage.removeItem('aetherium_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  verifySMS: (verificationData) => api.post('/auth/verify-sms', verificationData),
  login: (loginData) => api.post('/auth/login', loginData),
  resendSMS: (email) => api.post('/auth/resend-sms', { email }),
}

// Users API
export const usersAPI = {
  getProfile: () => api.get('/users/profile'),
  getCompanyNumber: () => api.get('/users/company-number'),
}

// Subscriptions API
export const subscriptionsAPI = {
  getTiers: () => api.get('/subscriptions/tiers'),
  initiatePayment: (tierData) => api.post('/subscriptions/initiate-payment', tierData),
}

// Workflows API
export const workflowsAPI = {
  getWorkflows: () => api.get('/workflows/'),
  getWorkflow: (id) => api.get(`/workflows/${id}`),
  createWorkflow: (workflowData) => api.post('/workflows/', workflowData),
  updateWorkflow: (id, workflowData) => api.put(`/workflows/${id}`, workflowData),
  deleteWorkflow: (id) => api.delete(`/workflows/${id}`),
  validateWorkflow: (id) => api.get(`/workflows/${id}/validate`),
}

// Sessions API
export const sessionsAPI = {
  getSessions: (params = {}) => api.get('/sessions/', { params }),
  getSession: (id) => api.get(`/sessions/${id}`),
  getActiveCount: () => api.get('/sessions/active/count'),
  getRecentSummary: (hours = 24) => api.get(`/sessions/recent/summary?hours=${hours}`),
}

// Statistics API
export const statisticsAPI = {
  getDashboard: () => api.get('/statistics/dashboard'),
  getDaily: (days = 30) => api.get(`/statistics/daily?days=${days}`),
  getTrends: (days = 7) => api.get(`/statistics/trends?days=${days}`),
  getHourlyDistribution: (days = 7) => api.get(`/statistics/hourly-distribution?days=${days}`),
  getOutcomeAnalysis: (days = 30) => api.get(`/statistics/outcome-analysis?days=${days}`),
}

// Payments API
export const paymentsAPI = {
  initiateConsultationPayment: (data) =>
    api.post('/payments/initiate-consultation', data),
  
  getPaymentStatus: (paymentId) =>
    api.get(`/payments/status/${paymentId}`),
  
  confirmSMSPayment: (data) =>
    api.post('/payments/confirm-sms', data),
  
  cancelPayment: (paymentId) =>
    api.post(`/payments/cancel/${paymentId}`),
  
  getBankInfo: () =>
    api.get('/payments/bank-info'),
  
  getPaymentSessions: () =>
    api.get('/payments/sessions'),
  
  // Legacy transactions (for history)
  getTransactions: (params = {}) => 
    api.get('/payments/sessions', { params })
}

// Telegram API
export const telegramAPI = {
  getChats: () => api.get('/telegram/chats'),
  linkChat: (chatData) => api.post('/telegram/link-chat', chatData),
  unlinkChat: (chatId) => api.delete(`/telegram/chats/${chatId}`),
  getBotInfo: () => api.get('/telegram/bot-info'),
}

export default api