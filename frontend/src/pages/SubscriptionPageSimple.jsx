import React from 'react'
import Layout from '../components/Layout'

const SubscriptionPageSimple = () => {
  return (
    <Layout>
      <div className="space-y-8">
        <div className="text-center">
          <h1 className="heading-primary text-3xl mb-4">Subscription Plans</h1>
          <p className="text-coffee-sienna text-lg max-w-2xl mx-auto">
            Choose the perfect plan for your AI call center needs
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Apprentice Tier */}
          <div className="paper-panel">
            <div className="text-center mb-6">
              <h3 className="heading-secondary text-xl mb-2">Apprentice</h3>
              <div className="mb-4">
                <span className="text-3xl font-bold text-coffee-brown">250,000</span>
                <span className="text-coffee-sienna ml-2">so'm/oy</span>
                <div className="text-sm text-coffee-sienna mt-1">
                  ($20 USD)
                </div>
              </div>
            </div>
            
            <div className="space-y-3 mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-coffee-green rounded-full"></div>
                <span className="text-coffee-brown">240 minutes AI processing daily</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-coffee-green rounded-full"></div>
                <span className="text-coffee-brown">100 SMS messages daily</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-coffee-green rounded-full"></div>
                <span className="text-coffee-brown">Agentic functions access</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-coffee-green rounded-full"></div>
                <span className="text-coffee-brown">Agentic constructor tab</span>
              </div>
            </div>
            
            <button className="btn-primary w-full">
              Choose Plan
            </button>
          </div>

          {/* Journeyman Tier */}
          <div className="paper-panel border-4 border-yellow-400">
            <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
              <span className="bg-yellow-400 text-yellow-900 px-4 py-1 rounded-full text-sm font-bold">
                Most Popular
              </span>
            </div>
            
            <div className="text-center mb-6">
              <h3 className="heading-secondary text-xl mb-2">Journeyman</h3>
              <div className="mb-4">
                <span className="text-3xl font-bold text-coffee-brown">750,000</span>
                <span className="text-coffee-sienna ml-2">so'm/oy</span>
                <div className="text-sm text-coffee-sienna mt-1">
                  ($50 USD)
                </div>
              </div>
            </div>
            
            <div className="space-y-3 mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-coffee-green rounded-full"></div>
                <span className="text-coffee-brown">480 minutes AI processing daily</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-coffee-green rounded-full"></div>
                <span className="text-coffee-brown">300 SMS messages daily</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-coffee-green rounded-full"></div>
                <span className="text-coffee-brown">All Apprentice features</span>
              </div>
            </div>
            
            <button className="btn-primary w-full">
              Choose Plan
            </button>
          </div>

          {/* Master Scribe Tier */}
          <div className="paper-panel">
            <div className="text-center mb-6">
              <h3 className="heading-secondary text-xl mb-2">Master Scribe</h3>
              <div className="mb-4">
                <span className="text-3xl font-bold text-coffee-brown">1,250,000</span>
                <span className="text-coffee-sienna ml-2">so'm/oy</span>
                <div className="text-sm text-coffee-sienna mt-1">
                  ($100 USD)
                </div>
              </div>
            </div>
            
            <div className="space-y-3 mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-coffee-green rounded-full"></div>
                <span className="text-coffee-brown">Unlimited AI processing</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-coffee-green rounded-full"></div>
                <span className="text-coffee-brown">Unlimited SMS messages</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-coffee-green rounded-full"></div>
                <span className="text-coffee-brown">All Journeyman features</span>
              </div>
            </div>
            
            <button className="btn-primary w-full">
              Choose Plan
            </button>
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default SubscriptionPageSimple