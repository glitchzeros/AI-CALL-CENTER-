import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import Layout from '../components/Layout'
import { subscriptionsAPI, paymentsAPI, usersAPI } from '../services/api'
import { useAuth } from '../hooks/useAuth'
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
  const queryClient = useQueryClient()
  const [selectedTier, setSelectedTier] = useState(null)
  const [isProcessingPayment, setIsProcessingPayment] = useState(false)

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

  // Payment initiation mutation
  const initiatePaymentMutation = useMutation(
    (tierData) => subscriptionsAPI.initiatePayment(tierData),
    {
      onSuccess: (data) => {
        // Redirect to payment URL
        window.open(data.payment_url, '_blank')
        toast.success('Payment initiated. Complete the transaction in the new window.')
        setIsProcessingPayment(false)
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to initiate payment')
        setIsProcessingPayment(false)
      }
    }
  )

  const handleSubscribe = async (tier) => {
    setSelectedTier(tier)
    setIsProcessingPayment(true)
    
    try {
      await initiatePaymentMutation.mutateAsync({ tier_id: tier.id })
    } catch (error) {
      // Error handled in mutation
    }
  }

  const getTierIcon = (tierName) => {
    switch (tierName.toLowerCase()) {
      case 'apprentice': return Zap
      case 'journeyman': return Star
      case 'master scribe': return Crown
      default: return Sparkles
    }
  }

  const getTierColor = (tierName) => {
    switch (tierName.toLowerCase()) {
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
              Most Popular
            </span>
          </div>
        )}

        {isCurrentTier && (
          <div className="absolute -top-3 right-4">
            <span className="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-bold">
              Current Plan
            </span>
          </div>
        )}

        <div className="text-center mb-6">
          <div className={`w-16 h-16 mx-auto mb-4 bg-coffee-khaki rounded-full flex items-center justify-center border-4 border-${colorClass}`}>
            <Icon size={32} className={`text-${colorClass}`} />
          </div>
          
          <h3 className="heading-secondary text-xl mb-2">{tier.name}</h3>
          <div className="mb-4">
            <span className="text-4xl font-bold text-coffee-brown">${tier.price_usd}</span>
            <span className="text-coffee-sienna ml-2">USD/month</span>
          </div>
        </div>

        <div className="space-y-4 mb-8">
          <div className="flex items-start space-x-3">
            <Check size={20} className="text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-coffee-brown">Context Memory</p>
              <p className="text-sm text-coffee-sienna">{formatContextLimit(tier.context_limit)}</p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <Check size={20} className="text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-coffee-brown">Multi-Channel Support</p>
              <p className="text-sm text-coffee-sienna">Voice, SMS, and Telegram integration</p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <Check size={20} className="text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-coffee-brown">Visual Workflow Builder</p>
              <p className="text-sm text-coffee-sienna">Drag-and-drop Invocation Editor</p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <Check size={20} className="text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-coffee-brown">Real-time Analytics</p>
              <p className="text-sm text-coffee-sienna">Comprehensive performance insights</p>
            </div>
          </div>

          {tier.name.toLowerCase() === 'master scribe' && (
            <>
              <div className="flex items-start space-x-3">
                <Crown size={20} className="text-yellow-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-coffee-brown">Priority Support</p>
                  <p className="text-sm text-coffee-sienna">Dedicated assistance channel</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Crown size={20} className="text-yellow-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-coffee-brown">Advanced Features</p>
                  <p className="text-sm text-coffee-sienna">Early access to new capabilities</p>
                </div>
              </div>
            </>
          )}
        </div>

        <button
          onClick={() => handleSubscribe(tier)}
          disabled={isCurrentTier || isProcessingPayment}
          className={`w-full ${
            isCurrentTier 
              ? 'btn-secondary opacity-50 cursor-not-allowed' 
              : isRecommended 
                ? 'bg-yellow-400 hover:bg-yellow-500 text-yellow-900 font-bold py-3 px-6 rounded border-2 border-yellow-600'
                : 'btn-primary'
          } flex items-center justify-center space-x-2`}
        >
          {isProcessingPayment && selectedTier?.id === tier.id ? (
            <div className="loading-quill w-5 h-5"></div>
          ) : isCurrentTier ? (
            <>
              <Check size={20} />
              <span>Current Plan</span>
            </>
          ) : (
            <>
              <CreditCard size={20} />
              <span>Subscribe Now</span>
              <ArrowRight size={16} />
            </>
          )}
        </button>
      </div>
    )
  }

  if (tiersLoading || profileLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="loading-quill mb-4"></div>
            <p className="text-coffee-brown">The Scribe is preparing subscription options...</p>
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
          <h1 className="heading-primary text-3xl mb-4">Choose Your Scribe's Power</h1>
          <p className="text-coffee-sienna text-lg max-w-2xl mx-auto">
            Select the subscription tier that best fits your communication needs. 
            Each tier offers different context memory capabilities for your AI conversations.
          </p>
        </div>

        {/* Current Subscription Status */}
        {profile?.subscription && (
          <div className="paper-panel bg-coffee-green bg-opacity-10 border-2 border-coffee-green">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-coffee-green bg-opacity-20 rounded-full">
                  <Shield size={24} className="text-coffee-green" />
                </div>
                <div>
                  <h3 className="font-semibold text-coffee-brown">Active Subscription</h3>
                  <p className="text-coffee-sienna">
                    {profile.subscription.tier_name} - ${profile.subscription.price_usd}/month
                  </p>
                  <p className="text-sm text-coffee-sienna">
                    Next billing: {new Date(profile.subscription.expires_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              
              <div className="text-right">
                <div className="flex items-center space-x-2 text-green-600">
                  <Check size={20} />
                  <span className="font-medium">Active</span>
                </div>
              </div>
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
      </div>
    </Layout>
  )
}

export default SubscriptionPage