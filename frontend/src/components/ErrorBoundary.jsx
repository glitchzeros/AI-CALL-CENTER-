import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      errorId: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { 
      hasError: true,
      errorId: Math.random().toString(36).substr(2, 9)
    };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details
    console.error('Error Boundary caught an error:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // Log to external service if available
    if (window.Sentry) {
      window.Sentry.captureException(error, {
        contexts: {
          react: {
            componentStack: errorInfo.componentStack
          }
        }
      });
    }
  }

  handleRetry = () => {
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null,
      errorId: null
    });
  };

  render() {
    if (this.state.hasError) {
      return (
        <ErrorFallback
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          errorId={this.state.errorId}
          onRetry={this.handleRetry}
          resetError={this.handleRetry}
        />
      );
    }

    return this.props.children;
  }
}

const ErrorFallback = ({ error, errorInfo, errorId, onRetry, resetError }) => {
  const navigate = useNavigate();
  const isDevelopment = import.meta.env.VITE_ENVIRONMENT === 'development';

  const handleGoHome = () => {
    resetError();
    navigate('/');
  };

  const handleReload = () => {
    window.location.reload();
  };

  const copyErrorDetails = () => {
    const errorDetails = {
      errorId,
      message: error?.message,
      stack: error?.stack,
      componentStack: errorInfo?.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    navigator.clipboard.writeText(JSON.stringify(errorDetails, null, 2))
      .then(() => {
        alert('Error details copied to clipboard');
      })
      .catch(() => {
        console.error('Failed to copy error details');
      });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-xl border-2 border-amber-200 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-amber-600 to-orange-600 text-white p-6">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="h-8 w-8" />
            <div>
              <h1 className="text-2xl font-bold font-['Cinzel_Decorative']">
                The Scribe Encountered an Error
              </h1>
              <p className="text-amber-100 mt-1">
                Something unexpected happened in the mystical realm
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Error Message */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="font-semibold text-red-800 mb-2">Error Details</h3>
            <p className="text-red-700 font-mono text-sm">
              {error?.message || 'An unknown error occurred'}
            </p>
            {errorId && (
              <p className="text-red-600 text-xs mt-2">
                Error ID: {errorId}
              </p>
            )}
          </div>

          {/* Development Details */}
          {isDevelopment && error?.stack && (
            <details className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <summary className="font-semibold text-gray-800 cursor-pointer">
                Stack Trace (Development)
              </summary>
              <pre className="text-xs text-gray-600 mt-2 overflow-auto max-h-40">
                {error.stack}
              </pre>
            </details>
          )}

          {/* Actions */}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={onRetry}
              className="flex items-center space-x-2 bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Try Again</span>
            </button>

            <button
              onClick={handleGoHome}
              className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <Home className="h-4 w-4" />
              <span>Go Home</span>
            </button>

            <button
              onClick={handleReload}
              className="flex items-center space-x-2 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Reload Page</span>
            </button>

            {isDevelopment && (
              <button
                onClick={copyErrorDetails}
                className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <span>Copy Error Details</span>
              </button>
            )}
          </div>

          {/* Help Text */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-800 mb-2">What can you do?</h3>
            <ul className="text-blue-700 text-sm space-y-1">
              <li>• Try refreshing the page or clicking "Try Again"</li>
              <li>• Check your internet connection</li>
              <li>• Clear your browser cache and cookies</li>
              <li>• If the problem persists, contact support with the Error ID</li>
            </ul>
          </div>

          {/* Contact Support */}
          <div className="text-center text-gray-600 text-sm">
            <p>
              Need help? Contact our support team at{' '}
              <a 
                href="mailto:support@aetherium.ai" 
                className="text-amber-600 hover:text-amber-700 underline"
              >
                support@aetherium.ai
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ErrorBoundary;