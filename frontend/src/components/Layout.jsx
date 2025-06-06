import React from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useSound } from '../hooks/useSound'
import { useTranslation, LanguageSelector } from '../hooks/useTranslation'
import SupportChat from './SupportChat'
import { 
  Home, 
  Settings, 
  BarChart3, 
  MessageSquare, 
  Workflow, 
  CreditCard,
  LogOut,
  Volume2,
  VolumeX,
  Globe
} from 'lucide-react'

const Layout = ({ children }) => {
  const { user, logout } = useAuth()
  const { soundEnabled, toggleSounds } = useSound()
  const { t } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navItems = [
    { path: '/dashboard', label: t('navigation', 'dashboard'), icon: Home },
    { path: '/invocation-editor', label: t('navigation', 'invocationEditor'), icon: Workflow },
    { path: '/sessions', label: t('navigation', 'sessions'), icon: MessageSquare },
    { path: '/statistics', label: t('navigation', 'statistics'), icon: BarChart3 },
    { path: '/subscription', label: t('navigation', 'subscription'), icon: CreditCard },
  ]

  return (
    <div className="min-h-screen bg-coffee-beige">
      {/* Navigation */}
      <nav className="nav-scribe">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4">
            <h1 className="heading-decorative text-2xl">{t('common', 'aetherium')}</h1>
            <span className="text-coffee-sienna text-sm">{t('common', 'scribe')}'s Desk</span>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`nav-link flex items-center space-x-2 ${isActive ? 'active' : ''}`}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            {/* Language Selector */}
            <div className="flex items-center space-x-2">
              <Globe size={16} className="text-coffee-sienna" />
              <LanguageSelector className="input-paper text-sm py-1 px-2" />
            </div>

            {/* Sound Toggle */}
            <button
              onClick={toggleSounds}
              className="p-2 rounded-full hover:bg-coffee-tan transition-colors"
              title={soundEnabled ? 'Disable sounds' : 'Enable sounds'}
            >
              {soundEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
            </button>

            {/* User Info */}
            <div className="text-right">
              <p className="text-sm font-medium text-coffee-brown">{user?.email}</p>
              {user?.company_number && (
                <p className="text-xs text-coffee-sienna">{user.company_number}</p>
              )}
            </div>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="p-2 rounded-full hover:bg-coffee-tan transition-colors text-coffee-brown"
              title={t('common', 'logout')}
            >
              <LogOut size={20} />
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden mt-4 flex flex-wrap gap-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link flex items-center space-x-1 text-sm ${isActive ? 'active' : ''}`}
              >
                <Icon size={16} />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {children}
      </main>

      {/* Support Chat - Available on all pages */}
      <SupportChat />
    </div>
  )
}

export default Layout