import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, isFirstLogin } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-coffee-beige">
        <div className="text-center">
          <div className="loading-quill mb-4"></div>
          <p className="text-coffee-brown font-body">The Scribe is preparing...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Redirect to company number page on first login (except if already there)
  if (isFirstLogin && location.pathname !== '/company-number') {
    return <Navigate to="/company-number" replace />
  }

  return children
}

export default ProtectedRoute