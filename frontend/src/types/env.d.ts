/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_WS_BASE_URL: string;
  readonly VITE_APP_NAME: string;
  readonly VITE_APP_VERSION: string;
  readonly VITE_ENVIRONMENT: 'development' | 'staging' | 'production';
  readonly VITE_ENABLE_ANALYTICS: string;
  readonly VITE_SENTRY_DSN: string;
  readonly VITE_TELEGRAM_BOT_USERNAME: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}