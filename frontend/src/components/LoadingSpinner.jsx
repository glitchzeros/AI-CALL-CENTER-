import React from 'react';
import { cn } from '../utils/helpers';

const LoadingSpinner = ({ 
  size = 'md', 
  color = 'amber', 
  text = null, 
  fullScreen = false,
  className = '',
  ...props 
}) => {
  const sizeClasses = {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12',
    '2xl': 'h-16 w-16'
  };

  const colorClasses = {
    amber: 'text-amber-600',
    blue: 'text-blue-600',
    green: 'text-green-600',
    red: 'text-red-600',
    purple: 'text-purple-600',
    gray: 'text-gray-600'
  };

  const spinnerElement = (
    <div className={cn('flex items-center justify-center', className)} {...props}>
      <div className="flex flex-col items-center space-y-3">
        {/* Spinner */}
        <div className="relative">
          <div
            className={cn(
              'animate-spin rounded-full border-2 border-transparent',
              sizeClasses[size],
              colorClasses[color]
            )}
            style={{
              borderTopColor: 'currentColor',
              borderRightColor: 'currentColor',
              borderBottomColor: 'transparent',
              borderLeftColor: 'transparent'
            }}
          />
          {/* Inner spinner for coffee paper effect */}
          <div
            className={cn(
              'absolute inset-1 animate-spin rounded-full border border-transparent',
              'opacity-30'
            )}
            style={{
              borderTopColor: 'currentColor',
              borderRightColor: 'transparent',
              borderBottomColor: 'currentColor',
              borderLeftColor: 'transparent',
              animationDirection: 'reverse',
              animationDuration: '1.5s'
            }}
          />
        </div>

        {/* Loading text */}
        {text && (
          <div className="text-center">
            <p className={cn(
              'font-serif text-sm',
              colorClasses[color],
              'animate-pulse'
            )}>
              {text}
            </p>
          </div>
        )}
      </div>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-gradient-to-br from-amber-50 to-orange-100 bg-opacity-90 backdrop-blur-sm z-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-xl border-2 border-amber-200 p-8">
          {spinnerElement}
        </div>
      </div>
    );
  }

  return spinnerElement;
};

// Specialized loading components
export const PageLoader = ({ text = "The Scribe is preparing..." }) => (
  <LoadingSpinner 
    size="xl" 
    color="amber" 
    text={text}
    fullScreen 
    className="min-h-screen"
  />
);

export const ButtonLoader = ({ size = 'sm', color = 'white' }) => (
  <LoadingSpinner 
    size={size} 
    color={color}
    className="inline-flex"
  />
);

export const CardLoader = ({ text = "Loading..." }) => (
  <div className="flex items-center justify-center p-8">
    <LoadingSpinner 
      size="lg" 
      color="amber" 
      text={text}
    />
  </div>
);

export const TableLoader = () => (
  <div className="flex items-center justify-center py-12">
    <LoadingSpinner 
      size="lg" 
      color="amber" 
      text="Loading data..."
    />
  </div>
);

// Skeleton loaders for better UX
export const SkeletonLoader = ({ className = '', lines = 3, ...props }) => (
  <div className={cn('animate-pulse space-y-3', className)} {...props}>
    {Array.from({ length: lines }).map((_, index) => (
      <div
        key={index}
        className={cn(
          'h-4 bg-gradient-to-r from-amber-100 to-orange-100 rounded',
          index === lines - 1 ? 'w-3/4' : 'w-full'
        )}
      />
    ))}
  </div>
);

export const CardSkeleton = () => (
  <div className="bg-white rounded-lg border-2 border-amber-200 p-6 animate-pulse">
    <div className="space-y-4">
      <div className="h-6 bg-gradient-to-r from-amber-100 to-orange-100 rounded w-1/2" />
      <div className="space-y-2">
        <div className="h-4 bg-gradient-to-r from-amber-100 to-orange-100 rounded" />
        <div className="h-4 bg-gradient-to-r from-amber-100 to-orange-100 rounded w-5/6" />
        <div className="h-4 bg-gradient-to-r from-amber-100 to-orange-100 rounded w-3/4" />
      </div>
    </div>
  </div>
);

export const TableSkeleton = ({ rows = 5, columns = 4 }) => (
  <div className="space-y-3">
    {/* Header */}
    <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
      {Array.from({ length: columns }).map((_, index) => (
        <div
          key={`header-${index}`}
          className="h-6 bg-gradient-to-r from-amber-200 to-orange-200 rounded"
        />
      ))}
    </div>
    
    {/* Rows */}
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <div
        key={`row-${rowIndex}`}
        className="grid gap-4"
        style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}
      >
        {Array.from({ length: columns }).map((_, colIndex) => (
          <div
            key={`cell-${rowIndex}-${colIndex}`}
            className="h-4 bg-gradient-to-r from-amber-100 to-orange-100 rounded"
          />
        ))}
      </div>
    ))}
  </div>
);

// Loading states for specific components
export const WorkflowLoader = () => (
  <div className="flex items-center justify-center h-96 bg-gradient-to-br from-amber-50 to-orange-100 rounded-lg border-2 border-amber-200">
    <LoadingSpinner 
      size="xl" 
      color="amber" 
      text="Loading workflow canvas..."
    />
  </div>
);

export const ChartLoader = () => (
  <div className="flex items-center justify-center h-64 bg-gradient-to-br from-amber-50 to-orange-100 rounded-lg border-2 border-amber-200">
    <LoadingSpinner 
      size="lg" 
      color="amber" 
      text="Generating charts..."
    />
  </div>
);

export const SessionLoader = () => (
  <div className="flex items-center justify-center p-8">
    <div className="text-center space-y-4">
      <LoadingSpinner size="xl" color="amber" />
      <div className="space-y-2">
        <p className="text-amber-700 font-serif text-lg">
          Establishing connection...
        </p>
        <p className="text-amber-600 text-sm">
          The Scribe is preparing for your conversation
        </p>
      </div>
    </div>
  </div>
);

// Animated dots loader
export const DotsLoader = ({ color = 'amber' }) => (
  <div className="flex space-x-1">
    {[0, 1, 2].map((index) => (
      <div
        key={index}
        className={cn(
          'h-2 w-2 rounded-full animate-bounce',
          colorClasses[color] || 'bg-amber-600'
        )}
        style={{
          animationDelay: `${index * 0.1}s`,
          animationDuration: '0.6s'
        }}
      />
    ))}
  </div>
);

// Progress bar loader
export const ProgressLoader = ({ progress = 0, text = '', className = '' }) => (
  <div className={cn('w-full space-y-2', className)}>
    <div className="flex justify-between text-sm text-amber-700">
      <span>{text}</span>
      <span>{Math.round(progress)}%</span>
    </div>
    <div className="w-full bg-amber-100 rounded-full h-2">
      <div
        className="bg-gradient-to-r from-amber-500 to-orange-500 h-2 rounded-full transition-all duration-300 ease-out"
        style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
      />
    </div>
  </div>
);

export default LoadingSpinner;