import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import Layout from '../components/Layout'
import { subscriptionsAPI, paymentsAPI, usersAPI } from '../services/api'
import { useAuth } from '../hooks/useAuth'
import { useTranslation, LanguageSelector } from '../hooks/useTranslation'
import toast from 'react-hot-toast'
import {
  Crown,
  Zap,
  Star,
  Check,
  CreditCard,
  Clock,
  TrendingUp,
  Shield,
  Sparkles,
  ArrowRight,
  RefreshCw
} from 'lucide-react'

const SubscriptionPage = () => {
  const { user } = useAuth()
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [selectedTier, setSelectedTier] = useState(null)
  const [isProcessingPayment, setIsProcessingPayment] = useState(false)
  const [showPaymentMonitoring, setShowPaymentMonitoring] = useState(false)
  const [bankCardNumber, setBankCardNumber] = useState('')
  const [paymentSession, setPaymentSession] = useState(null)
  const [timeRemaining, setTimeRemaining] = useState(0)

  // Fetch subscription tiers
  const { data: tiers, isLoading: tiersLoading } = useQuery(
    'subscription-tiers',
    subscriptionsAPI.getTiers
  )

  // Fetch user profile for current subscription
  const { data: profile, isLoading: profileLoading } = useQuery(
    'user-profile',
    usersAPI.getProfile
  )

  // Fetch payment transactions
  const { data: transactions, isLoading: transactionsLoading } = useQuery(
    'payment-transactions',
    () => paymentsAPI.getTransactions({ limit: 10 })
  )

  // Fetch current subscription and usage
  const { data: mySubscription, isLoading: subscriptionLoading } = useQuery(
    'my-subscription',
    subscriptionsAPI.getMySubscription,
    { refetchInterval: 30000 } // Refresh every 30 seconds
  )

  // Fetch usage status
  const { data: usageStatus, isLoading: usageLoading } = useQuery(
    'usage-status',
    subscriptionsAPI.getUsageStatus,
    { refetchInterval: 60000 } // Refresh every minute
  )

  // Manual payment initiation mutation
  const initiatePaymentMutation = useMutation(
    (tierData) => paymentsAPI.initiateConsultationPayment(tierData),
    {
      onSuccess: (data) => {
        // Show payment instructions modal
        setPaymentInstructions(data)
        setShowPaymentModal(true)
        setIsProcessingPayment(false)
        toast.success('To\'lov ko\'rsatmalari tayyor. 30 daqiqa ichida to\'lovni amalga oshiring.')
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'To\'lov boshlanmadi')
        setIsProcessingPayment(false)
      }
    }
  )

  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [paymentInstructions, setPaymentInstructions] = useState(null)

  const handleSubscribe = async (tier) => {
    setSelectedTier(tier)
    setIsProcessingPayment(true)
    
    try {
      await initiatePaymentMutation.mutateAsync({ tier_name: tier.name })
    } catch (error) {
      // Error handled in mutation
    }
  }

  // Timer for payment window
  useEffect(() => {
    if (paymentInstructions && showPaymentModal) {
      const interval = setInterval(() => {
        const now = new Date()
        const expiresAt = new Date(paymentInstructions.expires_at)
        const remaining = Math.max(0, Math.floor((expiresAt - now) / 1000))
        
        setTimeRemaining(remaining)
        
        if (remaining === 0) {
          setShowPaymentModal(false)
          toast.error('To\'lov vaqti tugadi. Qaytadan urinib ko\'ring.')
        }
      }, 1000)
      
      return () => clearInterval(interval)
    }
  }, [paymentInstructions, showPaymentModal])

  // Check for active payment monitoring session on load
  useEffect(() => {
    checkPaymentMonitoringStatus()
  }, [])

  // Timer for payment monitoring session
  useEffect(() => {
    if (paymentSession && paymentSession.time_remaining_seconds > 0) {
      const interval = setInterval(() => {
        setTimeRemaining(prev => {
          const newTime = Math.max(0, prev - 1)
          if (newTime === 0) {
            setPaymentSession(null)
            setShowPaymentMonitoring(false)
            toast.error('Payment monitoring expired. Please try again.')
          }
          return newTime
        })
      }, 1000)
      
      return () => clearInterval(interval)
    }
  }, [paymentSession])

  const checkPaymentMonitoringStatus = async () => {
    try {
      const response = await subscriptionsAPI.getPaymentMonitoringStatus()
      if (response.data.has_active_session) {
        setPaymentSession(response.data.session)
        setTimeRemaining(response.data.session.time_remaining_seconds)
        setShowPaymentMonitoring(true)
      }
    } catch (error) {
      console.error('Failed to check payment monitoring status:', error)
    }
  }

  const startPaymentMonitoring = async (tier) => {
    if (!bankCardNumber.trim()) {
      toast.error('Please enter a bank card number')
      return
    }

    setIsProcessingPayment(true)
    try {
      const response = await subscriptionsAPI.startPaymentMonitoring({
        tier_id: tier.id,
        bank_card_number: bankCardNumber.trim()
      })

      setPaymentSession(response.data.monitoring_session)
      setTimeRemaining(30 * 60) // 30 minutes
      setShowPaymentMonitoring(true)
      toast.success(response.data.message)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to start payment monitoring')
    } finally {
      setIsProcessingPayment(false)
    }
  }

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const getTierIcon = (tierName) => {
    switch (tierName.toLowerCase()) {
      case 'tier1': return Zap
      case 'tier2': return Star
      case 'tier3': return Crown
      case 'apprentice': return Zap
      case 'journeyman': return Star
      case 'master scribe': return Crown
      default: return Sparkles
    }
  }

  const getTierColor = (tierName) => {
    switch (tierName.toLowerCase()) {
      case 'tier1': return 'coffee-brown'
      case 'tier2': return 'coffee-sienna'
      case 'tier3': return 'yellow-600'
      case 'apprentice': return 'coffee-brown'
      case 'journeyman': return 'coffee-sienna'
      case 'master scribe': return 'yellow-600'
      default: return 'coffee-brown'
    }
  }

  const formatContextLimit = (limit) => {
    if (limit >= 32000) return 'Full Session History (Unlimited Tokens for Session Duration)'
    if (limit >= 4000) return `Up to ${(limit / 1000).toFixed(0)}K Tokens (Approx. 1 hour)`
    return `Up to ${(limit / 1000).toFixed(0)}K Tokens (Approx. 5 mins)`
  }

  const SubscriptionTierCard = ({ tier, isCurrentTier = false, isRecommended = false }) => {
    const Icon = getTierIcon(tier.name)
    const colorClass = getTierColor(tier.name)

    return (
      <div className={`relative paper-panel ${isRecommended ? 'border-4 border-yellow-400' : ''} ${isCurrentTier ? 'bg-coffee-green bg-opacity-10' : ''}`}>
        {isRecommended && (
          <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
            <span className="bg-yellow-400 text-yellow-900 px-4 py-1 rounded-full text-sm font-bold">
{t('subscription', 'mostPopular')}
            </span>
          </div>
        )}

        {isCurrentTier && (
          <div className="absolute -top-3 right-4">
            <span className="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-bold">
{t('subscription', 'currentPlan')}
            </span>
          </div>
        )}

        <div className="text-center mb-6">
          <div className={`w-16 h-16 mx-auto mb-4 bg-coffee-khaki rounded-full flex items-center justify-center border-4 border-${colorClass}`}>
            <Icon size={32} className={`text-${colorClass}`} />
          </div>
          
          <h3 className="heading-secondary text-xl mb-2">{tier.display_name || tier.name}</h3>
          <div className="mb-4">
            <span className="text-3xl font-bold text-coffee-brown">{tier.price_uzs?.toLocaleString() || (tier.price_usd * 12300).toLocaleString()}</span>
            <span className="text-coffee-sienna ml-2">so'm/oy</span>
            <div className="text-sm text-coffee-sienna mt-1">
              (${tier.price_usd} USD)
            </div>
          </div>
        </div>

        <div className="space-y-4 mb-8">
          {/* Daily AI Minutes */}
          <div className="flex items-start space-x-3">
            <Check size={20} className="text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-coffee-brown">Daily AI Call Processing</p>
              <p className="text-sm text-coffee-sienna">
                {tier.max_daily_ai_minutes >= 999999 ? 'Unlimited minutes' : `${tier.max_daily_ai_minutes} minutes per day`}
              </p>
            </div>
          </div>

          {/* Daily SMS */}
          <div className="flex items-start space-x-3">
            <Check size={20} className="text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-coffee-brown">Daily SMS Limit</p>
              <p className="text-sm text-coffee-sienna">
                {tier.max_daily_sms >= 999999 ? 'Unlimited SMS' : `${tier.max_daily_sms} SMS per day (incoming + outgoing)`}
              </p>
            </div>
          </div>

          {/* Agentic Functions */}
          {tier.has_agentic_functions && (
            <div className="flex items-start space-x-3">
              <Check size={20} className="text-green-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-medium text-coffee-brown">Agentic Functions Access</p>
                <p className="text-sm text-coffee-sienna">Access to advanced AI agent capabilities</p>
              </div>
            </div>
          )}

          {/* Agentic Constructor */}
          {tier.has_agentic_constructor && (
            <div className="flex items-start space-x-3">
              <Check size={20} className="text-green-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-medium text-coffee-brown">Agentic Functions Constructor</p>
                <p className="text-sm text-coffee-sienna">Build and customize your own AI agent functions</p>
              </div>
            </div>
          )}

          <div className="flex items-start space-x-3">
            <Check size={20} className="text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-coffee-brown">{t('subscription', 'contextMemory')}</p>
              <p className="text-sm text-coffee-sienna">{formatContextLimit(tier.context_limit)}</p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <Check size={20} className="text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-coffee-brown">{t('subscription', 'multiChannelSupport')}</p>
              <p className="text-sm text-coffee-sienna">{t('subscription', 'multiChannelDesc')}</p>
            </div>
          </div>

          {(tier.name.toLowerCase() === 'master scribe' || tier.name.toLowerCase() === 'tier3') && (
            <>
              <div className="flex items-start space-x-3">
                <Crown size={20} className="text-yellow-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-coffee-brown">{t('subscription', 'prioritySupport')}</p>
                  <p className="text-sm text-coffee-sienna">{t('subscription', 'prioritySupportDesc')}</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Crown size={20} className="text-yellow-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-coffee-brown">{t('subscription', 'advancedFeatures')}</p>
                  <p className="text-sm text-coffee-sienna">{t('subscription', 'advancedFeaturesDesc')}</p>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Payment Options */}
        <div className="space-y-3">
          {!isCurrentTier && (
            <>
              {/* Bank Card Input for Payment Monitoring */}
              <div>
                <label className="block text-coffee-brown text-sm font-medium mb-2">
                  Bank Card Number (for payment monitoring)
                </label>
                <input
                  type="text"
                  value={bankCardNumber}
                  onChange={(e) => setBankCardNumber(e.target.value)}
                  placeholder="8600 1234 5678 9012"
                  className="input-paper w-full text-sm"
                  disabled={isProcessingPayment}
                />
              </div>

              {/* Payment Monitoring Button */}
              <button
                onClick={() => startPaymentMonitoring(tier)}
                disabled={isProcessingPayment || !bankCardNumber.trim()}
                className={`w-full ${
                  isRecommended 
                    ? 'bg-yellow-400 hover:bg-yellow-500 text-yellow-900 font-bold py-3 px-6 rounded border-2 border-yellow-600'
                    : 'btn-primary'
                } flex items-center justify-center space-x-2`}
              >
                {isProcessingPayment && selectedTier?.id === tier.id ? (
                  <div className="loading-quill w-5 h-5"></div>
                ) : (
                  <>
                    <Clock size={20} />
                    <span>Start Payment Monitoring (30 min)</span>
                  </>
                )}
              </button>

              {/* Traditional Payment Button */}
              <button
                onClick={() => handleSubscribe(tier)}
                disabled={isProcessingPayment}
                className="w-full btn-secondary flex items-center justify-center space-x-2"
              >
                {isProcessingPayment && selectedTier?.id === tier.id ? (
                  <div className="loading-quill w-5 h-5"></div>
                ) : (
                  <>
                    <CreditCard size={20} />
                    <span>Traditional Payment</span>
                  </>
                )}
              </button>
            </>
          )}

          {isCurrentTier && (
            <button
              disabled
              className="w-full btn-secondary opacity-50 cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <Check size={20} />
              <span>{t('subscription', 'currentPlan')}</span>
            </button>
          )}
        </div>
      </div>
    )
  }

  if (tiersLoading || profileLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="loading-quill mb-4"></div>
            <p className="text-coffee-brown">{t('subscription', 'loading')}</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <LanguageSelector />
          </div>
          <h1 className="heading-primary text-3xl mb-4">{t('subscription', 'title')}</h1>
          <p className="text-coffee-sienna text-lg max-w-2xl mx-auto">
            {t('subscription', 'subtitle')}
          </p>
        </div>

        {/* Current Subscription Status */}
        {mySubscription?.data?.has_subscription && (
          <div className="paper-panel bg-coffee-green bg-opacity-10 border-2 border-coffee-green">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-coffee-green bg-opacity-20 rounded-full">
                  <Shield size={24} className="text-coffee-green" />
                </div>
                <div>
                  <h3 className="font-semibold text-coffee-brown">{t('subscription', 'currentPlan')}</h3>
                  <p className="text-coffee-sienna">
                    {mySubscription.data.tier.display_name} - {mySubscription.data.tier.price_uzs?.toLocaleString()} UZS/month
                  </p>
                  <p className="text-sm text-coffee-sienna">
                    {t('subscription', 'nextBilling')}: {mySubscription.data.subscription.expires_at ? new Date(mySubscription.data.subscription.expires_at).toLocaleDateString() : 'N/A'}
                  </p>
                </div>
              </div>
              
              <div className="text-right">
                <div className="flex items-center space-x-2 text-green-600">
                  <Check size={20} />
                  <span className="font-medium">{t('subscription', 'active')}</span>
                </div>
              </div>
            </div>

            {/* Daily Usage Status */}
            {mySubscription.data.usage && (
              <div className="border-t border-coffee-green border-opacity-30 pt-4">
                <h4 className="font-medium text-coffee-brown mb-3">Today's Usage</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* AI Minutes Usage */}
                  <div className="bg-white bg-opacity-50 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-coffee-brown">AI Call Processing</span>
                      <span className="text-xs text-coffee-sienna">
                        {mySubscription.data.usage.ai_minutes_used || 0} / {mySubscription.data.usage.ai_minutes_limit >= 999999 ? '∞' : mySubscription.data.usage.ai_minutes_limit} min
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-coffee-green h-2 rounded-full transition-all duration-300"
                        style={{
                          width: mySubscription.data.usage.ai_minutes_limit >= 999999 
                            ? '20%' 
                            : `${Math.min(100, (mySubscription.data.usage.ai_minutes_used / mySubscription.data.usage.ai_minutes_limit) * 100)}%`
                        }}
                      ></div>
                    </div>
                  </div>

                  {/* SMS Usage */}
                  <div className="bg-white bg-opacity-50 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-coffee-brown">SMS Messages</span>
                      <span className="text-xs text-coffee-sienna">
                        {mySubscription.data.usage.sms_count_used || 0} / {mySubscription.data.usage.sms_limit >= 999999 ? '∞' : mySubscription.data.usage.sms_limit}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-coffee-sienna h-2 rounded-full transition-all duration-300"
                        style={{
                          width: mySubscription.data.usage.sms_limit >= 999999 
                            ? '20%' 
                            : `${Math.min(100, (mySubscription.data.usage.sms_count_used / mySubscription.data.usage.sms_limit) * 100)}%`
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Payment Monitoring Status */}
        {showPaymentMonitoring && paymentSession && (
          <div className="paper-panel bg-blue-50 border-2 border-blue-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-blue-100 rounded-full">
                  <Clock size={24} className="text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-coffee-brown">Payment Monitoring Active</h3>
                  <p className="text-coffee-sienna">
                    Monitoring payments to card: {paymentSession.bank_card_number}
                  </p>
                  <p className="text-sm text-coffee-sienna">
                    Amount: {paymentSession.amount_uzs?.toLocaleString()} UZS (${paymentSession.amount_usd})
                  </p>
                  <p className="text-sm text-coffee-sienna">
                    Reference: {paymentSession.reference_code}
                  </p>
                </div>
              </div>
              
              <div className="text-right">
                <div className={`text-lg font-bold ${timeRemaining < 300 ? 'text-red-600' : 'text-blue-600'}`}>
                  {formatTime(timeRemaining)}
                </div>
                <p className="text-sm text-coffee-sienna">remaining</p>
              </div>
            </div>
            
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                <strong>Instructions:</strong> Transfer {paymentSession.amount_uzs?.toLocaleString()} UZS to card 
                {paymentSession.bank_card_number} with reference "{paymentSession.reference_code}". 
                We'll automatically detect the payment via SMS and activate your subscription.
              </p>
            </div>
          </div>
        )}

        {/* Subscription Tiers */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {tiers?.map((tier, index) => (
            <SubscriptionTierCard
              key={tier.id}
              tier={tier}
              isCurrentTier={profile?.subscription?.tier_id === tier.id}
              isRecommended={index === 1} // Middle tier is recommended
            />
          ))}
        </div>

        {/* Features Comparison */}
        <div className="paper-panel">
          <h2 className="heading-secondary mb-6">Feature Comparison</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-coffee-tan">
                  <th className="text-left py-3 px-4 font-medium text-coffee-brown">Feature</th>
                  {tiers?.map(tier => (
                    <th key={tier.id} className="text-center py-3 px-4 font-medium text-coffee-brown">
                      {tier.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-coffee-tan">
                  <td className="py-3 px-4 text-coffee-brown">Context Memory</td>
                  {tiers?.map(tier => (
                    <td key={tier.id} className="text-center py-3 px-4 text-coffee-sienna">
                      {tier.context_limit >= 32000 ? 'Unlimited' : `${(tier.context_limit / 1000).toFixed(0)}K tokens`}
                    </td>
                  ))}
                </tr>
                <tr className="border-b border-coffee-tan">
                  <td className="py-3 px-4 text-coffee-brown">Concurrent Sessions</td>
                  {tiers?.map(tier => (
                    <td key={tier.id} className="text-center py-3 px-4 text-coffee-sienna">
                      Up to 40
                    </td>
                  ))}
                </tr>
                <tr className="border-b border-coffee-tan">
                  <td className="py-3 px-4 text-coffee-brown">Multi-Channel Support</td>
                  {tiers?.map(tier => (
                    <td key={tier.id} className="text-center py-3 px-4">
                      <Check size={20} className="text-green-600 mx-auto" />
                    </td>
                  ))}
                </tr>
                <tr className="border-b border-coffee-tan">
                  <td className="py-3 px-4 text-coffee-brown">Analytics & Reporting</td>
                  {tiers?.map(tier => (
                    <td key={tier.id} className="text-center py-3 px-4">
                      <Check size={20} className="text-green-600 mx-auto" />
                    </td>
                  ))}
                </tr>
                <tr className="border-b border-coffee-tan">
                  <td className="py-3 px-4 text-coffee-brown">Priority Support</td>
                  {tiers?.map((tier, index) => (
                    <td key={tier.id} className="text-center py-3 px-4">
                      {index === 2 ? (
                        <Check size={20} className="text-green-600 mx-auto" />
                      ) : (
                        <span className="text-coffee-sienna">Standard</span>
                      )}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Payment History */}
        {transactions && transactions.length > 0 && (
          <div className="paper-panel">
            <div className="flex items-center justify-between mb-6">
              <h2 className="heading-secondary">Payment History</h2>
              <button
                onClick={() => queryClient.invalidateQueries('payment-transactions')}
                className="btn-secondary flex items-center space-x-2"
              >
                <RefreshCw size={16} />
                <span>Refresh</span>
              </button>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b-2 border-coffee-tan">
                    <th className="text-left py-3 px-4 font-medium text-coffee-brown">Date</th>
                    <th className="text-left py-3 px-4 font-medium text-coffee-brown">Amount</th>
                    <th className="text-left py-3 px-4 font-medium text-coffee-brown">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-coffee-brown">Transaction ID</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map(transaction => (
                    <tr key={transaction.id} className="border-b border-coffee-tan">
                      <td className="py-3 px-4 text-coffee-brown">
                        {new Date(transaction.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4 text-coffee-brown">
                        ${transaction.amount.toFixed(2)}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          transaction.status === 'completed' 
                            ? 'bg-green-100 text-green-800'
                            : transaction.status === 'pending'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {transaction.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-coffee-sienna font-mono text-sm">
                        {transaction.merchant_trans_id || transaction.id}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* FAQ Section */}
        <div className="paper-panel coffee-stain">
          <h2 className="heading-secondary mb-6">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-medium text-coffee-brown mb-2">What is context memory?</h3>
              <p className="text-coffee-sienna">
                Context memory determines how much conversation history your Scribe can remember during a session. 
                Higher limits allow for more natural, coherent conversations over longer periods.
              </p>
            </div>
            
            <div>
              <h3 className="font-medium text-coffee-brown mb-2">Can I change my subscription tier?</h3>
              <p className="text-coffee-sienna">
                Yes, you can upgrade or downgrade your subscription at any time. Changes take effect immediately, 
                and billing is prorated accordingly.
              </p>
            </div>
            
            <div>
              <h3 className="font-medium text-coffee-brown mb-2">What payment methods are accepted?</h3>
              <p className="text-coffee-sienna">
                We accept all major credit cards and local payment methods through our secure Click payment gateway.
              </p>
            </div>
            
            <div>
              <h3 className="font-medium text-coffee-brown mb-2">Is there a free trial?</h3>
              <p className="text-coffee-sienna">
                New users receive a 7-day trial with Apprentice tier features to explore the platform capabilities.
              </p>
            </div>
          </div>
        </div>

        {/* Payment Instructions Modal */}
        {showPaymentModal && paymentInstructions && (
          <PaymentInstructionsModal
            instructions={paymentInstructions}
            timeRemaining={timeRemaining}
            onClose={() => setShowPaymentModal(false)}
          />
        )}
      </div>
    </Layout>
  )
}

// Payment Instructions Modal Component
const PaymentInstructionsModal = ({ instructions, timeRemaining, onClose }) => {
  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    toast.success('Nusxalandi!')
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="modal-scroll max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="heading-secondary text-2xl">To'lov Ko'rsatmalari</h2>
          <div className="flex items-center space-x-4">
            <div className={`text-lg font-bold ${timeRemaining < 300 ? 'text-red-600' : 'text-coffee-brown'}`}>
              {formatTime(timeRemaining)}
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-coffee-tan rounded-full"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {/* Amount Display */}
          <div className="text-center bg-coffee-khaki p-6 rounded-lg border-2 border-coffee-sienna">
            <h3 className="text-2xl font-bold text-coffee-brown mb-2">
              {instructions.amount_uzs?.toLocaleString()} so'm
            </h3>
            <p className="text-coffee-sienna">
              (${instructions.amount_usd} USD) - {instructions.payment_instructions?.title}
            </p>
          </div>

          {/* Bank Details */}
          <div className="bg-coffee-beige p-6 rounded-lg border border-coffee-tan">
            <h3 className="font-bold text-coffee-brown mb-4">Bank Ma'lumotlari:</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-coffee-sienna">Karta raqami:</span>
                <div className="flex items-center space-x-2">
                  <span className="font-mono font-bold text-coffee-brown">
                    {instructions.bank_details?.card_number}
                  </span>
                  <button
                    onClick={() => copyToClipboard(instructions.bank_details?.card_number)}
                    className="btn-secondary text-xs px-2 py-1"
                  >
                    Nusxalash
                  </button>
                </div>
              </div>
              
              <div className="flex justify-between">
                <span className="text-coffee-sienna">Bank:</span>
                <span className="font-medium text-coffee-brown">
                  {instructions.bank_details?.bank_name}
                </span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-coffee-sienna">Karta egasi:</span>
                <span className="font-medium text-coffee-brown">
                  {instructions.bank_details?.cardholder_name}
                </span>
              </div>
            </div>
          </div>

          {/* Reference Code */}
          <div className="bg-yellow-50 border-2 border-yellow-400 p-4 rounded-lg">
            <h3 className="font-bold text-yellow-800 mb-2">Muhim! Reference Kod:</h3>
            <div className="flex items-center justify-between">
              <span className="font-mono text-xl font-bold text-yellow-900">
                {instructions.reference_code}
              </span>
              <button
                onClick={() => copyToClipboard(instructions.reference_code)}
                className="bg-yellow-400 hover:bg-yellow-500 text-yellow-900 px-3 py-1 rounded font-medium"
              >
                Nusxalash
              </button>
            </div>
            <p className="text-yellow-800 text-sm mt-2">
              To'lov izohida albatta ushbu kodni ko'rsating!
            </p>
          </div>

          {/* Instructions */}
          <div className="space-y-4">
            <h3 className="font-bold text-coffee-brown">Ko'rsatmalar:</h3>
            <ol className="list-decimal list-inside space-y-2 text-coffee-brown">
              {instructions.payment_instructions?.instructions?.map((instruction, index) => (
                <li key={index} className="text-sm">{instruction}</li>
              ))}
            </ol>
          </div>

          {/* Important Notes */}
          <div className="bg-red-50 border-2 border-red-400 p-4 rounded-lg">
            <h3 className="font-bold text-red-800 mb-2">Diqqat!</h3>
            <ul className="list-disc list-inside space-y-1 text-red-800 text-sm">
              {instructions.payment_instructions?.important_notes?.map((note, index) => (
                <li key={index}>{note}</li>
              ))}
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between space-x-4">
            <button
              onClick={onClose}
              className="btn-secondary flex-1"
            >
              Yopish
            </button>
            <button
              onClick={() => {
                // Refresh page to check payment status
                window.location.reload()
              }}
              className="btn-primary flex-1"
            >
              To'lov Holatini Tekshirish
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SubscriptionPage