import React, { useState, useEffect } from 'react'
import { useQuery } from 'react-query'
import Layout from '../components/Layout'
import { statisticsAPI, sessionsAPI } from '../services/api'
import { useSound } from '../hooks/useSound'
import { useTranslation, LanguageSelector } from '../hooks/useTranslation'
import { 
  Phone, 
  MessageSquare, 
  TrendingUp, 
  TrendingDown, 
  Clock, 
  Users,
  Activity,
  BarChart3
} from 'lucide-react'

const DashboardPage = () => {
  const { playBellDing } = useSound()
  const { t, formatTime } = useTranslation()
  const [lastUpdateTime, setLastUpdateTime] = useState(new Date())

  // Fetch dashboard statistics
  const { data: stats, isLoading: statsLoading, refetch: refetchStats } = useQuery(
    'dashboard-stats',
    statisticsAPI.getDashboard,
    {
      refetchInterval: 30000, // Refresh every 30 seconds
      onSuccess: () => {
        setLastUpdateTime(new Date())
        playBellDing()
      }
    }
  )

  // Fetch active sessions
  const { data: activeSessions, isLoading: sessionsLoading } = useQuery(
    'active-sessions',
    sessionsAPI.getActiveCount,
    {
      refetchInterval: 10000, // Refresh every 10 seconds
    }
  )

  // Fetch recent summary
  const { data: recentSummary, isLoading: summaryLoading } = useQuery(
    'recent-summary',
    () => sessionsAPI.getRecentSummary(24),
    {
      refetchInterval: 60000, // Refresh every minute
    }
  )

  const StatCard = ({ title, value, subtitle, icon: Icon, trend, trendValue, color = "coffee-brown" }) => (
    <div className="card-paper">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-full bg-coffee-khaki border-2 border-${color}`}>
          <Icon size={24} className={`text-${color}`} />
        </div>
        {trend && (
          <div className={`flex items-center space-x-1 ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
            {trend === 'up' ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            <span className="text-sm font-medium">{trendValue}%</span>
          </div>
        )}
      </div>
      
      <div>
        <h3 className="text-2xl font-bold text-coffee-brown mb-1">{value}</h3>
        <p className="text-coffee-sienna font-medium">{title}</p>
        {subtitle && (
          <p className="text-coffee-brown text-sm mt-1">{subtitle}</p>
        )}
      </div>
    </div>
  )

  const formatDuration = (seconds) => {
    return formatTime(seconds)
  }

  const formatPercentage = (value) => {
    return `${value.toFixed(1)}%`
  }

  if (statsLoading || sessionsLoading || summaryLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="loading-quill mb-4"></div>
            <p className="text-coffee-brown">{t('dashboard', 'loadingInsights')}</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="heading-primary">{t('dashboard', 'title')}</h1>
            <p className="text-coffee-sienna">
              {t('dashboard', 'subtitle')}
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <LanguageSelector />
            <div className="text-right">
              <p className="text-sm text-coffee-brown">{t('dashboard', 'lastUpdated')}</p>
              <p className="text-sm text-coffee-sienna">{lastUpdateTime.toLocaleTimeString()}</p>
            </div>
          </div>
        </div>

        {/* Active Sessions Alert */}
        {activeSessions?.active_count > 0 && (
          <div className="bg-coffee-green bg-opacity-20 border-2 border-coffee-green rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <Activity className="text-coffee-green animate-pulse" size={24} />
              <div>
                <h3 className="font-semibold text-coffee-brown">
                  {activeSessions.active_count} {t('dashboard', 'activeSessions')}
                </h3>
                <p className="text-coffee-sienna text-sm">
                  {t('dashboard', 'activeSessionsDesc')}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Main Statistics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title={t('dashboard', 'totalCalls')}
            value={stats?.total_calls?.toLocaleString() || '0'}
            subtitle={t('dashboard', 'allTimeConversations')}
            icon={Phone}
            color="coffee-brown"
          />
          
          <StatCard
            title={t('dashboard', 'totalDuration')}
            value={formatDuration(stats?.total_duration_seconds || 0)}
            subtitle={t('dashboard', 'cumulativeTalkTime')}
            icon={Clock}
            color="coffee-sienna"
          />
          
          <StatCard
            title={t('dashboard', 'positiveInteractions')}
            value={formatPercentage(stats?.positive_percentage || 0)}
            subtitle={`${stats?.positive_interactions || 0} ${t('dashboard', 'successfulOutcomes')}`}
            icon={TrendingUp}
            trend="up"
            trendValue={stats?.positive_percentage || 0}
            color="green-600"
          />
          
          <StatCard
            title={t('dashboard', 'averageCallDuration')}
            value={`${(stats?.average_call_duration || 0).toFixed(1)}s`}
            subtitle={t('dashboard', 'perConversation')}
            icon={BarChart3}
            color="coffee-brown"
          />
        </div>

        {/* Recent Activity Summary */}
        {recentSummary && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 24-Hour Summary */}
            <div className="paper-panel">
              <h2 className="heading-secondary mb-4">{t('dashboard', 'last24Hours')}</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-coffee-brown">{t('dashboard', 'sessions')}</span>
                  <span className="font-semibold text-coffee-brown">
                    {recentSummary.total_sessions}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-coffee-brown">{t('dashboard', 'successRate')}</span>
                  <span className="font-semibold text-green-600">
                    {recentSummary.success_rate.toFixed(1)}%
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-coffee-brown">{t('dashboard', 'totalDuration')}</span>
                  <span className="font-semibold text-coffee-brown">
                    {formatDuration(recentSummary.total_duration_seconds)}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-coffee-brown">{t('dashboard', 'avgDuration')}</span>
                  <span className="font-semibold text-coffee-brown">
                    {recentSummary.average_duration_seconds}s
                  </span>
                </div>
              </div>
            </div>

            {/* Session Types Breakdown */}
            <div className="paper-panel">
              <h2 className="heading-secondary mb-4">{t('dashboard', 'sessionTypes')}</h2>
              <div className="space-y-3">
                {Object.entries(recentSummary.sessions_by_type || {}).map(([type, count]) => (
                  <div key={type} className="flex justify-between items-center">
                    <div className="flex items-center space-x-2">
                      {type === 'voice' && <Phone size={16} className="text-coffee-brown" />}
                      {type === 'sms' && <MessageSquare size={16} className="text-coffee-brown" />}
                      {type === 'telegram' && <Users size={16} className="text-coffee-brown" />}
                      <span className="text-coffee-brown capitalize">{t('dashboard', type)}</span>
                    </div>
                    <span className="font-semibold text-coffee-brown">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="paper-panel">
          <h2 className="heading-secondary mb-4">{t('dashboard', 'quickActions')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => window.location.href = '/invocation-editor'}
              className="btn-primary flex items-center justify-center space-x-2"
            >
              <Activity size={20} />
              <span>{t('dashboard', 'editWorkflows')}</span>
            </button>
            
            <button
              onClick={() => window.location.href = '/sessions'}
              className="btn-secondary flex items-center justify-center space-x-2"
            >
              <MessageSquare size={20} />
              <span>{t('dashboard', 'viewSessions')}</span>
            </button>
            
            <button
              onClick={() => window.location.href = '/statistics'}
              className="btn-secondary flex items-center justify-center space-x-2"
            >
              <BarChart3 size={20} />
              <span>{t('dashboard', 'detailedAnalytics')}</span>
            </button>
          </div>
        </div>

        {/* System Status */}
        <div className="paper-panel coffee-stain">
          <h2 className="heading-secondary mb-4">{t('dashboard', 'systemStatus')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mx-auto mb-2"></div>
              <p className="text-sm text-coffee-brown font-medium">{t('dashboard', 'aiScribe')}</p>
              <p className="text-xs text-coffee-sienna">{t('dashboard', 'online')}</p>
            </div>
            
            <div className="text-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mx-auto mb-2"></div>
              <p className="text-sm text-coffee-brown font-medium">{t('dashboard', 'voiceSystem')}</p>
              <p className="text-xs text-coffee-sienna">{t('dashboard', 'ready')}</p>
            </div>
            
            <div className="text-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mx-auto mb-2"></div>
              <p className="text-sm text-coffee-brown font-medium">{t('dashboard', 'messaging')}</p>
              <p className="text-xs text-coffee-sienna">{t('dashboard', 'active')}</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default DashboardPage