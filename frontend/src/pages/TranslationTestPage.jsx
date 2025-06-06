/**
 * Translation Test Page
 * For testing the manual translation system
 */

import React from 'react'
import { useTranslation, LanguageSelector } from '../hooks/useTranslation'
import { Globe, Check, X } from 'lucide-react'

const TranslationTestPage = () => {
  const { t, currentLanguage, getCategory, formatTime, formatRelative } = useTranslation()

  const testCategories = ['common', 'auth', 'dashboard', 'subscription', 'navigation', 'companyNumber']
  const testDate = new Date(Date.now() - 3600000) // 1 hour ago

  return (
    <div className="min-h-screen bg-coffee-beige p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="heading-decorative text-4xl mb-4">Translation System Test</h1>
          <p className="text-coffee-sienna text-lg">Manual Translation Verification</p>
          
          {/* Language Selector */}
          <div className="flex justify-center items-center space-x-4 mt-6">
            <Globe size={20} className="text-coffee-sienna" />
            <LanguageSelector className="language-selector" />
            <span className="text-coffee-brown">Current: {currentLanguage}</span>
          </div>
        </div>

        {/* Translation Categories Test */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {testCategories.map(category => {
            const categoryTranslations = getCategory(category)
            const hasTranslations = Object.keys(categoryTranslations).length > 0
            
            return (
              <div key={category} className="paper-panel">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="heading-secondary text-lg">{category}</h3>
                  {hasTranslations ? (
                    <Check size={20} className="text-green-600" />
                  ) : (
                    <X size={20} className="text-red-600" />
                  )}
                </div>
                
                <div className="space-y-2 text-sm">
                  {Object.entries(categoryTranslations).slice(0, 5).map(([key, value]) => (
                    <div key={key} className="border-b border-coffee-tan pb-1">
                      <span className="font-mono text-coffee-sienna">{key}:</span>
                      <br />
                      <span className="text-coffee-brown">{value}</span>
                    </div>
                  ))}
                  {Object.keys(categoryTranslations).length > 5 && (
                    <p className="text-coffee-sienna italic">
                      ...and {Object.keys(categoryTranslations).length - 5} more
                    </p>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* Sample Translations Test */}
        <div className="paper-panel mb-8">
          <h3 className="heading-secondary mb-4">Sample Translations</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold text-coffee-brown mb-2">Authentication</h4>
              <ul className="space-y-1 text-sm">
                <li><strong>Login Title:</strong> {t('auth', 'loginTitle')}</li>
                <li><strong>Email Required:</strong> {t('auth', 'emailRequired')}</li>
                <li><strong>Create Account:</strong> {t('auth', 'createAccount')}</li>
                <li><strong>Verify Code:</strong> {t('auth', 'verifyCode')}</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-coffee-brown mb-2">Navigation</h4>
              <ul className="space-y-1 text-sm">
                <li><strong>Dashboard:</strong> {t('navigation', 'dashboard')}</li>
                <li><strong>Subscription:</strong> {t('navigation', 'subscription')}</li>
                <li><strong>Sessions:</strong> {t('navigation', 'sessions')}</li>
                <li><strong>Statistics:</strong> {t('navigation', 'statistics')}</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-coffee-brown mb-2">Common</h4>
              <ul className="space-y-1 text-sm">
                <li><strong>Aetherium:</strong> {t('common', 'aetherium')}</li>
                <li><strong>Scribe:</strong> {t('common', 'scribe')}</li>
                <li><strong>Loading:</strong> {t('common', 'loading')}</li>
                <li><strong>Save:</strong> {t('common', 'save')}</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-coffee-brown mb-2">Time Formatting</h4>
              <ul className="space-y-1 text-sm">
                <li><strong>3600 seconds:</strong> {formatTime(3600)}</li>
                <li><strong>120 seconds:</strong> {formatTime(120)}</li>
                <li><strong>1 hour ago:</strong> {formatRelative(testDate)}</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Language Coverage Test */}
        <div className="paper-panel">
          <h3 className="heading-secondary mb-4">Language Coverage</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {['en', 'uz', 'ru'].map(lang => (
              <div key={lang} className="border border-coffee-tan rounded p-4">
                <h4 className="font-semibold text-coffee-brown mb-2">
                  {lang.toUpperCase()} - {lang === 'en' ? 'English' : lang === 'uz' ? 'O\'zbekcha' : 'Русский'}
                </h4>
                <div className="space-y-1 text-sm">
                  <p><strong>Login:</strong> {t('auth', 'loginTitle', lang)}</p>
                  <p><strong>Dashboard:</strong> {t('navigation', 'dashboard', lang)}</p>
                  <p><strong>Save:</strong> {t('common', 'save', lang)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-coffee-sienna text-sm">
            Translation system test completed. Check console for any warnings.
          </p>
        </div>
      </div>
    </div>
  )
}

export default TranslationTestPage