// Error Handling Utilities

import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';

/**
 * Error types for better categorization
 */
export const ERROR_TYPES = {
  NETWORK: 'NETWORK_ERROR',
  VALIDATION: 'VALIDATION_ERROR',
  AUTHENTICATION: 'AUTHENTICATION_ERROR',
  AUTHORIZATION: 'AUTHORIZATION_ERROR',
  SERVER: 'SERVER_ERROR',
  CLIENT: 'CLIENT_ERROR',
  UNKNOWN: 'UNKNOWN_ERROR'
};

/**
 * Custom error class for application errors
 */
export class AppError extends Error {
  constructor(message, type = ERROR_TYPES.UNKNOWN, statusCode = null, details = null) {
    super(message);
    this.name = 'AppError';
    this.type = type;
    this.statusCode = statusCode;
    this.details = details;
    this.timestamp = new Date().toISOString();
  }
}

/**
 * Determines error type based on error object
 */
export const getErrorType = (error) => {
  if (!error) return ERROR_TYPES.UNKNOWN;
  
  // Network errors
  if (error.code === 'NETWORK_ERROR' || !navigator.onLine) {
    return ERROR_TYPES.NETWORK;
  }
  
  // HTTP status code based errors
  if (error.response?.status) {
    const status = error.response.status;
    
    if (status === 401) return ERROR_TYPES.AUTHENTICATION;
    if (status === 403) return ERROR_TYPES.AUTHORIZATION;
    if (status >= 400 && status < 500) return ERROR_TYPES.CLIENT;
    if (status >= 500) return ERROR_TYPES.SERVER;
  }
  
  // Validation errors
  if (error.type === 'validation' || error.name === 'ValidationError') {
    return ERROR_TYPES.VALIDATION;
  }
  
  return ERROR_TYPES.UNKNOWN;
};

/**
 * Extracts user-friendly error message
 */
export const getErrorMessage = (error) => {
  if (!error) return 'An unknown error occurred';
  
  // If it's already a string, return it
  if (typeof error === 'string') return error;
  
  // Check for custom error message
  if (error.message) return error.message;
  
  // Check for API error response
  if (error.response?.data?.message) return error.response.data.message;
  if (error.response?.data?.error) return error.response.data.error;
  
  // Check for network errors
  if (error.code === 'NETWORK_ERROR') {
    return 'Network connection failed. Please check your internet connection.';
  }
  
  // HTTP status based messages
  if (error.response?.status) {
    const status = error.response.status;
    
    switch (status) {
      case 400:
        return 'Invalid request. Please check your input.';
      case 401:
        return 'Authentication required. Please log in again.';
      case 403:
        return 'Access denied. You do not have permission to perform this action.';
      case 404:
        return 'The requested resource was not found.';
      case 409:
        return 'Conflict detected. The resource already exists or is in use.';
      case 422:
        return 'Validation failed. Please check your input.';
      case 429:
        return 'Too many requests. Please try again later.';
      case 500:
        return 'Internal server error. Please try again later.';
      case 502:
        return 'Bad gateway. The server is temporarily unavailable.';
      case 503:
        return 'Service unavailable. Please try again later.';
      case 504:
        return 'Gateway timeout. The request took too long to process.';
      default:
        return `Server error (${status}). Please try again later.`;
    }
  }
  
  return 'An unexpected error occurred. Please try again.';
};

/**
 * Handles errors with appropriate user feedback
 */
export const handleError = (error, options = {}) => {
  const {
    showToast = true,
    logError = true,
    fallbackMessage = null,
    onError = null
  } = options;
  
  const errorType = getErrorType(error);
  const errorMessage = fallbackMessage || getErrorMessage(error);
  
  // Log error for debugging
  if (logError) {
    console.error('Error occurred:', {
      type: errorType,
      message: errorMessage,
      error: error,
      timestamp: new Date().toISOString()
    });
  }
  
  // Show toast notification
  if (showToast) {
    const toastOptions = {
      duration: 5000,
      style: {
        background: '#F5F5DC',
        color: '#8B4513',
        border: '2px solid #CD853F',
        fontFamily: 'Vollkorn, serif',
      }
    };
    
    switch (errorType) {
      case ERROR_TYPES.NETWORK:
        toast.error('🌐 ' + errorMessage, toastOptions);
        break;
      case ERROR_TYPES.AUTHENTICATION:
        toast.error('🔐 ' + errorMessage, toastOptions);
        break;
      case ERROR_TYPES.AUTHORIZATION:
        toast.error('🚫 ' + errorMessage, toastOptions);
        break;
      case ERROR_TYPES.VALIDATION:
        toast.error('⚠️ ' + errorMessage, toastOptions);
        break;
      case ERROR_TYPES.SERVER:
        toast.error('🔧 ' + errorMessage, toastOptions);
        break;
      default:
        toast.error('❌ ' + errorMessage, toastOptions);
    }
  }
  
  // Call custom error handler if provided
  if (onError && typeof onError === 'function') {
    onError(error, errorType, errorMessage);
  }
  
  return {
    type: errorType,
    message: errorMessage,
    originalError: error
  };
};

/**
 * Async error boundary for handling promise rejections
 */
export const withErrorHandling = (asyncFunction, options = {}) => {
  return async (...args) => {
    try {
      return await asyncFunction(...args);
    } catch (error) {
      handleError(error, options);
      throw error; // Re-throw so calling code can handle it if needed
    }
  };
};

/**
 * Retry function with exponential backoff
 */
export const retryWithBackoff = async (
  asyncFunction,
  maxRetries = 3,
  baseDelay = 1000,
  maxDelay = 10000
) => {
  let lastError;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await asyncFunction();
    } catch (error) {
      lastError = error;
      
      // Don't retry on client errors (4xx) except 408, 429
      if (error.response?.status >= 400 && error.response?.status < 500) {
        const status = error.response.status;
        if (status !== 408 && status !== 429) {
          throw error;
        }
      }
      
      // Don't retry on the last attempt
      if (attempt === maxRetries) {
        break;
      }
      
      // Calculate delay with exponential backoff and jitter
      const delay = Math.min(
        baseDelay * Math.pow(2, attempt) + Math.random() * 1000,
        maxDelay
      );
      
      console.warn(`Attempt ${attempt + 1} failed, retrying in ${delay}ms...`, error);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError;
};

/**
 * Validates form data and returns formatted errors
 */
export const validateFormData = (data, validationRules) => {
  const errors = {};
  
  for (const [field, rules] of Object.entries(validationRules)) {
    const value = data[field];
    const fieldErrors = [];
    
    // Required validation
    if (rules.required && (!value || (typeof value === 'string' && value.trim() === ''))) {
      fieldErrors.push(`${rules.label || field} is required`);
      continue; // Skip other validations if required field is empty
    }
    
    // Skip other validations if field is empty and not required
    if (!value && !rules.required) continue;
    
    // Type validation
    if (rules.type && typeof value !== rules.type) {
      fieldErrors.push(`${rules.label || field} must be a ${rules.type}`);
    }
    
    // String validations
    if (typeof value === 'string') {
      if (rules.minLength && value.length < rules.minLength) {
        fieldErrors.push(`${rules.label || field} must be at least ${rules.minLength} characters`);
      }
      
      if (rules.maxLength && value.length > rules.maxLength) {
        fieldErrors.push(`${rules.label || field} must be no more than ${rules.maxLength} characters`);
      }
      
      if (rules.pattern && !rules.pattern.test(value)) {
        fieldErrors.push(rules.patternMessage || `${rules.label || field} format is invalid`);
      }
    }
    
    // Number validations
    if (typeof value === 'number') {
      if (rules.min !== undefined && value < rules.min) {
        fieldErrors.push(`${rules.label || field} must be at least ${rules.min}`);
      }
      
      if (rules.max !== undefined && value > rules.max) {
        fieldErrors.push(`${rules.label || field} must be no more than ${rules.max}`);
      }
    }
    
    // Custom validation
    if (rules.validate && typeof rules.validate === 'function') {
      const customError = rules.validate(value, data);
      if (customError) {
        fieldErrors.push(customError);
      }
    }
    
    if (fieldErrors.length > 0) {
      errors[field] = fieldErrors;
    }
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

/**
 * Global error handler for unhandled promise rejections
 */
export const setupGlobalErrorHandling = () => {
  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    
    handleError(event.reason, {
      showToast: true,
      logError: true,
      fallbackMessage: 'An unexpected error occurred'
    });
    
    // Prevent the default browser error handling
    event.preventDefault();
  });
  
  // Handle general JavaScript errors
  window.addEventListener('error', (event) => {
    console.error('JavaScript error:', event.error);
    
    handleError(event.error, {
      showToast: false, // Don't show toast for JS errors as they might be frequent
      logError: true
    });
  });
};

/**
 * Error boundary hook for React components
 */
export const useErrorBoundary = () => {
  const [error, setError] = useState(null);
  
  const resetError = () => setError(null);
  
  const captureError = (error) => {
    setError(error);
    handleError(error);
  };
  
  useEffect(() => {
    if (error) {
      // Log error to external service if needed
      console.error('Component error boundary triggered:', error);
    }
  }, [error]);
  
  return {
    error,
    resetError,
    captureError,
    hasError: !!error
  };
};