import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useAuth } from '../hooks/useAuth'
import { useTranslation, LanguageSelector } from '../hooks/useTranslation'
import { Eye, EyeOff, UserPlus, Phone, Mail, Lock, Globe } from 'lucide-react'

const RegisterPage = () => {
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState('register') // 'register' or 'verify'
  const [registrationEmail, setRegistrationEmail] = useState('')
  const [verificationCode, setVerificationCode] = useState('')
  const [resendLoading, setResendLoading] = useState(false)
  const [countdown, setCountdown] = useState(0)

  const { register: registerUser, verifySMS, resendSMS } = useAuth()
  const { t } = useTranslation()
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm()

  const password = watch('password')

  // Countdown timer for resend button
  React.useEffect(() => {
    let timer
    if (countdown > 0) {
      timer = setTimeout(() => setCountdown(countdown - 1), 1000)
    }
    return () => clearTimeout(timer)
  }, [countdown])

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      const result = await registerUser(data)
      if (result.success) {
        setRegistrationEmail(data.email)
        setStep('verify')
        setCountdown(60) // Start 1-minute countdown
      }
    } finally {
      setLoading(false)
    }
  }

  const handleVerification = async (e) => {
    e.preventDefault()
    if (!verificationCode || verificationCode.length !== 6) {
      return
    }

    setLoading(true)
    try {
      const result = await verifySMS({
        email: registrationEmail,
        verification_code: verificationCode,
      })
      if (result.success) {
        navigate('/company-number')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleResendCode = async () => {
    setResendLoading(true)
    try {
      const result = await resendSMS(registrationEmail)
      if (result.success) {
        setCountdown(60)
      }
    } finally {
      setResendLoading(false)
    }
  }

  if (step === 'verify') {
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

          <div className="text-center mb-8">
            <h1 className="heading-decorative text-4xl mb-2">{t('auth', 'verificationTitle')}</h1>
            <p className="text-coffee-brown">
              {t('auth', 'verificationDescription')}
            </p>
            <p className="text-coffee-sienna text-sm mt-2">{registrationEmail}</p>
          </div>

          <div className="paper-panel">
            <form onSubmit={handleVerification} className="space-y-6">
              <div>
                <label className="block text-coffee-brown font-medium mb-2">
                  {t('auth', 'verificationCode')}
                </label>
                <input
                  type="text"
                  maxLength="6"
                  className="input-paper w-full text-center text-2xl tracking-widest"
                  placeholder={t('auth', 'verificationCodePlaceholder')}
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
                />
                <p className="text-coffee-sienna text-sm mt-2">
                  {t('auth', 'verificationCodeHint')}
                </p>
              </div>

              <button
                type="submit"
                disabled={loading || verificationCode.length !== 6}
                className="btn-primary w-full"
              >
                {loading ? (
                  <div className="loading-quill w-5 h-5 mx-auto"></div>
                ) : (
                  t('auth', 'verifyCode')
                )}
              </button>
            </form>

            <div className="mt-6 text-center">
              <button
                onClick={handleResendCode}
                disabled={countdown > 0 || resendLoading}
                className="btn-secondary"
              >
                {resendLoading ? (
                  <div className="loading-quill w-4 h-4 mx-auto"></div>
                ) : countdown > 0 ? (
                  `${t('auth', 'resendIn')} ${countdown}s`
                ) : (
                  t('auth', 'resendCode')
                )}
              </button>
            </div>

            <div className="mt-4 text-center">
              <button
                onClick={() => setStep('register')}
                className="text-coffee-sienna hover:text-coffee-brown text-sm underline"
              >
                {t('auth', 'backToRegistration')}
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
          <h1 className="heading-decorative text-4xl mb-2">{t('auth', 'registerTitle')}</h1>
          <p className="text-coffee-sienna text-lg">{t('auth', 'registerSubtitle')}</p>
          <p className="text-coffee-brown mt-2">{t('auth', 'registerDescription')}</p>
        </div>

        {/* Registration Form */}
        <div className="paper-panel">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Email */}
            <div>
              <label className="block text-coffee-brown font-medium mb-2">
                <Mail size={16} className="inline mr-2" />
                {t('auth', 'emailAddress')}
              </label>
              <input
                type="email"
                className="input-paper w-full"
                placeholder={t('auth', 'emailPlaceholder')}
                {...register('email', {
                  required: t('auth', 'emailRequired'),
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: t('auth', 'emailInvalid'),
                  },
                })}
              />
              {errors.email && (
                <p className="text-red-600 text-sm mt-1">{errors.email.message}</p>
              )}
            </div>

            {/* Phone Number */}
            <div>
              <label className="block text-coffee-brown font-medium mb-2">
                <Phone size={16} className="inline mr-2" />
                {t('auth', 'phoneNumber')}
              </label>
              <input
                type="tel"
                className="input-paper w-full"
                placeholder={t('auth', 'phonePlaceholder')}
                {...register('phone_number', {
                  required: t('auth', 'phoneRequired'),
                  pattern: {
                    value: /^\+?[1-9]\d{1,14}$/,
                    message: t('auth', 'phoneInvalid'),
                  },
                })}
              />
              {errors.phone_number && (
                <p className="text-red-600 text-sm mt-1">{errors.phone_number.message}</p>
              )}
              <p className="text-coffee-sienna text-sm mt-1">
                {t('auth', 'phoneHint')}
              </p>
            </div>

            {/* Password */}
            <div>
              <label className="block text-coffee-brown font-medium mb-2">
                <Lock size={16} className="inline mr-2" />
                {t('auth', 'password')}
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="input-paper w-full pr-12"
                  placeholder={t('auth', 'createPassword')}
                  {...register('password', {
                    required: t('auth', 'passwordRequired'),
                    minLength: {
                      value: 8,
                      message: t('auth', 'passwordMinLength'),
                    },
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

            {/* Confirm Password */}
            <div>
              <label className="block text-coffee-brown font-medium mb-2">
                <Lock size={16} className="inline mr-2" />
                {t('auth', 'confirmPassword')}
              </label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  className="input-paper w-full pr-12"
                  placeholder={t('auth', 'confirmPassword')}
                  {...register('confirm_password', {
                    required: t('auth', 'confirmPasswordRequired'),
                    validate: (value) =>
                      value === password || t('auth', 'passwordsNotMatch'),
                  })}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-coffee-sienna hover:text-coffee-brown"
                >
                  {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {errors.confirm_password && (
                <p className="text-red-600 text-sm mt-1">{errors.confirm_password.message}</p>
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
                  <UserPlus size={20} />
                  <span>{t('auth', 'createAccount')}</span>
                </>
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-coffee-brown">
              {t('auth', 'alreadyHaveAccount')}{' '}
              <Link
                to="/login"
                className="text-coffee-sienna hover:text-coffee-brown font-medium underline"
              >
                {t('auth', 'signInHere')}
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-coffee-sienna text-sm">
            {t('auth', 'registerFooter')}
          </p>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage