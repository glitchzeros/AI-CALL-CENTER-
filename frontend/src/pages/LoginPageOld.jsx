import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useAuth } from '../hooks/useAuth'
import { useTranslation, LanguageSelector } from '../hooks/useTranslation'
import { Eye, EyeOff, LogIn, Globe, MessageSquare, Clock, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

const LoginPage = () => {
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [smsStep, setSmsStep] = useState(false)
  const [smsLoading, setSmsLoading] = useState(false)
  const [demoCode, setDemoCode] = useState(null)
  const [timeRemaining, setTimeRemaining] = useState(0)
  const [loginData, setLoginData] = useState(null)
  
  const { login, isAuthenticated, isFirstLogin } = useAuth()
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm()

  const {
    register: registerSMS,
    handleSubmit: handleSubmitSMS,
    formState: { errors: smsErrors },
    reset: resetSMS
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

  // Timer for SMS verification
  useEffect(() => {
    if (timeRemaining > 0) {
      const timer = setTimeout(() => {
        setTimeRemaining(timeRemaining - 1)
      }, 1000)
      return () => clearTimeout(timer)
    }
  }, [timeRemaining])

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      const result = await login(data)
      
      if (result.success) {
        if (result.requires_sms) {
          // SMS verification required
          setLoginData(data)
          setSmsStep(true)
          await requestSmsCode(data)
        } else {
          // Direct login successful
          if (result.isFirstLogin) {
            navigate('/company-number')
          } else {
            const from = location.state?.from?.pathname || '/dashboard'
            navigate(from)
          }
        }
      }
    } catch (error) {
      toast.error(error.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const requestSmsCode = async (data) => {
    setSmsLoading(true)
    try {
      const response = await fetch('/api/auth/login-sms-request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      const result = await response.json()

      if (response.ok) {
        setTimeRemaining(600) // 10 minutes
        
        if (result.demo_code) {
          setDemoCode(result.demo_code)
          toast.success(`Demo SMS code: ${result.demo_code}`, {
            duration: 10000,
            icon: '📱'
          })
        } else {
          toast.success('SMS verification code sent to your phone')
        }
      } else {
        throw new Error(result.detail || 'Failed to send SMS')
      }
    } catch (error) {
      toast.error(error.message || 'Failed to send SMS verification code')
      setSmsStep(false)
    } finally {
      setSmsLoading(false)
    }
  }

  const onSmsSubmit = async (data) => {
    setSmsLoading(true)
    try {
      const response = await fetch('/api/auth/login-sms-verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          login_identifier: loginData.login_identifier,
          verification_code: data.verification_code
        }),
      })

      const result = await response.json()

      if (response.ok) {
        // Store token and redirect
        localStorage.setItem('token', result.access_token)
        toast.success('Login successful!')
        
        if (result.is_first_login) {
          navigate('/company-number')
        } else {
          const from = location.state?.from?.pathname || '/dashboard'
          navigate(from)
        }
      } else {
        throw new Error(result.detail || 'Invalid verification code')
      }
    } catch (error) {
      toast.error(error.message || 'SMS verification failed')
    } finally {
      setSmsLoading(false)
    }
  }

  const getDemoCode = async () => {
    try {
      const response = await fetch('/api/gsm-modules/demo-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          login_identifier: loginData.login_identifier
        }),
      })

      const result = await response.json()

      if (response.ok) {
        setDemoCode(result.demo_code)
        toast.success(`Demo code: ${result.demo_code}`, {
          duration: 10000,
          icon: '📱'
        })
      } else {
        toast.error('No demo code available')
      }
    } catch (error) {
      toast.error('Failed to get demo code')
    }
  }

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const resendSms = async () => {
    await requestSmsCode(loginData)
  }

  const goBack = () => {
    setSmsStep(false)
    setDemoCode(null)
    setTimeRemaining(0)
    resetSms()
  }

  if (smsStep) {
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
            <p className="text-coffee-sienna text-lg">SMS Verification</p>
            <p className="text-coffee-brown mt-2">Enter the verification code sent to your phone</p>
          </div>

          {/* SMS Verification Form */}
          <div className="paper-panel">
            <form onSubmit={handleSubmitSms(onSmsSubmit)} className="space-y-6">
              {/* Verification Code */}
              <div>
                <label className="block text-coffee-brown font-medium mb-2">
                  Verification Code
                </label>
                <input
                  type="text"
                  className="input-paper w-full text-center text-2xl tracking-widest"
                  placeholder="000000"
                  maxLength="6"
                  {...registerSms('verification_code', {
                    required: 'Verification code is required',
                    pattern: {
                      value: /^\d{6}$/,
                      message: 'Please enter a 6-digit code'
                    }
                  })}
                />
                {smsErrors.verification_code && (
                  <p className="text-red-600 text-sm mt-1">{smsErrors.verification_code.message}</p>
                )}
              </div>

              {/* Timer */}
              {timeRemaining > 0 && (
                <div className="flex items-center justify-center space-x-2 text-coffee-sienna">
                  <Clock size={16} />
                  <span>Code expires in {formatTime(timeRemaining)}</span>
                </div>
              )}

              {/* Demo Code Display */}
              {demoCode && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 text-yellow-800">
                    <AlertCircle size={16} />
                    <span className="font-medium">Demo Mode</span>
                  </div>
                  <p className="text-yellow-700 mt-1">
                    No real GSM modules available. Use demo code: <strong>{demoCode}</strong>
                  </p>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={smsLoading}
                className="btn-primary w-full flex items-center justify-center space-x-2"
              >
                {smsLoading ? (
                  <div className="loading-quill w-5 h-5"></div>
                ) : (
                  <>
                    <MessageSquare size={20} />
                    <span>Verify Code</span>
                  </>
                )}
              </button>
            </form>

            {/* Actions */}
            <div className="mt-6 space-y-3">
              {/* Resend SMS */}
              <button
                onClick={resendSms}
                disabled={smsLoading || timeRemaining > 540} // Allow resend after 1 minute
                className="btn-secondary w-full"
              >
                Resend SMS Code
              </button>

              {/* Get Demo Code */}
              <button
                onClick={getDemoCode}
                className="btn-secondary w-full"
              >
                Get Demo Code
              </button>

              {/* Back to Login */}
              <button
                onClick={goBack}
                className="text-coffee-sienna hover:text-coffee-brown font-medium underline w-full text-center"
              >
                Back to Login
              </button>
            </div>
          </div>
        </div>
      </div>
    )
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