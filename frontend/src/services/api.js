import axios from 'axios'
import { APP_CONFIG, LOCAL_STORAGE_KEYS } from '../utils/constants'
import { handleError, retryWithBackoff } from '../utils/errorHandler'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: APP_CONFIG.apiBaseUrl,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
})

// Request interceptor to add auth token and request ID
api.interceptors.request.use(
  (config) => {
    // Add auth token
    const token = localStorage.getItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Add request ID for tracking
    config.headers['X-Request-ID'] = generateRequestId()
    
    // Add timestamp
    config.headers['X-Request-Time'] = new Date().toISOString()
    
    // Log request in development
    if (APP_CONFIG.environment === 'development') {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        headers: config.headers,
        data: config.data,
        params: config.params
      })
    }
    
    return config
  },
  (error) => {
    console.error('Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors and logging
api.interceptors.response.use(
  (response) => {
    // Log response in development
    if (APP_CONFIG.environment === 'development') {
      console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data,
        headers: response.headers
      })
    }
    
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // Log error in development
    if (APP_CONFIG.environment === 'development') {
      console.error(`❌ API Error: ${originalRequest?.method?.toUpperCase()} ${originalRequest?.url}`, {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      })
    }
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      // Try to refresh token
      const refreshToken = localStorage.getItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN)
      if (refreshToken) {
        try {
          const response = await axios.post(`${APP_CONFIG.apiBaseUrl}/api/auth/refresh`, {
            refresh_token: refreshToken
          })
          
          const { access_token, refresh_token: newRefreshToken } = response.data
          
          // Update tokens
          localStorage.setItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN, access_token)
          if (newRefreshToken) {
            localStorage.setItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN, newRefreshToken)
          }
          
          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch (refreshError) {
          // Refresh failed, clear tokens and redirect to login
          clearAuthData()
          redirectToLogin()
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token, clear auth data and redirect
        clearAuthData()
        redirectToLogin()
      }
    }
    
    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      handleError(error, {
        fallbackMessage: 'Access denied. You do not have permission to perform this action.'
      })
    }
    
    // Handle network errors with retry
    if (error.code === 'NETWORK_ERROR' || error.code === 'ECONNABORTED') {
      if (!originalRequest._retryCount) {
        originalRequest._retryCount = 0
      }
      
      if (originalRequest._retryCount < 3) {
        originalRequest._retryCount++
        console.log(`Retrying request (attempt ${originalRequest._retryCount})...`)
        
        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, 1000 * originalRequest._retryCount))
        return api(originalRequest)
      }
    }
    
    return Promise.reject(error)
  }
)

// Helper functions
const generateRequestId = () => {
  return Math.random().toString(36).substr(2, 9)
}

const clearAuthData = () => {
  localStorage.removeItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN)
  localStorage.removeItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN)
  localStorage.removeItem('aetherium_user') // Legacy key
}

const redirectToLogin = () => {
  // Avoid redirect loops
  if (window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
}

// API wrapper with retry logic
const apiWithRetry = {
  get: (url, config = {}) => retryWithBackoff(() => api.get(url, config)),
  post: (url, data, config = {}) => retryWithBackoff(() => api.post(url, data, config)),
  put: (url, data, config = {}) => retryWithBackoff(() => api.put(url, data, config)),
  patch: (url, data, config = {}) => retryWithBackoff(() => api.patch(url, data, config)),
  delete: (url, config = {}) => retryWithBackoff(() => api.delete(url, config)),
}

// Auth API
export const authAPI = {
  register: (userData) => api.post('/api/auth/register', userData),
  verifySMS: (verificationData) => api.post('/api/auth/verify-sms', verificationData),
  login: (loginData) => api.post('/api/auth/login', loginData),
  requestLoginSMS: (loginData) => api.post('/api/auth/login-sms-request', loginData),
  verifyLoginSMS: (verificationData) => api.post('/api/auth/login-sms-verify', verificationData),
  resendSMS: (email) => api.post('/api/auth/resend-sms', { email }),
}

// Users API
export const usersAPI = {
  getProfile: () => api.get('/api/users/profile'),
  getCompanyNumber: () => api.get('/api/users/company-number'),
}

// Subscriptions API
export const subscriptionsAPI = {
  getTiers: () => api.get('/api/subscriptions/tiers'),
  initiatePayment: (tierData) => api.post('/api/subscriptions/initiate-payment', tierData),
  startPaymentMonitoring: (paymentData) => api.post('/api/subscriptions/start-payment-monitoring', paymentData),
  getPaymentMonitoringStatus: () => api.get('/api/subscriptions/payment-monitoring-status'),
}

// Workflows API
export const workflowsAPI = {
  getWorkflows: () => api.get('/api/workflows/'),
  getWorkflow: (id) => api.get(`/api/workflows/${id}`),
  createWorkflow: (workflowData) => api.post('/api/workflows/', workflowData),
  updateWorkflow: (id, workflowData) => api.put(`/api/workflows/${id}`, workflowData),
  deleteWorkflow: (id) => api.delete(`/api/workflows/${id}`),
  validateWorkflow: (id) => api.get(`/api/workflows/${id}/validate`),
}

// Sessions API
export const sessionsAPI = {
  getSessions: (params = {}) => api.get('/api/sessions/', { params }),
  getSession: (id) => api.get(`/api/sessions/${id}`),
  getActiveCount: () => api.get('/api/sessions/active/count'),
  getRecentSummary: (hours = 24) => api.get(`/api/sessions/recent/summary?hours=${hours}`),
}

// Statistics API
export const statisticsAPI = {
  getDashboard: () => api.get('/api/statistics/dashboard'),
  getDaily: (days = 30) => api.get(`/api/statistics/daily?days=${days}`),
  getTrends: (days = 7) => api.get(`/api/statistics/trends?days=${days}`),
  getHourlyDistribution: (days = 7) => api.get(`/api/statistics/hourly-distribution?days=${days}`),
  getOutcomeAnalysis: (days = 30) => api.get(`/api/statistics/outcome-analysis?days=${days}`),
}

// Payments API
export const paymentsAPI = {
  initiateConsultationPayment: (data) =>
    api.post('/api/payment-sessions/initiate', data),
  
  getPaymentStatus: (paymentId) =>
    api.get(`/api/payment-sessions/${paymentId}/status`),
  
  confirmSMSPayment: (data) =>
    api.post('/api/payment-sessions/confirm-sms', data),
  
  cancelPayment: (paymentId) =>
    api.post(`/api/payment-sessions/${paymentId}/cancel`),
  
  getBankInfo: () =>
    api.get('/api/payment-sessions/bank-info'),
  
  getPaymentSessions: () =>
    api.get('/api/payment-sessions/'),
  
  // Legacy transactions (for history)
  getTransactions: (params = {}) => 
    api.get('/api/payment-sessions/', { params })
}

// Telegram API
export const telegramAPI = {
  getChats: () => api.get('/api/telegram/chats'),
  linkChat: (chatData) => api.post('/api/telegram/link-chat', chatData),
  unlinkChat: (chatId) => api.delete(`/api/telegram/chats/${chatId}`),
  getBotInfo: () => api.get('/api/telegram/bot-info'),
}

// GSM Modules API
export const gsmModulesAPI = {
  getModules: () => api.get('/api/gsm-modules/'),
  createModule: (moduleData) => api.post('/api/gsm-modules/', moduleData),
  updateModule: (moduleId, moduleData) => api.put(`/api/gsm-modules/${moduleId}`, moduleData),
  deleteModule: (moduleId) => api.delete(`/api/gsm-modules/${moduleId}`),
  getDemoCodes: () => api.get('/api/gsm-modules/demo-codes'),
  regenerateDemoCode: (moduleId) => api.post(`/api/gsm-modules/${moduleId}/regenerate-demo-code`),
}

export default api