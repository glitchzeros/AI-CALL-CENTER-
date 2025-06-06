import React, { useState } from 'react'
import { useQuery } from 'react-query'
import Layout from '../components/Layout'
import { sessionsAPI } from '../services/api'
import { 
  Phone, 
  MessageSquare, 
  Send, 
  Clock, 
  User, 
  Calendar,
  ChevronDown,
  ChevronRight,
  Filter,
  Search,
  Download
} from 'lucide-react'
import { format } from 'date-fns'

const SessionsPage = () => {
  const [selectedSession, setSelectedSession] = useState(null)
  const [expandedSessions, setExpandedSessions] = useState(new Set())
  const [filters, setFilters] = useState({
    session_type: '',
    status: '',
    search: ''
  })
  const [pagination, setPagination] = useState({
    limit: 20,
    offset: 0
  })

  // Fetch sessions
  const { data: sessions, isLoading, refetch } = useQuery(
    ['sessions', filters, pagination],
    () => sessionsAPI.getSessions({
      ...filters,
      ...pagination
    }),
    {
      keepPreviousData: true
    }
  )

  // Fetch session detail when selected
  const { data: sessionDetail, isLoading: detailLoading } = useQuery(
    ['session-detail', selectedSession?.id],
    () => sessionsAPI.getSession(selectedSession.id),
    {
      enabled: !!selectedSession
    }
  )

  const handleSessionClick = (session) => {
    setSelectedSession(session)
  }

  const toggleSessionExpansion = (sessionId) => {
    const newExpanded = new Set(expandedSessions)
    if (newExpanded.has(sessionId)) {
      newExpanded.delete(sessionId)
    } else {
      newExpanded.add(sessionId)
    }
    setExpandedSessions(newExpanded)
  }

  const getSessionIcon = (type) => {
    switch (type) {
      case 'voice': return Phone
      case 'sms': return MessageSquare
      case 'telegram': return Send
      default: return MessageSquare
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600'
      case 'active': return 'text-blue-600'
      case 'failed': return 'text-red-600'
      default: return 'text-coffee-brown'
    }
  }

  const getOutcomeColor = (outcome) => {
    switch (outcome) {
      case 'positive': return 'text-green-600 bg-green-50'
      case 'negative': return 'text-red-600 bg-red-50'
      default: return 'text-coffee-brown bg-coffee-beige'
    }
  }

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A'
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}m ${secs}s`
  }

  const SessionRow = ({ session }) => {
    const Icon = getSessionIcon(session.session_type)
    const isExpanded = expandedSessions.has(session.id)

    return (
      <div className="card-paper mb-4">
        <div 
          className="flex items-center justify-between p-4 cursor-pointer hover:bg-coffee-khaki transition-colors"
          onClick={() => toggleSessionExpansion(session.id)}
        >
          <div className="flex items-center space-x-4">
            <button className="text-coffee-brown">
              {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
            </button>
            
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-coffee-khaki rounded-full">
                <Icon size={20} className="text-coffee-brown" />
              </div>
              
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-coffee-brown">
                    {session.caller_id || 'Unknown'}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(session.status)}`}>
                    {session.status}
                  </span>
                  {session.outcome && (
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getOutcomeColor(session.outcome)}`}>
                      {session.outcome}
                    </span>
                  )}
                </div>
                <p className="text-sm text-coffee-sienna">
                  {format(new Date(session.started_at), 'MMM dd, yyyy HH:mm')}
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm font-medium text-coffee-brown">
                {formatDuration(session.duration_seconds)}
              </p>
              <p className="text-xs text-coffee-sienna">
                {session.session_type}
              </p>
            </div>
            
            <button
              onClick={(e) => {
                e.stopPropagation()
                handleSessionClick(session)
              }}
              className="btn-secondary text-sm px-3 py-1"
            >
              View Details
            </button>
          </div>
        </div>

        {isExpanded && (
          <div className="border-t border-coffee-tan p-4 bg-coffee-beige">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium text-coffee-brown mb-2">Session Info</h4>
                <div className="space-y-1 text-sm">
                  <p><span className="text-coffee-sienna">Company Number:</span> {session.company_number}</p>
                  <p><span className="text-coffee-sienna">Started:</span> {format(new Date(session.started_at), 'PPpp')}</p>
                  {session.ended_at && (
                    <p><span className="text-coffee-sienna">Ended:</span> {format(new Date(session.ended_at), 'PPpp')}</p>
                  )}
                </div>
              </div>
              
              {session.ai_summary && (
                <div>
                  <h4 className="font-medium text-coffee-brown mb-2">AI Summary</h4>
                  <p className="text-sm text-coffee-brown bg-coffee-khaki p-3 rounded border">
                    {session.ai_summary}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    )
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="loading-quill mb-4"></div>
            <p className="text-coffee-brown">The Scribe is retrieving conversation records...</p>
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
            <h1 className="heading-primary">Session History</h1>
            <p className="text-coffee-sienna">
              Complete record of all Scribe conversations and interactions
            </p>
          </div>
          
          <button className="btn-secondary flex items-center space-x-2">
            <Download size={16} />
            <span>Export</span>
          </button>
        </div>

        {/* Filters */}
        <div className="paper-panel">
          <div className="flex items-center space-x-4 mb-4">
            <Filter size={20} className="text-coffee-brown" />
            <h2 className="heading-secondary text-lg">Filters</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-coffee-brown font-medium mb-2">Search</label>
              <div className="relative">
                <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-coffee-sienna" />
                <input
                  type="text"
                  placeholder="Search caller ID, summary..."
                  value={filters.search}
                  onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                  className="input-paper pl-10 w-full"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-coffee-brown font-medium mb-2">Session Type</label>
              <select
                value={filters.session_type}
                onChange={(e) => setFilters(prev => ({ ...prev, session_type: e.target.value }))}
                className="input-paper w-full"
              >
                <option value="">All Types</option>
                <option value="voice">Voice</option>
                <option value="sms">SMS</option>
                <option value="telegram">Telegram</option>
              </select>
            </div>
            
            <div>
              <label className="block text-coffee-brown font-medium mb-2">Status</label>
              <select
                value={filters.status}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                className="input-paper w-full"
              >
                <option value="">All Statuses</option>
                <option value="completed">Completed</option>
                <option value="active">Active</option>
                <option value="failed">Failed</option>
              </select>
            </div>
            
            <div className="flex items-end">
              <button
                onClick={() => {
                  setFilters({ session_type: '', status: '', search: '' })
                  refetch()
                }}
                className="btn-secondary w-full"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Sessions List */}
        <div>
          {sessions && sessions.length > 0 ? (
            <div>
              {sessions.map(session => (
                <SessionRow key={session.id} session={session} />
              ))}
              
              {/* Pagination */}
              <div className="flex items-center justify-between mt-6">
                <p className="text-coffee-sienna">
                  Showing {pagination.offset + 1} to {Math.min(pagination.offset + pagination.limit, pagination.offset + sessions.length)} sessions
                </p>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setPagination(prev => ({ ...prev, offset: Math.max(0, prev.offset - prev.limit) }))}
                    disabled={pagination.offset === 0}
                    className="btn-secondary disabled:opacity-50"
                  >
                    Previous
                  </button>
                  
                  <button
                    onClick={() => setPagination(prev => ({ ...prev, offset: prev.offset + prev.limit }))}
                    disabled={sessions.length < pagination.limit}
                    className="btn-secondary disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="paper-panel text-center py-12">
              <MessageSquare size={48} className="mx-auto mb-4 text-coffee-sienna opacity-50" />
              <h3 className="text-lg font-medium text-coffee-brown mb-2">No Sessions Found</h3>
              <p className="text-coffee-sienna">
                {Object.values(filters).some(f => f) 
                  ? 'No sessions match your current filters. Try adjusting your search criteria.'
                  : 'Your Scribe hasn\'t handled any conversations yet. Sessions will appear here once interactions begin.'
                }
              </p>
            </div>
          )}
        </div>

        {/* Session Detail Modal */}
        {selectedSession && (
          <SessionDetailModal
            session={selectedSession}
            sessionDetail={sessionDetail}
            isLoading={detailLoading}
            onClose={() => setSelectedSession(null)}
          />
        )}
      </div>
    </Layout>
  )
}

// Session Detail Modal Component
const SessionDetailModal = ({ session, sessionDetail, isLoading, onClose }) => {
  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="modal-scroll max-w-4xl w-full mx-4 p-6">
          <div className="text-center">
            <div className="loading-quill mb-4"></div>
            <p className="text-coffee-brown">Loading session details...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="modal-scroll max-w-4xl w-full mx-4 p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="heading-secondary">Session Details</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-coffee-tan rounded-full"
          >
            <X size={20} />
          </button>
        </div>

        {sessionDetail && (
          <div className="space-y-6">
            {/* Session Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="font-medium text-coffee-brown">Session Information</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-coffee-sienna">Session ID:</span>
                    <span className="text-coffee-brown font-mono">{sessionDetail.session.id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-coffee-sienna">Type:</span>
                    <span className="text-coffee-brown capitalize">{sessionDetail.session.session_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-coffee-sienna">Caller ID:</span>
                    <span className="text-coffee-brown">{sessionDetail.session.caller_id || 'Unknown'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-coffee-sienna">Company Number:</span>
                    <span className="text-coffee-brown">{sessionDetail.session.company_number}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-coffee-sienna">Duration:</span>
                    <span className="text-coffee-brown">
                      {sessionDetail.session.duration_seconds 
                        ? `${Math.floor(sessionDetail.session.duration_seconds / 60)}m ${sessionDetail.session.duration_seconds % 60}s`
                        : 'N/A'
                      }
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-coffee-sienna">Status:</span>
                    <span className={`font-medium ${getStatusColor(sessionDetail.session.status)}`}>
                      {sessionDetail.session.status}
                    </span>
                  </div>
                  {sessionDetail.session.outcome && (
                    <div className="flex justify-between">
                      <span className="text-coffee-sienna">Outcome:</span>
                      <span className={`font-medium ${getOutcomeColor(sessionDetail.session.outcome).split(' ')[0]}`}>
                        {sessionDetail.session.outcome}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-medium text-coffee-brown">Timeline</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-coffee-sienna">Started:</span>
                    <span className="text-coffee-brown">
                      {format(new Date(sessionDetail.session.started_at), 'PPpp')}
                    </span>
                  </div>
                  {sessionDetail.session.ended_at && (
                    <div className="flex justify-between">
                      <span className="text-coffee-sienna">Ended:</span>
                      <span className="text-coffee-brown">
                        {format(new Date(sessionDetail.session.ended_at), 'PPpp')}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* AI Summary */}
            {sessionDetail.session.ai_summary && (
              <div>
                <h3 className="font-medium text-coffee-brown mb-3">AI Generated Summary</h3>
                <div className="bg-coffee-khaki p-4 rounded border-2 border-coffee-tan">
                  <p className="text-coffee-brown">{sessionDetail.session.ai_summary}</p>
                </div>
              </div>
            )}

            {/* Conversation Messages */}
            {sessionDetail.messages && sessionDetail.messages.length > 0 && (
              <div>
                <h3 className="font-medium text-coffee-brown mb-3">Conversation History</h3>
                <div className="space-y-3 max-h-96 overflow-y-auto bg-coffee-beige p-4 rounded border">
                  {sessionDetail.messages.map((message, index) => (
                    <div
                      key={message.id}
                      className={`flex ${message.speaker === 'user' ? 'justify-start' : 'justify-end'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.speaker === 'user'
                            ? 'bg-coffee-tan text-coffee-brown'
                            : 'bg-coffee-sienna text-coffee-beige'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-medium">
                            {message.speaker === 'user' ? 'User' : 'Scribe'}
                          </span>
                          <span className="text-xs opacity-75">
                            {format(new Date(message.timestamp), 'HH:mm')}
                          </span>
                        </div>
                        <p className="text-sm">{message.content}</p>
                        {message.message_type !== 'text' && (
                          <p className="text-xs opacity-75 mt-1">
                            Type: {message.message_type}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default SessionsPage