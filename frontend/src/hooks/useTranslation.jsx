/**
 * Translation Hook for Aetherium
 * The Scribe's Linguistic Interface
 */

import React, { createContext, useContext, useState, useEffect } from 'react'
import { 
  getTranslation, 
  getCategoryTranslations, 
  SUPPORTED_LANGUAGES, 
  DEFAULT_LANGUAGE, 
  getBrowserLanguage,
  formatTimeWithTranslation,
  formatRelativeTime
} from '../utils/translations'

// Translation Context
const TranslationContext = createContext()

// Translation Provider Component
export const TranslationProvider = ({ children }) => {
  // Get initial language from localStorage or browser preference
  const getInitialLanguage = () => {
    const savedLanguage = localStorage.getItem('aetherium_language')
    if (savedLanguage && Object.keys(SUPPORTED_LANGUAGES).includes(savedLanguage)) {
      return savedLanguage
    }
    return getBrowserLanguage()
  }

  const [currentLanguage, setCurrentLanguage] = useState(getInitialLanguage)

  // Save language preference to localStorage
  useEffect(() => {
    localStorage.setItem('aetherium_language', currentLanguage)
  }, [currentLanguage])

  // Change language function
  const changeLanguage = (newLanguage) => {
    if (Object.keys(SUPPORTED_LANGUAGES).includes(newLanguage)) {
      setCurrentLanguage(newLanguage)
    } else {
      console.warn(`Unsupported language: ${newLanguage}`)
    }
  }

  // Translation function with current language
  const t = (category, key, fallbackLanguage = null) => {
    return getTranslation(category, key, fallbackLanguage || currentLanguage)
  }

  // Get all translations for a category
  const getCategory = (category) => {
    return getCategoryTranslations(category, currentLanguage)
  }

  // Format time with current language
  const formatTime = (seconds) => {
    return formatTimeWithTranslation(seconds, currentLanguage)
  }

  // Format relative time with current language
  const formatRelative = (date) => {
    return formatRelativeTime(date, currentLanguage)
  }

  // Get language display name
  const getLanguageName = (langCode = currentLanguage) => {
    return SUPPORTED_LANGUAGES[langCode] || langCode
  }

  // Check if current language is RTL (none of our supported languages are RTL, but good to have)
  const isRTL = () => {
    const rtlLanguages = ['ar', 'he', 'fa', 'ur']
    return rtlLanguages.includes(currentLanguage)
  }

  const value = {
    currentLanguage,
    changeLanguage,
    t,
    getCategory,
    formatTime,
    formatRelative,
    getLanguageName,
    isRTL,
    supportedLanguages: SUPPORTED_LANGUAGES
  }

  return (
    <TranslationContext.Provider value={value}>
      {children}
    </TranslationContext.Provider>
  )
}

// Hook to use translation context
export const useTranslation = () => {
  const context = useContext(TranslationContext)
  if (!context) {
    throw new Error('useTranslation must be used within a TranslationProvider')
  }
  return context
}

// Higher-order component for class components (if needed)
export const withTranslation = (WrappedComponent) => {
  return function TranslatedComponent(props) {
    const translation = useTranslation()
    return <WrappedComponent {...props} translation={translation} />
  }
}

// Language selector component
export const LanguageSelector = ({ className = '' }) => {
  const { currentLanguage, changeLanguage, supportedLanguages, getLanguageName } = useTranslation()

  return (
    <select
      value={currentLanguage}
      onChange={(e) => changeLanguage(e.target.value)}
      className={`language-selector ${className}`}
      title="Select Language / Tilni tanlang / Выберите язык"
    >
      {Object.entries(supportedLanguages).map(([code, name]) => (
        <option key={code} value={code}>
          {name}
        </option>
      ))}
    </select>
  )
}

export default useTranslation