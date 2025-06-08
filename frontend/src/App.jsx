import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './hooks/useAuth'
import { SoundProvider } from './hooks/useSound'
import { TranslationProvider } from './hooks/useTranslation'
import ProtectedRoute from './components/ProtectedRoute'

// Pages
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import CompanyNumberPage from './pages/CompanyNumberPage'
import DashboardPage from './pages/DashboardPage'
import SubscriptionPage from './pages/SubscriptionPage'
import InvocationEditorPage from './pages/InvocationEditorPage'
import StatisticsPage from './pages/StatisticsPage'
import SessionsPage from './pages/SessionsPage'
import TranslationTestPage from './pages/TranslationTestPage'
import GSMModulesPage from './pages/GSMModulesPage'

function App() {
  return (
    <TranslationProvider>
      <AuthProvider>
        <SoundProvider>
          <div className="app">
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/translation-test" element={<TranslationTestPage />} />
            
            {/* Protected routes */}
            <Route path="/company-number" element={
              <ProtectedRoute>
                <CompanyNumberPage />
              </ProtectedRoute>
            } />
            
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } />
            
            <Route path="/subscription" element={
              <ProtectedRoute>
                <SubscriptionPage />
              </ProtectedRoute>
            } />
            
            <Route path="/invocation-editor" element={
              <ProtectedRoute>
                <InvocationEditorPage />
              </ProtectedRoute>
            } />
            
            <Route path="/statistics" element={
              <ProtectedRoute>
                <StatisticsPage />
              </ProtectedRoute>
            } />
            
            <Route path="/sessions" element={
              <ProtectedRoute>
                <SessionsPage />
              </ProtectedRoute>
            } />
            
            <Route path="/gsm-modules" element={
              <ProtectedRoute>
                <GSMModulesPage />
              </ProtectedRoute>
            } />
            
            {/* Default redirect */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          </div>
        </SoundProvider>
      </AuthProvider>
    </TranslationProvider>
  )
}

export default App