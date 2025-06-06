import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useAuth } from '../hooks/useAuth'
import { Eye, EyeOff, LogIn } from 'lucide-react'

const LoginPage = () => {
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const { login, isAuthenticated, isFirstLogin } = useAuth()
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
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="heading-decorative text-4xl mb-2">Aetherium</h1>
          <p className="text-coffee-sienna text-lg">The Scribe's Portal</p>
          <p className="text-coffee-brown mt-2">Enter your credentials to access the realm</p>
        </div>

        {/* Login Form */}
        <div className="paper-panel">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Login Identifier */}
            <div>
              <label className="block text-coffee-brown font-medium mb-2">
                Email or Phone Number
              </label>
              <input
                type="text"
                className="input-paper w-full"
                placeholder="Enter your email or phone number"
                {...register('login_identifier', {
                  required: 'Email or phone number is required',
                })}
              />
              {errors.login_identifier && (
                <p className="text-red-600 text-sm mt-1">{errors.login_identifier.message}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="block text-coffee-brown font-medium mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="input-paper w-full pr-12"
                  placeholder="Enter your password"
                  {...register('password', {
                    required: 'Password is required',
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
                  <span>Enter the Realm</span>
                </>
              )}
            </button>
          </form>

          {/* Register Link */}
          <div className="mt-6 text-center">
            <p className="text-coffee-brown">
              New to Aetherium?{' '}
              <Link
                to="/register"
                className="text-coffee-sienna hover:text-coffee-brown font-medium underline"
              >
                Begin your journey
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-coffee-sienna text-sm">
            "Where AI Scribes dwell and conversations flow like ink upon parchment"
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage