// Global type definitions for Aetherium Frontend

export interface User {
  id: string;
  email: string;
  phone: string;
  company_number: string;
  subscription_tier: 'apprentice' | 'journeyman' | 'master_scribe';
  subscription_status: 'active' | 'inactive' | 'expired';
  created_at: string;
  updated_at: string;
}

export interface Session {
  id: string;
  user_id: string;
  session_type: 'voice' | 'sms' | 'telegram';
  status: 'active' | 'completed' | 'failed';
  start_time: string;
  end_time?: string;
  duration?: number;
  phone_number?: string;
  telegram_chat_id?: string;
  conversation_summary?: string;
  outcome: 'positive' | 'negative' | 'neutral';
  created_at: string;
  updated_at: string;
}

export interface Workflow {
  id: string;
  user_id: string;
  name: string;
  description: string;
  nodes: WorkflowNode[];
  connections: WorkflowConnection[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkflowNode {
  id: string;
  type: 'trigger' | 'action' | 'condition' | 'response';
  position: { x: number; y: number };
  data: Record<string, any>;
}

export interface WorkflowConnection {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

export interface Statistics {
  total_calls: number;
  total_duration: number;
  positive_interactions: number;
  negative_interactions: number;
  neutral_interactions: number;
  active_sessions: number;
  hourly_distribution: Array<{
    hour: number;
    count: number;
  }>;
  daily_trends: Array<{
    date: string;
    calls: number;
    duration: number;
  }>;
}

export interface Payment {
  id: string;
  user_id: string;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed' | 'expired';
  payment_method: 'bank_transfer' | 'click' | 'payme';
  transaction_id?: string;
  created_at: string;
  updated_at: string;
}

export interface Subscription {
  id: string;
  user_id: string;
  tier: 'apprentice' | 'journeyman' | 'master_scribe';
  status: 'active' | 'inactive' | 'expired';
  start_date: string;
  end_date: string;
  auto_renew: boolean;
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T = any> {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

export interface WebSocketMessage {
  type: 'session_update' | 'call_status' | 'error' | 'notification';
  data: any;
  timestamp: string;
}

export interface AudioSettings {
  inputDevice?: string;
  outputDevice?: string;
  volume: number;
  noiseReduction: boolean;
  echoCancellation: boolean;
}

export interface TranslationKey {
  [key: string]: string | TranslationKey;
}

export interface SoundEffect {
  name: string;
  url: string;
  volume: number;
}

// Utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

// Form types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  password: string;
  confirmPassword: string;
  phone: string;
  acceptTerms: boolean;
}

export interface WorkflowForm {
  name: string;
  description: string;
  trigger_type: string;
  trigger_config: Record<string, any>;
}

// Error types
export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

export interface ValidationError {
  field: string;
  message: string;
}

// Theme types
export interface Theme {
  colors: {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    border: string;
    error: string;
    warning: string;
    success: string;
    info: string;
  };
  fonts: {
    heading: string;
    body: string;
    mono: string;
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
    full: string;
  };
}