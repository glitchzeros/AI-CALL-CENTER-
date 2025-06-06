import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useAuth } from '../hooks/useAuth'
import { Eye, EyeOff, UserPlus, Phone, Mail, Lock } from 'lucide-react'

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
          <div className="text-center mb-8">
            <h1 className="heading-decorative text-4xl mb-2">Verification</h1>
            <p className="text-coffee-brown">
              A verification code has been sent to your phone
            </p>
            <p className="text-coffee-sienna text-sm mt-2">{registrationEmail}</p>
          </div>

          <div className="paper-panel">
            <form onSubmit={handleVerification} className="space-y-6">
              <div>
                <label className="block text-coffee-brown font-medium mb-2">
                  Verification Code
                </label>
                <input
                  type="text"
                  maxLength="6"
                  className="input-paper w-full text-center text-2xl tracking-widest"
                  placeholder="000000"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
                />
                <p className="text-coffee-sienna text-sm mt-2">
                  Enter the 6-digit code sent to your phone
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
                  'Verify Code'
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
                  `Resend in ${countdown}s`
                ) : (
                  'Resend Code'
                )}
              </button>
            </div>

            <div className="mt-4 text-center">
              <button
                onClick={() => setStep('register')}
                className="text-coffee-sienna hover:text-coffee-brown text-sm underline"
              >
                Back to registration
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
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="heading-decorative text-4xl mb-2">Join Aetherium</h1>
          <p className="text-coffee-sienna text-lg">Begin Your Journey</p>
          <p className="text-coffee-brown mt-2">Create your account to access the Scribe's realm</p>
        </div>

        {/* Registration Form */}
        <div className="paper-panel">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Email */}
            <div>
              <label className="block text-coffee-brown font-medium mb-2">
                <Mail size={16} className="inline mr-2" />
                Email Address
              </label>
              <input
                type="email"
                className="input-paper w-full"
                placeholder="your.email@example.com"
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Invalid email address',
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
                Phone Number
              </label>
              <input
                type="tel"
                className="input-paper w-full"
                placeholder="+998901234567"
                {...register('phone_number', {
                  required: 'Phone number is required',
                  pattern: {
                    value: /^\+?[1-9]\d{1,14}$/,
                    message: 'Invalid phone number format',
                  },
                })}
              />
              {errors.phone_number && (
                <p className="text-red-600 text-sm mt-1">{errors.phone_number.message}</p>
              )}
              <p className="text-coffee-sienna text-sm mt-1">
                Include country code (e.g., +998901234567)
              </p>
            </div>

            {/* Password */}
            <div>
              <label className="block text-coffee-brown font-medium mb-2">
                <Lock size={16} className="inline mr-2" />
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="input-paper w-full pr-12"
                  placeholder="Create a strong password"
                  {...register('password', {
                    required: 'Password is required',
                    minLength: {
                      value: 8,
                      message: 'Password must be at least 8 characters',
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
                Confirm Password
              </label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  className="input-paper w-full pr-12"
                  placeholder="Confirm your password"
                  {...register('confirm_password', {
                    required: 'Please confirm your password',
                    validate: (value) =>
                      value === password || 'Passwords do not match',
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
                  <span>Create Account</span>
                </>
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-coffee-brown">
              Already have an account?{' '}
              <Link
                to="/login"
                className="text-coffee-sienna hover:text-coffee-brown font-medium underline"
              >
                Sign in here
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-coffee-sienna text-sm">
            By creating an account, you agree to let the Scribe serve your communication needs
          </p>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage