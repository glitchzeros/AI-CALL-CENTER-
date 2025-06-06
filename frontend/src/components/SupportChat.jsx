/**
 * Support Chat Component
 * Gemini-powered support chat system
 */

import React, { useState, useRef, useEffect } from 'react'
import { useTranslation } from '../hooks/useTranslation'
import { MessageCircle, X, Send, Bot, User, Minimize2, Maximize2 } from 'lucide-react'

const SupportChat = () => {
  const { t } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // System prompt for Gemini about Aetherium project
  const systemPrompt = `You are a helpful support assistant for Aetherium, an AI call center platform. Here's what you need to know about the platform:

ABOUT AETHERIUM:
- Aetherium is an AI communication platform that deploys autonomous agents called "Scribes"
- Scribes can conduct natural, context-aware conversations across multiple channels (voice, SMS, Telegram)
- The platform uses Google's Gemini 2.0 Flashlight model for AI processing
- It features a unique "coffee paper" aesthetic theme called "The Scribe's Desk"

KEY FEATURES:
- Visual workflow builder called "Invocation Editor" for creating automated behaviors
- Multi-channel communication (voice calls via GSM modems, SMS, Telegram)
- Real-time statistics and call history
- Subscription tiers with different context memory limits:
  * Apprentice ($20): 4,000 tokens (~5 minutes)
  * Journeyman ($50): 32,000 tokens (~1 hour)  
  * Master Scribe ($100): Unlimited tokens for session duration
- Manual payment system with bank transfers
- Multi-language support (English, Uzbek, Russian)

TECHNICAL DETAILS:
- Uses SIM800C modems with dual USB connections
- Supports 40 concurrent voice calls
- Integrates with Microsoft Edge TTS for voice synthesis
- Click API for payment processing
- Manual translation system (no automated translation)

INVOCATION TYPES:
- Payment Ritual: Handles manual payment flows
- The Messenger: Sends SMS messages
- Telegram Channeler: Telegram bot integration
- The Final Word: Hangs up calls
- The Scribe's Reply: Gets AI responses

HELP TOPICS YOU CAN ASSIST WITH:
- Account setup and registration
- Subscription plans and pricing
- How to use the Invocation Editor
- Understanding statistics and call history
- Payment processes and bank transfers
- Multi-language features
- Technical troubleshooting
- Platform capabilities and limitations

Always be helpful, professional, and maintain the thematic language of "The Scribe" when appropriate. If you don't know something specific, acknowledge it and suggest contacting technical support.`

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (isOpen && !isMinimized && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen, isMinimized])

  // Initialize chat with welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          id: 1,
          type: 'bot',
          content: t('support', 'welcome'),
          timestamp: new Date()
        }
      ])
    }
  }, [isOpen, messages.length, t])

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // Simulate API call to Gemini
      // In real implementation, this would call your backend API
      // which then calls Gemini with the system prompt and conversation history
      
      const response = await fetch('/api/support/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          message: inputMessage.trim(),
          language: language
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.response || t('support', 'error'),
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Support chat error:', error)
      
      // Fallback response for demo purposes
      const fallbackMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: t('support', 'error'),
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, fallbackMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsOpen(true)}
          className="bg-coffee-sienna hover:bg-coffee-brown text-coffee-beige p-4 rounded-full shadow-lg transition-all duration-300 hover:scale-110"
          title={t('support', 'helpButton')}
        >
          <MessageCircle size={24} />
        </button>
      </div>
    )
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <div className={`bg-coffee-beige border-2 border-coffee-sienna rounded-lg shadow-xl transition-all duration-300 ${
        isMinimized ? 'w-80 h-16' : 'w-96 h-96'
      }`}>
        {/* Header */}
        <div className="bg-coffee-sienna text-coffee-beige p-4 rounded-t-lg flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bot size={20} />
            <span className="font-semibold">{t('support', 'chatTitle')}</span>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="hover:bg-coffee-brown p-1 rounded transition-colors"
            >
              {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="hover:bg-coffee-brown p-1 rounded transition-colors"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            {/* Messages */}
            <div className="h-64 overflow-y-auto p-4 space-y-3">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-xs lg:max-w-md px-3 py-2 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-coffee-sienna text-coffee-beige'
                      : 'bg-coffee-khaki text-coffee-brown border border-coffee-tan'
                  }`}>
                    <div className="flex items-start space-x-2">
                      {message.type === 'bot' && <Bot size={16} className="mt-1 flex-shrink-0" />}
                      {message.type === 'user' && <User size={16} className="mt-1 flex-shrink-0" />}
                      <div className="flex-1">
                        <p className="text-sm">{message.content}</p>
                        <p className={`text-xs mt-1 ${
                          message.type === 'user' ? 'text-coffee-khaki' : 'text-coffee-sienna'
                        }`}>
                          {formatTime(message.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-coffee-khaki text-coffee-brown border border-coffee-tan px-3 py-2 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <Bot size={16} />
                      <div className="loading-quill w-4 h-4"></div>
                      <span className="text-sm">{t('support', 'typing')}</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-coffee-tan p-4">
              <div className="flex space-x-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={t('support', 'placeholder')}
                  className="flex-1 input-paper text-sm"
                  disabled={isLoading}
                />
                <button
                  onClick={sendMessage}
                  disabled={!inputMessage.trim() || isLoading}
                  className="btn-primary p-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send size={16} />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default SupportChat