import React, { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'
import { LOCAL_STORAGE_KEYS } from '../utils/constants'
import toast from 'react-hot-toast'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isFirstLogin, setIsFirstLogin] = useState(false)

  useEffect(() => {
    // Check for stored auth data on mount
    const storedToken = localStorage.getItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN)
    const storedUser = localStorage.getItem('aetherium_user')
    
    if (storedToken && storedUser) {
      try {
        setToken(storedToken)
        setUser(JSON.parse(storedUser))
      } catch (error) {
        console.error('Error parsing stored user data:', error)
        logout()
      }
    }
    
    setLoading(false)
  }, [])

  const login = async (loginData) => {
    try {
      // First try regular login to check if SMS verification is required
      const response = await authAPI.login(loginData)
      const { access_token, user_id, email, company_number, is_first_login, requires_sms } = response.data
      
      if (requires_sms) {
        // SMS verification required, return flag to trigger SMS flow
        return { success: true, requires_sms: true }
      }
      
      const userData = {
        id: user_id,
        email,
        company_number,
      }
      
      setToken(access_token)
      setUser(userData)
      setIsFirstLogin(is_first_login)
      
      localStorage.setItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN, access_token)
      localStorage.setItem('aetherium_user', JSON.stringify(userData))
      
      toast.success('Welcome to Aetherium, The Scribe awaits your command')
      
      return { success: true, isFirstLogin: is_first_login }
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed'
      
      // Check if error indicates SMS verification is required
      if (message.includes('SMS verification required') || message.includes('requires_sms')) {
        return { success: true, requires_sms: true }
      }
      
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData)
      toast.success('Registration successful! Please check your phone for the verification code.')
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.detail || 'Registration failed'
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const verifySMS = async (verificationData) => {
    try {
      const response = await authAPI.verifySMS(verificationData)
      const { access_token, user_id, email, company_number, is_first_login } = response.data
      
      const userData = {
        id: user_id,
        email,
        company_number,
      }
      
      setToken(access_token)
      setUser(userData)
      setIsFirstLogin(is_first_login)
      
      localStorage.setItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN, access_token)
      localStorage.setItem('aetherium_user', JSON.stringify(userData))
      
      toast.success('Phone verified! Welcome to Aetherium')
      
      return { success: true, isFirstLogin: is_first_login }
    } catch (error) {
      const message = error.response?.data?.detail || 'Verification failed'
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const resendSMS = async (email) => {
    try {
      await authAPI.resendSMS(email)
      toast.success('Verification code resent')
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to resend code'
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    setIsFirstLogin(false)
    localStorage.removeItem(LOCAL_STORAGE_KEYS.AUTH_TOKEN)
    localStorage.removeItem('aetherium_user')
    toast.success('The Scribe bids you farewell')
  }

  const clearFirstLoginFlag = () => {
    setIsFirstLogin(false)
  }

  const value = {
    user,
    token,
    loading,
    isFirstLogin,
    login,
    register,
    verifySMS,
    resendSMS,
    logout,
    clearFirstLoginFlag,
    isAuthenticated: !!token,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}