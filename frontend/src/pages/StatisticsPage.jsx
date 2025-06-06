import React, { useState } from 'react'
import { useQuery } from 'react-query'
import Layout from '../components/Layout'
import { statisticsAPI } from '../services/api'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import {
  TrendingUp,
  TrendingDown,
  Calendar,
  Clock,
  Phone,
  MessageSquare,
  Target,
  Activity
} from 'lucide-react'

const StatisticsPage = () => {
  const [selectedPeriod, setSelectedPeriod] = useState(30)

  // Fetch statistics data
  const { data: dailyStats, isLoading: dailyLoading } = useQuery(
    ['daily-stats', selectedPeriod],
    () => statisticsAPI.getDaily(selectedPeriod)
  )

  const { data: trends, isLoading: trendsLoading } = useQuery(
    'trends',
    () => statisticsAPI.getTrends(7)
  )

  const { data: hourlyDistribution, isLoading: hourlyLoading } = useQuery(
    'hourly-distribution',
    () => statisticsAPI.getHourlyDistribution(7)
  )

  const { data: outcomeAnalysis, isLoading: outcomeLoading } = useQuery(
    'outcome-analysis',
    () => statisticsAPI.getOutcomeAnalysis(30)
  )

  const isLoading = dailyLoading || trendsLoading || hourlyLoading || outcomeLoading

  // Chart colors matching coffee theme
  const chartColors = {
    primary: '#8B4513',
    secondary: '#D2B48C',
    accent: '#A0522D',
    success: '#8FBC8F',
    warning: '#F0E68C',
    danger: '#CD853F'
  }

  // Format data for charts
  const formatDailyData = (data) => {
    return data?.map(item => ({
      date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      calls: item.total_calls,
      duration: Math.round(item.total_duration_seconds / 60), // Convert to minutes
      positive: item.positive_interactions,
      negative: item.negative_interactions,
      successRate: item.total_calls > 0 ? (item.positive_interactions / item.total_calls * 100) : 0
    })) || []
  }

  const formatHourlyData = (data) => {
    return data?.hourly_distribution?.map(item => ({
      hour: `${item.hour}:00`,
      calls: item.call_count,
      avgDuration: item.average_duration
    })) || []
  }

  const formatOutcomeData = (data) => {
    if (!data?.outcome_analysis) return []
    
    const outcomes = []
    Object.entries(data.outcome_analysis).forEach(([outcome, types]) => {
      Object.entries(types).forEach(([type, stats]) => {
        outcomes.push({
          name: `${outcome} (${type})`,
          value: stats.count,
          outcome,
          type
        })
      })
    })
    return outcomes
  }

  const TrendCard = ({ title, current, previous, icon: Icon, format = (val) => val }) => {
    const change = previous > 0 ? ((current - previous) / previous * 100) : 0
    const isPositive = change >= 0

    return (
      <div className="card-paper">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-coffee-khaki rounded-full">
              <Icon size={20} className="text-coffee-brown" />
            </div>
            <h3 className="font-medium text-coffee-brown">{title}</h3>
          </div>
          <div className={`flex items-center space-x-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {isPositive ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            <span className="text-sm font-medium">{Math.abs(change).toFixed(1)}%</span>
          </div>
        </div>
        
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-coffee-sienna">Current Period</span>
            <span className="font-semibold text-coffee-brown">{format(current)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-coffee-sienna">Previous Period</span>
            <span className="text-coffee-brown">{format(previous)}</span>
          </div>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="loading-quill mb-4"></div>
            <p className="text-coffee-brown">The Scribe is analyzing the data...</p>
          </div>
        </div>
      </Layout>
    )
  }

  const dailyData = formatDailyData(dailyStats)
  const hourlyData = formatHourlyData(hourlyDistribution)
  const outcomeData = formatOutcomeData(outcomeAnalysis)

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="heading-primary">The Scribe's Analytics</h1>
            <p className="text-coffee-sienna">
              Deep insights into your AI communication performance
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <label className="text-coffee-brown font-medium">Period:</label>
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(Number(e.target.value))}
              className="input-paper"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
          </div>
        </div>

        {/* Trend Cards */}
        {trends && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <TrendCard
              title="Total Calls"
              current={trends.current_period.calls}
              previous={trends.previous_period.calls}
              icon={Phone}
            />
            <TrendCard
              title="Positive Interactions"
              current={trends.current_period.positive_interactions}
              previous={trends.previous_period.positive_interactions}
              icon={Target}
            />
            <TrendCard
              title="Total Duration"
              current={trends.current_period.total_duration}
              previous={trends.previous_period.total_duration}
              icon={Clock}
              format={(val) => `${Math.round(val / 60)}m`}
            />
          </div>
        )}

        {/* Daily Performance Chart */}
        <div className="paper-panel">
          <h2 className="heading-secondary mb-4">Daily Performance Trends</h2>
          <div className="chart-paper h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dailyData}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartColors.secondary} />
                <XAxis 
                  dataKey="date" 
                  stroke={chartColors.primary}
                  fontSize={12}
                />
                <YAxis stroke={chartColors.primary} fontSize={12} />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#F5F5DC',
                    border: `1px solid ${chartColors.secondary}`,
                    borderRadius: '4px'
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="calls" 
                  stroke={chartColors.primary} 
                  strokeWidth={2}
                  name="Total Calls"
                />
                <Line 
                  type="monotone" 
                  dataKey="positive" 
                  stroke={chartColors.success} 
                  strokeWidth={2}
                  name="Positive Interactions"
                />
                <Line 
                  type="monotone" 
                  dataKey="successRate" 
                  stroke={chartColors.accent} 
                  strokeWidth={2}
                  name="Success Rate (%)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Hourly Distribution and Outcome Analysis */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Hourly Distribution */}
          <div className="paper-panel">
            <h2 className="heading-secondary mb-4">Hourly Activity Distribution</h2>
            <div className="chart-paper h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={chartColors.secondary} />
                  <XAxis 
                    dataKey="hour" 
                    stroke={chartColors.primary}
                    fontSize={10}
                  />
                  <YAxis stroke={chartColors.primary} fontSize={12} />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: '#F5F5DC',
                      border: `1px solid ${chartColors.secondary}`,
                      borderRadius: '4px'
                    }}
                  />
                  <Bar 
                    dataKey="calls" 
                    fill={chartColors.primary}
                    name="Calls"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Outcome Analysis */}
          <div className="paper-panel">
            <h2 className="heading-secondary mb-4">Outcome Distribution</h2>
            <div className="chart-paper h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={outcomeData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {outcomeData.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={entry.outcome === 'positive' ? chartColors.success : chartColors.danger} 
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Duration Analysis */}
        <div className="paper-panel">
          <h2 className="heading-secondary mb-4">Call Duration Analysis</h2>
          <div className="chart-paper h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={dailyData}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartColors.secondary} />
                <XAxis 
                  dataKey="date" 
                  stroke={chartColors.primary}
                  fontSize={12}
                />
                <YAxis stroke={chartColors.primary} fontSize={12} />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#F5F5DC',
                    border: `1px solid ${chartColors.secondary}`,
                    borderRadius: '4px'
                  }}
                  formatter={(value, name) => [
                    name === 'duration' ? `${value} minutes` : value,
                    name === 'duration' ? 'Total Duration' : name
                  ]}
                />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="duration" 
                  stroke={chartColors.accent} 
                  fill={chartColors.secondary}
                  fillOpacity={0.6}
                  name="Duration (minutes)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Performance Insights */}
        <div className="paper-panel coffee-stain">
          <h2 className="heading-secondary mb-4">Performance Insights</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <Activity className="mx-auto mb-2 text-coffee-brown" size={32} />
              <h3 className="font-semibold text-coffee-brown">Peak Hours</h3>
              <p className="text-sm text-coffee-sienna">
                {hourlyData.length > 0 && 
                  hourlyData.reduce((max, curr) => curr.calls > max.calls ? curr : max, hourlyData[0])?.hour
                }
              </p>
            </div>
            
            <div className="text-center">
              <Target className="mx-auto mb-2 text-coffee-brown" size={32} />
              <h3 className="font-semibold text-coffee-brown">Success Rate</h3>
              <p className="text-sm text-coffee-sienna">
                {dailyData.length > 0 && 
                  (dailyData.reduce((sum, day) => sum + day.successRate, 0) / dailyData.length).toFixed(1)
                }%
              </p>
            </div>
            
            <div className="text-center">
              <Clock className="mx-auto mb-2 text-coffee-brown" size={32} />
              <h3 className="font-semibold text-coffee-brown">Avg Duration</h3>
              <p className="text-sm text-coffee-sienna">
                {dailyData.length > 0 && 
                  Math.round(dailyData.reduce((sum, day) => sum + day.duration, 0) / dailyData.length)
                }m
              </p>
            </div>
            
            <div className="text-center">
              <MessageSquare className="mx-auto mb-2 text-coffee-brown" size={32} />
              <h3 className="font-semibold text-coffee-brown">Total Sessions</h3>
              <p className="text-sm text-coffee-sienna">
                {dailyData.reduce((sum, day) => sum + day.calls, 0).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default StatisticsPage