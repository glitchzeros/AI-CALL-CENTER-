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
  Shield,
  Sparkles,
  ArrowRight,
  RefreshCw,
  XCircle,
} from 'lucide-react'
import { CardSkeleton, SkeletonLoader } from '../components/LoadingSpinner'

const SubscriptionPage = () => {
  const { user } = useAuth()
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [selectedTier, setSelectedTier] = useState(null)
  const [isProcessingPayment, setIsProcessingPayment] = useState(false)
  const [paymentInstructions, setPaymentInstructions] = useState(null)
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [timeRemaining, setTimeRemaining] = useState(0)

  // Fetch subscription tiers
  const { data: tiers, isLoading: tiersLoading, error: tiersError } = useQuery(
    'subscription-tiers',
    subscriptionsAPI.getTiers
  )

  // Fetch current subscription and usage
  const { data: mySubscription, isLoading: subscriptionLoading, error: subscriptionError } = useQuery(
    'my-subscription',
    subscriptionsAPI.getMySubscription,
    { 
      refetchInterval: 30000,
      retry: false
    }
  )

  // Manual payment initiation mutation
  const initiatePaymentMutation = useMutation(
    (tierData) => paymentsAPI.initiateConsultationPayment(tierData),
    {
      onSuccess: (data) => {
        setPaymentInstructions(data.data);
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

  const handleSubscribe = (tier) => {
    setSelectedTier(tier)
    setIsProcessingPayment(true)
    initiatePaymentMutation.mutate({ tier_name: tier.name })
  }
  
  // Timer for payment window
  useEffect(() => {
    let timer;
    if (showPaymentModal && paymentInstructions) {
      const expiresAt = new Date(paymentInstructions.expires_at).getTime();
      timer = setInterval(() => {
        const now = new Date().getTime();
        const remaining = Math.max(0, Math.floor((expiresAt - now) / 1000));
        setTimeRemaining(remaining);
        if (remaining === 0) {
          setShowPaymentModal(false);
          setPaymentInstructions(null);
          toast.error('To\'lov vaqti tugadi. Qaytadan urinib ko\'ring.');
        }
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [showPaymentModal, paymentInstructions]);


  const getTierIcon = (tierName) => {
    const name = tierName.toLowerCase();
    if (name.includes('master') || name.includes('tier3')) return Crown;
    if (name.includes('journeyman') || name.includes('tier2')) return Star;
    if (name.includes('apprentice') || name.includes('tier1')) return Zap;
    return Sparkles;
  }

  const getTierColor = (tierName) => {
    const name = tierName.toLowerCase();
    if (name.includes('master') || name.includes('tier3')) return 'yellow-600';
    if (name.includes('journeyman') || name.includes('tier2')) return 'coffee-sienna';
    if (name.includes('apprentice') || name.includes('tier1')) return 'coffee-brown';
    return 'coffee-brown';
  }

  const formatContextLimit = (limit) => {
    if (!limit) return 'N/A';
    if (limit >= 999999) return 'Full Session History (Unlimited Tokens for Session Duration)'
    if (limit >= 32000) return `Up to ${(limit / 1000).toFixed(0)}K Tokens (Approx. 1 hour)`
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
            <span className="text-3xl font-bold text-coffee-brown">{tier.price_uzs?.toLocaleString()}</span>
            <span className="text-coffee-sienna ml-2">so'm/oy</span>
            <div className="text-sm text-coffee-sienna mt-1">
              (${tier.price_usd} USD)
            </div>
          </div>
        </div>

        <ul className="space-y-4 mb-8">
          {[
            { key: 'ai_minutes', value: tier.max_daily_ai_minutes, text: 'Daily AI Call Processing' },
            { key: 'sms', value: tier.max_daily_sms, text: 'Daily SMS Limit' },
          ].map(feature => (
            <li key={feature.key} className="flex items-start space-x-3">
              <Check size={20} className="text-green-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-medium text-coffee-brown">{feature.text}</p>
                <p className="text-sm text-coffee-sienna">
                  {feature.value >= 999999 ? 'Unlimited' : `${feature.value} per day`}
                </p>
              </div>
            </li>
          ))}
          {tier.has_agentic_functions && (
            <li className="flex items-start space-x-3">
              <Check size={20} className="text-green-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-medium text-coffee-brown">Agentic Functions Access</p>
              </div>
            </li>
          )}
          {tier.has_agentic_constructor && (
            <li className="flex items-start space-x-3">
              <Check size={20} className="text-green-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-medium text-coffee-brown">Agentic Functions Constructor</p>
              </div>
            </li>
          )}
        </ul>

        <button
          onClick={() => handleSubscribe(tier)}
          disabled={isProcessingPayment || isCurrentTier}
          className={`w-full ${
            isRecommended
              ? 'bg-yellow-400 hover:bg-yellow-500 text-yellow-900 font-bold'
              : isCurrentTier
              ? 'btn-secondary opacity-50 cursor-not-allowed'
              : 'btn-primary'
          } flex items-center justify-center space-x-2 py-3 px-6 rounded`}
        >
          {isProcessingPayment && selectedTier?.id === tier.id ? (
            <div className="loading-quill w-5 h-5"></div>
          ) : isCurrentTier ? (
            <>
              <Check size={20} />
              <span>{t('subscription', 'currentPlan')}</span>
            </>
          ) : (
            <>
              <CreditCard size={20} />
              <span>{t('subscription', 'subscribe')}</span>
            </>
          )}
        </button>
      </div>
    );
  };
  
  if (tiersLoading || subscriptionLoading) {
    return <Layout><CardSkeleton /></Layout>;
  }

  if (tiersError || subscriptionError) {
    return (
      <Layout>
        <div className="paper-panel text-center">
          <XCircle className="text-red-500 w-12 h-12 mx-auto mb-4" />
          <h2 className="heading-secondary text-red-700">Failed to load subscription data.</h2>
          <p className="text-coffee-sienna mb-4">Please try refreshing the page.</p>
          <button onClick={() => window.location.reload()} className="btn-primary">
            Refresh
          </button>
        </div>
      </Layout>
    );
  }

  const currentTierId = mySubscription?.data?.tier?.id;

  return (
    <Layout>
      <div className="space-y-8">
        <div className="text-center">
          <h1 className="heading-primary text-3xl mb-4">{t('subscription', 'title')}</h1>
          <p className="text-coffee-sienna text-lg max-w-2xl mx-auto">
            {t('subscription', 'subtitle')}
          </p>
        </div>

        {mySubscription?.data?.has_subscription && (
           <div className="paper-panel bg-coffee-green bg-opacity-10 border-2 border-coffee-green">
             <h3 className="heading-secondary">Your Current Plan</h3>
             <p>Tier: {mySubscription.data.tier.display_name}</p>
             <p>Expires: {new Date(mySubscription.data.subscription.expires_at).toLocaleDateString()}</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {tiers?.map((tier, index) => (
            <SubscriptionTierCard
              key={tier.id}
              tier={tier}
              isCurrentTier={currentTierId === tier.id}
              isRecommended={index === 1}
            />
          ))}
        </div>

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
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="modal-scroll max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="heading-secondary text-2xl">Payment Instructions</h2>
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
          <div className="text-center bg-coffee-khaki p-6 rounded-lg border-2 border-coffee-sienna">
            <h3 className="text-2xl font-bold text-coffee-brown mb-2">
              {instructions.amount_uzs?.toLocaleString()} UZS
            </h3>
            <p className="text-coffee-sienna">
              (${instructions.amount_usd}) - {instructions.tier_name}
            </p>
          </div>

          <div className="bg-coffee-beige p-6 rounded-lg border border-coffee-tan">
            <h3 className="font-bold text-coffee-brown mb-4">Bank Details:</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-coffee-sienna">Card Number:</span>
                <div className="flex items-center space-x-2">
                  <span className="font-mono font-bold text-coffee-brown">
                    {instructions.bank_details?.card_number}
                  </span>
                  <button
                    onClick={() => copyToClipboard(instructions.bank_details?.card_number)}
                    className="btn-secondary text-xs px-2 py-1"
                  >
                    Copy
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
                <span className="text-coffee-sienna">Cardholder:</span>
                <span className="font-medium text-coffee-brown">
                  {instructions.bank_details?.cardholder_name}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-yellow-50 border-2 border-yellow-400 p-4 rounded-lg">
            <h3 className="font-bold text-yellow-800 mb-2">Important! Reference Code:</h3>
            <div className="flex items-center justify-between">
              <span className="font-mono text-xl font-bold text-yellow-900">
                {instructions.reference_code}
              </span>
              <button
                onClick={() => copyToClipboard(instructions.reference_code)}
                className="bg-yellow-400 hover:bg-yellow-500 text-yellow-900 px-3 py-1 rounded font-medium"
              >
                Copy
              </button>
            </div>
            <p className="text-yellow-800 text-sm mt-2">
              Please include this code in your transfer description!
            </p>
          </div>

          <div className="flex justify-end space-x-4">
            <button
              onClick={() => {
                window.location.reload();
              }}
              className="btn-primary"
            >
              I have paid
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SubscriptionPage
