import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Phone, ArrowRight, Copy, Check } from 'lucide-react'
import toast from 'react-hot-toast'

const CompanyNumberPage = () => {
  const { user, clearFirstLoginFlag } = useAuth()
  const navigate = useNavigate()
  const [copied, setCopied] = React.useState(false)

  useEffect(() => {
    // This page should only be shown on first login
    // If user doesn't have a company number, something went wrong
    if (!user?.company_number) {
      navigate('/dashboard')
    }
  }, [user, navigate])

  const handleCopyNumber = async () => {
    if (user?.company_number) {
      try {
        await navigator.clipboard.writeText(user.company_number)
        setCopied(true)
        toast.success('Company number copied to clipboard')
        setTimeout(() => setCopied(false), 2000)
      } catch (error) {
        toast.error('Failed to copy number')
      }
    }
  }

  const handleContinue = () => {
    clearFirstLoginFlag()
    navigate('/dashboard')
  }

  if (!user?.company_number) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-coffee-beige">
        <div className="loading-quill"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-coffee-beige px-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="heading-decorative text-4xl mb-4">Welcome to Aetherium</h1>
          <p className="text-coffee-sienna text-xl">Your Scribe Awaits</p>
        </div>

        {/* Main Content */}
        <div className="paper-panel text-center">
          {/* Phone Icon */}
          <div className="mb-6">
            <div className="w-24 h-24 mx-auto bg-coffee-khaki rounded-full flex items-center justify-center border-3 border-coffee-sienna">
              <Phone size={48} className="text-coffee-brown" />
            </div>
          </div>

          {/* Company Number Display */}
          <div className="mb-8">
            <h2 className="heading-secondary mb-4">Your Scribe's Direct Line</h2>
            
            <div className="bg-coffee-khaki border-2 border-coffee-sienna rounded-lg p-6 mb-4">
              <div className="flex items-center justify-center space-x-4">
                <span className="text-3xl font-mono font-bold text-coffee-brown">
                  {user.company_number}
                </span>
                <button
                  onClick={handleCopyNumber}
                  className="p-2 hover:bg-coffee-tan rounded-full transition-colors"
                  title="Copy number"
                >
                  {copied ? (
                    <Check size={24} className="text-green-600" />
                  ) : (
                    <Copy size={24} className="text-coffee-brown" />
                  )}
                </button>
              </div>
            </div>

            {/* Sacred Text */}
            <div className="bg-coffee-beige border border-coffee-tan rounded-lg p-6 mb-6">
              <p className="text-coffee-brown text-lg italic leading-relaxed">
                "This is your Scribe's direct line. It is the conduit for your automated conversations. Guard it well."
              </p>
            </div>
          </div>

          {/* Instructions */}
          <div className="text-left mb-8">
            <h3 className="heading-secondary mb-4 text-center">What This Means</h3>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-coffee-sienna rounded-full flex items-center justify-center text-coffee-beige text-sm font-bold mt-1">
                  1
                </div>
                <p className="text-coffee-brown">
                  This phone number is exclusively yours - it's where your AI Scribe will receive and make calls
                </p>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-coffee-sienna rounded-full flex items-center justify-center text-coffee-beige text-sm font-bold mt-1">
                  2
                </div>
                <p className="text-coffee-brown">
                  Share this number with your customers for automated support and services
                </p>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-coffee-sienna rounded-full flex items-center justify-center text-coffee-beige text-sm font-bold mt-1">
                  3
                </div>
                <p className="text-coffee-brown">
                  Configure your Scribe's behavior using the Invocation Editor in your dashboard
                </p>
              </div>
            </div>
          </div>

          {/* Continue Button */}
          <button
            onClick={handleContinue}
            className="btn-primary flex items-center justify-center space-x-2 mx-auto"
          >
            <span>Enter the Dashboard</span>
            <ArrowRight size={20} />
          </button>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-coffee-sienna text-sm">
            Your journey with the Scribe begins now. May your conversations flow like ink upon parchment.
          </p>
        </div>
      </div>
    </div>
  )
}

export default CompanyNumberPage