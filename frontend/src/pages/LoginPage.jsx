import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useAuth } from '../hooks/useAuth'
import { useTranslation, LanguageSelector } from '../hooks/useTranslation'
import { Eye, EyeOff, LogIn, Globe } from 'lucide-react'

const LoginPage = () => {
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const { login, isAuthenticated, isFirstLogin } = useAuth()
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm()

  useEffect(() => {
    if (isAuthenticated) {
      const from = location.state?.from?.pathname || '/dashboard'
      if (isFirstLogin) {
        navigate('/company-number')
      } else {
        navigate(from)
      }
    }
  }, [isAuthenticated, isFirstLogin, navigate, location])

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      const result = await login(data)
      if (result.success) {
        if (result.isFirstLogin) {
          navigate('/company-number')
        } else {
          const from = location.state?.from?.pathname || '/dashboard'
          navigate(from)
        }
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-coffee-beige px-4">
      <div className="w-full max-w-md">
        {/* Language Selector */}
        <div className="flex justify-end mb-4">
          <div className="flex items-center space-x-2">
            <Globe size={16} className="text-coffee-sienna" />
            <LanguageSelector className="input-paper text-sm py-1 px-2" />
          </div>
        </div>

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="heading-decorative text-4xl mb-2">{t('common', 'aetherium')}</h1>
          <p className="text-coffee-sienna text-lg">{t('auth', 'loginTitle')}</p>
          <p className="text-coffee-brown mt-2">{t('auth', 'loginSubtitle')}</p>
        </div>

        {/* Login Form */}
        <div className="paper-panel">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Login Identifier */}
            <div>
              <label className="block text-coffee-brown font-medium mb-2">
                {t('auth', 'emailOrPhone')}
              </label>
              <input
                type="text"
                className="input-paper w-full"
                placeholder={t('auth', 'emailOrPhonePlaceholder')}
                {...register('login_identifier', {
                  required: t('auth', 'loginIdentifierRequired'),
                })}
              />
              {errors.login_identifier && (
                <p className="text-red-600 text-sm mt-1">{errors.login_identifier.message}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="block text-coffee-brown font-medium mb-2">
                {t('auth', 'password')}
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="input-paper w-full pr-12"
                  placeholder={t('auth', 'passwordPlaceholder')}
                  {...register('password', {
                    required: t('auth', 'passwordRequired'),
                  })}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-coffee-sienna hover:text-coffee-brown"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {errors.password && (
                <p className="text-red-600 text-sm mt-1">{errors.password.message}</p>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              {loading ? (
                <div className="loading-quill w-5 h-5"></div>
              ) : (
                <>
                  <LogIn size={20} />
                  <span>{t('auth', 'enterRealm')}</span>
                </>
              )}
            </button>
          </form>

          {/* Register Link */}
          <div className="mt-6 text-center">
            <p className="text-coffee-brown">
              {t('auth', 'newToAetherium')}{' '}
              <Link
                to="/register"
                className="text-coffee-sienna hover:text-coffee-brown font-medium underline"
              >
                {t('auth', 'beginJourney')}
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-coffee-sienna text-sm">
            "{t('auth', 'loginFooter')}"
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage