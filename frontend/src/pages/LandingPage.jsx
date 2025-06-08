import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation, LanguageSelector } from '../hooks/useTranslation'
import { landingAPI } from '../services/landingAPI'
import { 
  Phone, 
  MessageSquare, 
  BarChart3, 
  Shield, 
  Clock, 
  Globe, 
  CheckCircle, 
  Star,
  Zap,
  Users,
  Headphones,
  Settings,
  CreditCard,
  ArrowRight,
  Smartphone,
  TrendingUp,
  Award
} from 'lucide-react'

const LandingPage = () => {
  const { t } = useTranslation()
  const [landingData, setLandingData] = useState(null)
  const [publicStats, setPublicStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchLandingData = async () => {
      try {
        const [landingInfo, stats] = await Promise.all([
          landingAPI.getLandingInfo(),
          landingAPI.getPublicStats()
        ])
        setLandingData(landingInfo)
        setPublicStats(stats)
      } catch (error) {
        console.error('Error fetching landing data:', error)
        // Use fallback data if API fails
      } finally {
        setLoading(false)
      }
    }

    fetchLandingData()
  }, [])

  // Icon mapping for dynamic features
  const iconMap = {
    'phone': <Phone className="w-8 h-8" />,
    'message-square': <MessageSquare className="w-8 h-8" />,
    'bar-chart-3': <BarChart3 className="w-8 h-8" />,
    'globe': <Globe className="w-8 h-8" />,
    'shield': <Shield className="w-8 h-8" />,
    'settings': <Settings className="w-8 h-8" />
  }

  // Fallback features if API fails
  const fallbackFeatures = [
    {
      icon: <Phone className="w-8 h-8" />,
      title: "AI-Powered Call Center",
      description: "Advanced AI handles customer calls with natural conversation flow and intelligent responses."
    },
    {
      icon: <MessageSquare className="w-8 h-8" />,
      title: "SMS Verification System",
      description: "Secure SMS-based authentication with real GSM module integration and demo mode support."
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Real-time Analytics",
      description: "Comprehensive statistics and insights into call performance, customer satisfaction, and system metrics."
    },
    {
      icon: <Globe className="w-8 h-8" />,
      title: "Multi-language Support",
      description: "Support for multiple languages with seamless translation capabilities for global reach."
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Enterprise Security",
      description: "Bank-grade security with encrypted communications and secure payment processing."
    },
    {
      icon: <Settings className="w-8 h-8" />,
      title: "GSM Module Management",
      description: "Complete management of company GSM modules with bank card integration for payments."
    }
  ]

  // Get features from API or use fallback
  const features = landingData?.features?.map(feature => ({
    ...feature,
    icon: iconMap[feature.icon] || <Settings className="w-8 h-8" />
  })) || fallbackFeatures

  // Get pricing from API or use fallback
  const pricingPlans = landingData?.pricing_plans || [
    {
      name: "Starter",
      price: "$29",
      period: "/month",
      description: "Perfect for small businesses getting started",
      features: [
        "Up to 100 calls/month",
        "Basic SMS verification",
        "Standard AI responses",
        "Email support",
        "Basic analytics"
      ],
      popular: false,
      color: "coffee-tan"
    },
    {
      name: "Professional",
      price: "$99",
      period: "/month",
      description: "Ideal for growing businesses",
      features: [
        "Up to 1,000 calls/month",
        "Advanced SMS verification",
        "Custom AI training",
        "Priority support",
        "Advanced analytics",
        "Multi-language support",
        "GSM module integration"
      ],
      popular: true,
      color: "coffee-sienna"
    },
    {
      name: "Enterprise",
      price: "$299",
      period: "/month",
      description: "For large organizations",
      features: [
        "Unlimited calls",
        "Enterprise SMS system",
        "Custom AI personalities",
        "24/7 dedicated support",
        "Real-time analytics",
        "Full GSM management",
        "Custom integrations",
        "White-label solution"
      ],
      popular: false,
      color: "coffee-brown"
    }
  ]

  if (loading) {
    return (
      <div className="min-h-screen bg-coffee-beige flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-coffee-tan border-t-coffee-sienna rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-coffee-brown">Loading Aetherium...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-coffee-beige">
      {/* Header */}
      <header className="relative">
        <div className="container mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-coffee-brown rounded-lg flex items-center justify-center">
                <Phone className="w-6 h-6 text-coffee-beige" />
              </div>
              <h1 className="heading-decorative text-2xl">Aetherium</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Globe size={16} className="text-coffee-sienna" />
                <LanguageSelector className="input-paper text-sm py-1 px-2" />
              </div>
              <Link 
                to="/login" 
                className="btn-secondary text-sm px-4 py-2"
              >
                Login
              </Link>
              <Link 
                to="/register" 
                className="btn-primary text-sm px-4 py-2"
              >
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center">
          <h1 className="heading-decorative text-5xl md:text-6xl mb-6">
            The Future of
            <span className="text-coffee-sienna"> AI Communication</span>
          </h1>
          <p className="text-xl text-coffee-brown mb-8 max-w-3xl mx-auto">
            Transform your customer service with our advanced AI-powered call center system. 
            Handle thousands of calls simultaneously with natural conversation flow and intelligent responses.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link 
              to="/register" 
              className="btn-primary text-lg px-8 py-4 inline-flex items-center space-x-2"
            >
              <span>Start Free Trial</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link 
              to="/login" 
              className="btn-secondary text-lg px-8 py-4"
            >
              Watch Demo
            </Link>
          </div>

          {/* Stats Section */}
          {publicStats && (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 max-w-4xl mx-auto">
              <div className="text-center">
                <div className="text-3xl font-bold text-coffee-sienna mb-1">
                  {(publicStats.total_calls_handled / 1000000).toFixed(1)}M+
                </div>
                <div className="text-sm text-coffee-brown">Calls Handled</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-coffee-sienna mb-1">
                  {publicStats.active_customers?.toLocaleString()}+
                </div>
                <div className="text-sm text-coffee-brown">Active Customers</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-coffee-sienna mb-1">
                  {publicStats.countries_served}+
                </div>
                <div className="text-sm text-coffee-brown">Countries</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-coffee-sienna mb-1">
                  {publicStats.uptime_percentage}%
                </div>
                <div className="text-sm text-coffee-brown">Uptime</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-coffee-sienna mb-1">
                  {publicStats.average_response_time}
                </div>
                <div className="text-sm text-coffee-brown">Response Time</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-coffee-sienna mb-1 flex items-center justify-center">
                  {publicStats.customer_satisfaction}
                  <Star className="w-4 h-4 ml-1 text-yellow-500 fill-current" />
                </div>
                <div className="text-sm text-coffee-brown">Satisfaction</div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-gradient-to-b from-coffee-beige to-coffee-khaki">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="heading-primary text-4xl mb-4">Powerful Features</h2>
            <p className="text-lg text-coffee-brown max-w-2xl mx-auto">
              Everything you need to revolutionize your customer communication
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="paper-panel hover:shadow-lg transition-shadow">
                <div className="text-coffee-sienna mb-4">
                  {feature.icon}
                </div>
                <h3 className="heading-secondary text-xl mb-3">{feature.title}</h3>
                <p className="text-coffee-brown">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="heading-primary text-4xl mb-4">Simple, Transparent Pricing</h2>
            <p className="text-lg text-coffee-brown max-w-2xl mx-auto">
              Choose the perfect plan for your business needs. All plans include SMS verification and core AI features.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {pricingPlans.map((plan, index) => (
              <div 
                key={index} 
                className={`paper-panel relative ${plan.popular ? 'ring-2 ring-coffee-sienna' : ''} hover:shadow-xl transition-shadow`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className="bg-coffee-sienna text-coffee-beige px-4 py-1 rounded-full text-sm font-medium flex items-center space-x-1">
                      <Star className="w-4 h-4" />
                      <span>Most Popular</span>
                    </div>
                  </div>
                )}
                
                <div className="text-center mb-6">
                  <h3 className="heading-secondary text-2xl mb-2">{plan.name}</h3>
                  <div className="flex items-baseline justify-center mb-2">
                    <span className="text-4xl font-bold text-coffee-brown">{plan.price}</span>
                    <span className="text-coffee-sienna ml-1">{plan.period}</span>
                  </div>
                  <p className="text-coffee-brown">{plan.description}</p>
                </div>
                
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center space-x-3">
                      <CheckCircle className="w-5 h-5 text-coffee-green flex-shrink-0" />
                      <span className="text-coffee-brown">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Link 
                  to="/register" 
                  className={`btn-${plan.popular ? 'primary' : 'secondary'} w-full text-center py-3`}
                >
                  Get Started
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-coffee-brown text-coffee-beige">
        <div className="container mx-auto text-center">
          <h2 className="heading-decorative text-4xl mb-6">
            Ready to Transform Your Customer Service?
          </h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto opacity-90">
            Join thousands of businesses already using Aetherium to provide exceptional customer experiences.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              to="/register" 
              className="bg-coffee-beige text-coffee-brown px-8 py-4 rounded-lg font-medium hover:bg-coffee-khaki transition-colors inline-flex items-center space-x-2"
            >
              <span>Start Your Free Trial</span>
              <Zap className="w-5 h-5" />
            </Link>
            <Link 
              to="/login" 
              className="border-2 border-coffee-beige text-coffee-beige px-8 py-4 rounded-lg font-medium hover:bg-coffee-beige hover:text-coffee-brown transition-colors"
            >
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 bg-coffee-sienna text-coffee-beige">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-coffee-beige rounded-lg flex items-center justify-center">
                  <Phone className="w-5 h-5 text-coffee-brown" />
                </div>
                <h3 className="heading-decorative text-xl">Aetherium</h3>
              </div>
              <p className="opacity-90">
                Advanced AI Communication System for the modern business.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 opacity-90">
                <li><a href="#" className="hover:opacity-100 transition-opacity">Features</a></li>
                <li><a href="#" className="hover:opacity-100 transition-opacity">Pricing</a></li>
                <li><a href="#" className="hover:opacity-100 transition-opacity">API</a></li>
                <li><a href="#" className="hover:opacity-100 transition-opacity">Documentation</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 opacity-90">
                <li><a href="#" className="hover:opacity-100 transition-opacity">About</a></li>
                <li><a href="#" className="hover:opacity-100 transition-opacity">Blog</a></li>
                <li><a href="#" className="hover:opacity-100 transition-opacity">Careers</a></li>
                <li><a href="#" className="hover:opacity-100 transition-opacity">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 opacity-90">
                <li><a href="#" className="hover:opacity-100 transition-opacity">Help Center</a></li>
                <li><a href="#" className="hover:opacity-100 transition-opacity">Community</a></li>
                <li><a href="#" className="hover:opacity-100 transition-opacity">Status</a></li>
                <li><a href="#" className="hover:opacity-100 transition-opacity">Privacy</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-coffee-brown mt-8 pt-8 text-center opacity-75">
            <p>&copy; 2025 Aetherium. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage