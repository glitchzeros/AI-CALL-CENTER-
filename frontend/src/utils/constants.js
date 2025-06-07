// Application Constants

export const APP_CONFIG = {
  name: import.meta.env.VITE_APP_NAME || 'Aetherium',
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  environment: import.meta.env.VITE_ENVIRONMENT || 'development',
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  wsBaseUrl: import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000',
};

export const SUBSCRIPTION_TIERS = {
  APPRENTICE: {
    id: 'apprentice',
    name: 'Apprentice Scribe',
    price: 20,
    currency: 'USD',
    contextLimit: 4000,
    features: [
      'Basic AI conversations',
      '4K context memory',
      'SMS integration',
      'Basic analytics',
      'Email support'
    ],
    color: '#8B4513'
  },
  JOURNEYMAN: {
    id: 'journeyman',
    name: 'Journeyman Scribe',
    price: 50,
    currency: 'USD',
    contextLimit: 32000,
    features: [
      'Advanced AI conversations',
      '32K context memory',
      'Voice calls + SMS',
      'Telegram integration',
      'Advanced analytics',
      'Priority support',
      'Workflow automation'
    ],
    color: '#D2691E'
  },
  MASTER_SCRIBE: {
    id: 'master_scribe',
    name: 'Master Scribe',
    price: 100,
    currency: 'USD',
    contextLimit: -1, // Unlimited
    features: [
      'Premium AI conversations',
      'Unlimited context memory',
      'All communication channels',
      'Advanced workflow builder',
      'Real-time analytics',
      'Custom integrations',
      'Dedicated support',
      'API access'
    ],
    color: '#A0522D'
  }
};

export const SESSION_TYPES = {
  VOICE: 'voice',
  SMS: 'sms',
  TELEGRAM: 'telegram'
};

export const SESSION_STATUS = {
  ACTIVE: 'active',
  COMPLETED: 'completed',
  FAILED: 'failed'
};

export const PAYMENT_STATUS = {
  PENDING: 'pending',
  COMPLETED: 'completed',
  FAILED: 'failed',
  EXPIRED: 'expired'
};

export const WORKFLOW_NODE_TYPES = {
  TRIGGER: 'trigger',
  ACTION: 'action',
  CONDITION: 'condition',
  RESPONSE: 'response'
};

export const INVOCATION_TYPES = {
  PAYMENT_RITUAL: 'payment_ritual',
  MESSENGER: 'messenger',
  TELEGRAM_CHANNELER: 'telegram_channeler',
  FINAL_WORD: 'final_word',
  SCRIBES_REPLY: 'scribes_reply'
};

export const COFFEE_PAPER_THEME = {
  colors: {
    primary: '#8B4513', // Saddle Brown
    secondary: '#D2B48C', // Tan
    background: '#F5F5DC', // Beige
    surface: '#FAEBD7', // Antique White
    text: '#654321', // Dark Brown
    textSecondary: '#8B7355', // Burlywood
    border: '#DEB887', // Burlywood
    error: '#CD853F', // Peru
    warning: '#DAA520', // Goldenrod
    success: '#228B22', // Forest Green
    info: '#4682B4', // Steel Blue
    accent: '#A0522D' // Sienna
  },
  fonts: {
    heading: '"Cinzel Decorative", serif',
    body: '"Vollkorn", serif',
    mono: '"Courier New", monospace'
  },
  effects: {
    paperTexture: 'url("/textures/paper-grain.png")',
    inkStain: 'url("/textures/ink-stain.png")',
    coffeeRing: 'url("/textures/coffee-ring.png")'
  }
};

export const SOUND_EFFECTS = {
  PAGE_TURN: '/sounds/page-turn.mp3',
  PEN_SCRATCH: '/sounds/pen-scratch.mp3',
  BOOK_CLOSE: '/sounds/book-close.mp3',
  PAPER_SLIDE: '/sounds/paper-slide.mp3',
  INK_DROP: '/sounds/ink-drop.mp3',
  NOTIFICATION: '/sounds/notification.mp3',
  SUCCESS: '/sounds/success.mp3',
  ERROR: '/sounds/error.mp3'
};

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
    VERIFY_EMAIL: '/api/auth/verify-email',
    FORGOT_PASSWORD: '/api/auth/forgot-password',
    RESET_PASSWORD: '/api/auth/reset-password'
  },
  USERS: {
    PROFILE: '/api/users/profile',
    UPDATE_PROFILE: '/api/users/profile',
    CHANGE_PASSWORD: '/api/users/change-password',
    DELETE_ACCOUNT: '/api/users/delete-account'
  },
  SUBSCRIPTIONS: {
    LIST: '/api/subscriptions',
    CURRENT: '/api/subscriptions/current',
    SUBSCRIBE: '/api/subscriptions/subscribe',
    CANCEL: '/api/subscriptions/cancel',
    UPGRADE: '/api/subscriptions/upgrade'
  },
  WORKFLOWS: {
    LIST: '/api/workflows',
    CREATE: '/api/workflows',
    UPDATE: '/api/workflows',
    DELETE: '/api/workflows',
    ACTIVATE: '/api/workflows/activate',
    DEACTIVATE: '/api/workflows/deactivate'
  },
  SESSIONS: {
    LIST: '/api/sessions',
    CREATE: '/api/sessions',
    UPDATE: '/api/sessions',
    DELETE: '/api/sessions',
    ACTIVE: '/api/sessions/active'
  },
  STATISTICS: {
    OVERVIEW: '/api/statistics/overview',
    DETAILED: '/api/statistics/detailed',
    EXPORT: '/api/statistics/export'
  },
  PAYMENTS: {
    LIST: '/api/payments',
    CREATE: '/api/payments',
    VERIFY: '/api/payments/verify',
    CANCEL: '/api/payments/cancel'
  },
  TELEGRAM: {
    CONNECT: '/api/telegram/connect',
    DISCONNECT: '/api/telegram/disconnect',
    STATUS: '/api/telegram/status'
  }
};

export const WEBSOCKET_EVENTS = {
  SESSION_UPDATE: 'session_update',
  CALL_STATUS: 'call_status',
  ERROR: 'error',
  NOTIFICATION: 'notification',
  WORKFLOW_TRIGGER: 'workflow_trigger'
};

export const LOCAL_STORAGE_KEYS = {
  AUTH_TOKEN: 'aetherium_auth_token',
  REFRESH_TOKEN: 'aetherium_refresh_token',
  USER_PREFERENCES: 'aetherium_user_preferences',
  THEME_SETTINGS: 'aetherium_theme_settings',
  SOUND_SETTINGS: 'aetherium_sound_settings'
};

export const VALIDATION_RULES = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE: /^\+?[1-9]\d{1,14}$/,
  PASSWORD: {
    minLength: 8,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecialChars: true
  }
};

export const DATE_FORMATS = {
  DISPLAY: 'MMM dd, yyyy',
  DISPLAY_WITH_TIME: 'MMM dd, yyyy HH:mm',
  ISO: 'yyyy-MM-dd',
  TIME_ONLY: 'HH:mm',
  FULL: 'EEEE, MMMM dd, yyyy HH:mm:ss'
};

export const PAGINATION_DEFAULTS = {
  PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100
};

export const DEBOUNCE_DELAYS = {
  SEARCH: 300,
  SAVE: 1000,
  RESIZE: 100
};

export const ANIMATION_DURATIONS = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500
};

export const BREAKPOINTS = {
  SM: 640,
  MD: 768,
  LG: 1024,
  XL: 1280,
  '2XL': 1536
};