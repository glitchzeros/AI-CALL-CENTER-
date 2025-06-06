/**
 * Aetherium Manual Translation System
 * The Scribe's Linguistic Codex
 * 
 * All translations are manually crafted to maintain the thematic integrity
 * and cultural authenticity of the Aetherium platform.
 */

// Supported languages
export const SUPPORTED_LANGUAGES = {
  en: 'English',
  uz: 'O\'zbekcha',
  ru: 'Русский'
}

// Default language
export const DEFAULT_LANGUAGE = 'en'

// Manual translations organized by page/component
export const translations = {
  // Common/Shared translations
  common: {
    en: {
      aetherium: 'Aetherium',
      scribe: 'The Scribe',
      loading: 'Loading...',
      save: 'Save',
      cancel: 'Cancel',
      confirm: 'Confirm',
      close: 'Close',
      copy: 'Copy',
      copied: 'Copied!',
      error: 'Error',
      success: 'Success',
      warning: 'Warning',
      info: 'Information',
      yes: 'Yes',
      no: 'No',
      back: 'Back',
      next: 'Next',
      previous: 'Previous',
      continue: 'Continue',
      finish: 'Finish',
      edit: 'Edit',
      delete: 'Delete',
      view: 'View',
      download: 'Download',
      upload: 'Upload',
      search: 'Search',
      filter: 'Filter',
      sort: 'Sort',
      refresh: 'Refresh',
      settings: 'Settings',
      help: 'Help',
      logout: 'Logout',
      profile: 'Profile'
    },
    uz: {
      aetherium: 'Aetherium',
      scribe: 'Kotib',
      loading: 'Yuklanmoqda...',
      save: 'Saqlash',
      cancel: 'Bekor qilish',
      confirm: 'Tasdiqlash',
      close: 'Yopish',
      copy: 'Nusxalash',
      copied: 'Nusxalandi!',
      error: 'Xatolik',
      success: 'Muvaffaqiyat',
      warning: 'Ogohlantirish',
      info: 'Ma\'lumot',
      yes: 'Ha',
      no: 'Yo\'q',
      back: 'Orqaga',
      next: 'Keyingi',
      previous: 'Oldingi',
      continue: 'Davom etish',
      finish: 'Tugatish',
      edit: 'Tahrirlash',
      delete: 'O\'chirish',
      view: 'Ko\'rish',
      download: 'Yuklab olish',
      upload: 'Yuklash',
      search: 'Qidirish',
      filter: 'Filtrlash',
      sort: 'Saralash',
      refresh: 'Yangilash',
      settings: 'Sozlamalar',
      help: 'Yordam',
      logout: 'Chiqish',
      profile: 'Profil'
    },
    ru: {
      aetherium: 'Aetherium',
      scribe: 'Писец',
      loading: 'Загрузка...',
      save: 'Сохранить',
      cancel: 'Отмена',
      confirm: 'Подтвердить',
      close: 'Закрыть',
      copy: 'Копировать',
      copied: 'Скопировано!',
      error: 'Ошибка',
      success: 'Успех',
      warning: 'Предупреждение',
      info: 'Информация',
      yes: 'Да',
      no: 'Нет',
      back: 'Назад',
      next: 'Далее',
      previous: 'Предыдущий',
      continue: 'Продолжить',
      finish: 'Завершить',
      edit: 'Редактировать',
      delete: 'Удалить',
      view: 'Просмотр',
      download: 'Скачать',
      upload: 'Загрузить',
      search: 'Поиск',
      filter: 'Фильтр',
      sort: 'Сортировка',
      refresh: 'Обновить',
      settings: 'Настройки',
      help: 'Помощь',
      logout: 'Выйти',
      profile: 'Профиль'
    }
  },

  // Authentication pages
  auth: {
    en: {
      // Login page
      loginTitle: 'The Scribe\'s Portal',
      loginSubtitle: 'Enter your credentials to access the realm',
      emailOrPhone: 'Email or Phone Number',
      emailOrPhonePlaceholder: 'Enter your email or phone number',
      password: 'Password',
      passwordPlaceholder: 'Enter your password',
      enterRealm: 'Enter the Realm',
      newToAetherium: 'New to Aetherium?',
      beginJourney: 'Begin your journey',
      loginFooter: 'Where AI Scribes dwell and conversations flow like ink upon parchment',
      
      // Register page
      registerTitle: 'Join Aetherium',
      registerSubtitle: 'Begin Your Journey',
      registerDescription: 'Create your account to access the Scribe\'s realm',
      emailAddress: 'Email Address',
      emailPlaceholder: 'your.email@example.com',
      phoneNumber: 'Phone Number',
      phonePlaceholder: '+998901234567',
      phoneHint: 'Include country code (e.g., +998901234567)',
      createPassword: 'Create a strong password',
      confirmPassword: 'Confirm your password',
      createAccount: 'Create Account',
      alreadyHaveAccount: 'Already have an account?',
      signInHere: 'Sign in here',
      registerFooter: 'By creating an account, you agree to let the Scribe serve your communication needs',
      
      // Verification
      verificationTitle: 'Verification',
      verificationDescription: 'A verification code has been sent to your phone',
      verificationCode: 'Verification Code',
      verificationCodePlaceholder: '000000',
      verificationCodeHint: 'Enter the 6-digit code sent to your phone',
      verifyCode: 'Verify Code',
      resendCode: 'Resend Code',
      resendIn: 'Resend in',
      backToRegistration: 'Back to registration',
      
      // Validation messages
      emailRequired: 'Email is required',
      emailInvalid: 'Invalid email address',
      phoneRequired: 'Phone number is required',
      phoneInvalid: 'Invalid phone number format',
      passwordRequired: 'Password is required',
      passwordMinLength: 'Password must be at least 8 characters',
      confirmPasswordRequired: 'Please confirm your password',
      passwordsNotMatch: 'Passwords do not match',
      loginIdentifierRequired: 'Email or phone number is required'
    },
    uz: {
      // Login page
      loginTitle: 'Kotibning Portali',
      loginSubtitle: 'Hududga kirish uchun ma\'lumotlaringizni kiriting',
      emailOrPhone: 'Email yoki Telefon Raqami',
      emailOrPhonePlaceholder: 'Email yoki telefon raqamingizni kiriting',
      password: 'Parol',
      passwordPlaceholder: 'Parolingizni kiriting',
      enterRealm: 'Hududga Kirish',
      newToAetherium: 'Aetherium\'da yangimisiz?',
      beginJourney: 'Sayohatingizni boshlang',
      loginFooter: 'AI Kotiblar yashaydi va suhbatlar qog\'ozda siyohdek oqadi',
      
      // Register page
      registerTitle: 'Aetherium\'ga Qo\'shiling',
      registerSubtitle: 'Sayohatingizni Boshlang',
      registerDescription: 'Kotib hududiga kirish uchun hisobingizni yarating',
      emailAddress: 'Email Manzili',
      emailPlaceholder: 'sizning.email@example.com',
      phoneNumber: 'Telefon Raqami',
      phonePlaceholder: '+998901234567',
      phoneHint: 'Mamlakat kodini kiriting (masalan, +998901234567)',
      createPassword: 'Kuchli parol yarating',
      confirmPassword: 'Parolingizni tasdiqlang',
      createAccount: 'Hisob Yaratish',
      alreadyHaveAccount: 'Hisobingiz bormi?',
      signInHere: 'Bu yerda kiring',
      registerFooter: 'Hisob yaratish orqali siz Kotibga aloqa ehtiyojlaringizga xizmat qilishiga rozilik berasiz',
      
      // Verification
      verificationTitle: 'Tasdiqlash',
      verificationDescription: 'Telefoningizga tasdiqlash kodi yuborildi',
      verificationCode: 'Tasdiqlash Kodi',
      verificationCodePlaceholder: '000000',
      verificationCodeHint: 'Telefoningizga yuborilgan 6 raqamli kodni kiriting',
      verifyCode: 'Kodni Tasdiqlash',
      resendCode: 'Kodni Qayta Yuborish',
      resendIn: 'Qayta yuborish',
      backToRegistration: 'Ro\'yxatga qaytish',
      
      // Validation messages
      emailRequired: 'Email talab qilinadi',
      emailInvalid: 'Noto\'g\'ri email manzili',
      phoneRequired: 'Telefon raqami talab qilinadi',
      phoneInvalid: 'Noto\'g\'ri telefon raqami formati',
      passwordRequired: 'Parol talab qilinadi',
      passwordMinLength: 'Parol kamida 8 ta belgidan iborat bo\'lishi kerak',
      confirmPasswordRequired: 'Iltimos, parolingizni tasdiqlang',
      passwordsNotMatch: 'Parollar mos kelmaydi',
      loginIdentifierRequired: 'Email yoki telefon raqami talab qilinadi'
    },
    ru: {
      // Login page
      loginTitle: 'Портал Писца',
      loginSubtitle: 'Введите свои данные для доступа в область',
      emailOrPhone: 'Email или Номер Телефона',
      emailOrPhonePlaceholder: 'Введите ваш email или номер телефона',
      password: 'Пароль',
      passwordPlaceholder: 'Введите ваш пароль',
      enterRealm: 'Войти в Область',
      newToAetherium: 'Новичок в Aetherium?',
      beginJourney: 'Начните ваше путешествие',
      loginFooter: 'Где обитают ИИ Писцы и разговоры текут как чернила по пергаменту',
      
      // Register page
      registerTitle: 'Присоединиться к Aetherium',
      registerSubtitle: 'Начните Ваше Путешествие',
      registerDescription: 'Создайте аккаунт для доступа к области Писца',
      emailAddress: 'Email Адрес',
      emailPlaceholder: 'ваш.email@example.com',
      phoneNumber: 'Номер Телефона',
      phonePlaceholder: '+998901234567',
      phoneHint: 'Включите код страны (например, +998901234567)',
      createPassword: 'Создайте надежный пароль',
      confirmPassword: 'Подтвердите ваш пароль',
      createAccount: 'Создать Аккаунт',
      alreadyHaveAccount: 'Уже есть аккаунт?',
      signInHere: 'Войдите здесь',
      registerFooter: 'Создавая аккаунт, вы соглашаетесь позволить Писцу обслуживать ваши коммуникационные потребности',
      
      // Verification
      verificationTitle: 'Верификация',
      verificationDescription: 'Код подтверждения отправлен на ваш телефон',
      verificationCode: 'Код Подтверждения',
      verificationCodePlaceholder: '000000',
      verificationCodeHint: 'Введите 6-значный код, отправленный на ваш телефон',
      verifyCode: 'Подтвердить Код',
      resendCode: 'Отправить Код Повторно',
      resendIn: 'Повторная отправка через',
      backToRegistration: 'Вернуться к регистрации',
      
      // Validation messages
      emailRequired: 'Email обязателен',
      emailInvalid: 'Неверный email адрес',
      phoneRequired: 'Номер телефона обязателен',
      phoneInvalid: 'Неверный формат номера телефона',
      passwordRequired: 'Пароль обязателен',
      passwordMinLength: 'Пароль должен содержать минимум 8 символов',
      confirmPasswordRequired: 'Пожалуйста, подтвердите ваш пароль',
      passwordsNotMatch: 'Пароли не совпадают',
      loginIdentifierRequired: 'Email или номер телефона обязателен'
    }
  },

  // Company Number page
  companyNumber: {
    en: {
      title: 'Your Scribe\'s Direct Line',
      subtitle: 'The Conduit for Automated Conversations',
      description: 'This is your Scribe\'s direct line. It is the conduit for your automated conversations. Guard it well.',
      phoneNumber: 'Company Phone Number',
      continueToPortal: 'Continue to Portal',
      footer: 'This number will be your gateway to the realm of AI-powered communications'
    },
    uz: {
      title: 'Kotibingizning To\'g\'ridan-to\'g\'ri Liniyasi',
      subtitle: 'Avtomatlashtirilgan Suhbatlar uchun O\'tkazgich',
      description: 'Bu sizning Kotibingizning to\'g\'ridan-to\'g\'ri liniyasi. Bu sizning avtomatlashtirilgan suhbatlaringiz uchun o\'tkazgichdir. Uni yaxshi saqlang.',
      phoneNumber: 'Kompaniya Telefon Raqami',
      continueToPortal: 'Portalga Davom Etish',
      footer: 'Bu raqam AI-quvvatli aloqalar hududiga sizning darvozangiz bo\'ladi'
    },
    ru: {
      title: 'Прямая Линия Вашего Писца',
      subtitle: 'Проводник для Автоматизированных Разговоров',
      description: 'Это прямая линия вашего Писца. Это проводник для ваших автоматизированных разговоров. Берегите её хорошо.',
      phoneNumber: 'Номер Телефона Компании',
      continueToPortal: 'Продолжить в Портал',
      footer: 'Этот номер будет вашими воротами в область ИИ-коммуникаций'
    }
  },

  // Dashboard
  dashboard: {
    en: {
      title: 'The Scribe\'s Observatory',
      subtitle: 'Monitor Your AI Agent\'s Performance',
      totalCalls: 'Total Calls Handled',
      totalDuration: 'Total Call Duration',
      positiveInteractions: 'Positive Interactions',
      negativeInteractions: 'Negative Interactions',
      activeSessions: 'Active Sessions',
      recentActivity: 'Recent Activity',
      callHistory: 'Call History',
      lastUpdated: 'Last Updated',
      noRecentActivity: 'No recent activity',
      viewDetails: 'View Details',
      refreshData: 'Refresh Data',
      sessionDetails: 'Session Details',
      caller: 'Caller',
      duration: 'Duration',
      outcome: 'Outcome',
      summary: 'Summary',
      timestamp: 'Timestamp',
      channel: 'Channel',
      voice: 'Voice',
      sms: 'SMS',
      telegram: 'Telegram',
      positive: 'Positive',
      negative: 'Negative',
      neutral: 'Neutral',
      loadingInsights: 'The Scribe is gathering insights...',
      allTimeConversations: 'All-time conversations',
      cumulativeTalkTime: 'Cumulative talk time',
      successfulOutcomes: 'successful outcomes',
      perConversation: 'Per conversation',
      averageCallDuration: 'Average Call Duration',
      liveConversations: 'Your Scribe is currently handling live conversations',
      quickActions: 'Quick Actions',
      editWorkflows: 'Edit Workflows',
      viewSessions: 'View Sessions',
      detailedAnalytics: 'Detailed Analytics',
      systemStatus: 'System Status',
      aiScribe: 'AI Scribe',
      voiceSystem: 'Voice System',
      messaging: 'Messaging',
      online: 'Online',
      ready: 'Ready',
      active: 'Active',
      last24Hours: 'Last 24 Hours',
      sessions: 'Sessions',
      successRate: 'Success Rate',
      avgDuration: 'Avg Duration',
      sessionTypes: 'Session Types',
      activeSessionsDesc: 'Your Scribe is currently handling live conversations'
    },
    uz: {
      title: 'Kotibning Observatoriyasi',
      subtitle: 'AI Agentingizning Ishlashini Kuzating',
      totalCalls: 'Jami Qo\'ng\'iroqlar Soni',
      totalDuration: 'Jami Qo\'ng\'iroq Davomiyligi',
      positiveInteractions: 'Ijobiy Muloqotlar',
      negativeInteractions: 'Salbiy Muloqotlar',
      activeSessions: 'Faol Seanslar',
      recentActivity: 'So\'nggi Faoliyat',
      callHistory: 'Qo\'ng\'iroqlar Tarixi',
      lastUpdated: 'Oxirgi Yangilanish',
      noRecentActivity: 'So\'nggi faoliyat yo\'q',
      viewDetails: 'Tafsilotlarni Ko\'rish',
      refreshData: 'Ma\'lumotlarni Yangilash',
      sessionDetails: 'Seans Tafsilotlari',
      caller: 'Qo\'ng\'iroq Qiluvchi',
      duration: 'Davomiylik',
      outcome: 'Natija',
      summary: 'Xulosa',
      timestamp: 'Vaqt Belgisi',
      channel: 'Kanal',
      voice: 'Ovoz',
      sms: 'SMS',
      telegram: 'Telegram',
      positive: 'Ijobiy',
      negative: 'Salbiy',
      neutral: 'Neytral',
      loadingInsights: 'Kotib ma\'lumotlarni yig\'moqda...',
      allTimeConversations: 'Barcha vaqtdagi suhbatlar',
      cumulativeTalkTime: 'Jami gaplashish vaqti',
      successfulOutcomes: 'muvaffaqiyatli natijalar',
      perConversation: 'Har bir suhbat uchun',
      averageCallDuration: 'O\'rtacha Qo\'ng\'iroq Davomiyligi',
      liveConversations: 'Kotibingiz hozir jonli suhbatlarni boshqarmoqda',
      quickActions: 'Tezkor Harakatlar',
      editWorkflows: 'Ish Oqimlarini Tahrirlash',
      viewSessions: 'Seanslarni Ko\'rish',
      detailedAnalytics: 'Batafsil Tahlil',
      systemStatus: 'Tizim Holati',
      aiScribe: 'AI Kotib',
      voiceSystem: 'Ovoz Tizimi',
      messaging: 'Xabar Almashish',
      online: 'Onlayn',
      ready: 'Tayyor',
      active: 'Faol',
      last24Hours: 'Oxirgi 24 Soat',
      sessions: 'Seanslar',
      successRate: 'Muvaffaqiyat Darajasi',
      avgDuration: 'O\'rtacha Davomiylik',
      sessionTypes: 'Seans Turlari',
      activeSessionsDesc: 'Kotibingiz hozir jonli suhbatlarni boshqarmoqda'
    },
    ru: {
      title: 'Обсерватория Писца',
      subtitle: 'Мониторинг Производительности Вашего ИИ Агента',
      totalCalls: 'Всего Обработано Звонков',
      totalDuration: 'Общая Продолжительность Звонков',
      positiveInteractions: 'Положительные Взаимодействия',
      negativeInteractions: 'Отрицательные Взаимодействия',
      activeSessions: 'Активные Сессии',
      recentActivity: 'Недавняя Активность',
      callHistory: 'История Звонков',
      lastUpdated: 'Последнее Обновление',
      noRecentActivity: 'Нет недавней активности',
      viewDetails: 'Просмотр Деталей',
      refreshData: 'Обновить Данные',
      sessionDetails: 'Детали Сессии',
      caller: 'Звонящий',
      duration: 'Продолжительность',
      outcome: 'Результат',
      summary: 'Резюме',
      timestamp: 'Временная Метка',
      channel: 'Канал',
      voice: 'Голос',
      sms: 'SMS',
      telegram: 'Telegram',
      positive: 'Положительный',
      negative: 'Отрицательный',
      neutral: 'Нейтральный',
      loadingInsights: 'Писец собирает данные...',
      allTimeConversations: 'Все разговоры за все время',
      cumulativeTalkTime: 'Общее время разговоров',
      successfulOutcomes: 'успешных результатов',
      perConversation: 'За разговор',
      averageCallDuration: 'Средняя Продолжительность Звонка',
      liveConversations: 'Ваш Писец в настоящее время обрабатывает живые разговоры',
      quickActions: 'Быстрые Действия',
      editWorkflows: 'Редактировать Рабочие Процессы',
      viewSessions: 'Просмотр Сессий',
      detailedAnalytics: 'Подробная Аналитика',
      systemStatus: 'Состояние Системы',
      aiScribe: 'ИИ Писец',
      voiceSystem: 'Голосовая Система',
      messaging: 'Сообщения',
      online: 'В сети',
      ready: 'Готов',
      active: 'Активен',
      last24Hours: 'Последние 24 Часа',
      sessions: 'Сессии',
      successRate: 'Уровень Успеха',
      avgDuration: 'Средняя Продолжительность',
      sessionTypes: 'Типы Сессий',
      activeSessionsDesc: 'Ваш Писец в настоящее время обрабатывает живые разговоры'
    }
  },

  // Subscription page
  subscription: {
    en: {
      title: 'Choose Your Scribe\'s Power',
      subtitle: 'Select the tier that matches your communication needs',
      currentPlan: 'Current Plan',
      selectPlan: 'Select Plan',
      upgrade: 'Upgrade',
      downgrade: 'Downgrade',
      features: 'Features',
      contextMemory: 'Context Memory',
      unlimited: 'Unlimited',
      minutes: 'minutes',
      hour: 'hour',
      tokens: 'tokens',
      apprentice: 'Apprentice',
      journeyman: 'Journeyman',
      masterScribe: 'Master Scribe',
      apprenticeDesc: 'Perfect for small businesses starting their AI journey',
      journeymanDesc: 'Ideal for growing businesses with moderate call volumes',
      masterScribeDesc: 'Ultimate power for enterprises with high-volume operations',
      paymentInstructions: 'Payment Instructions',
      bankDetails: 'Bank Details',
      cardNumber: 'Card Number',
      bankName: 'Bank Name',
      cardholder: 'Cardholder',
      amount: 'Amount',
      referenceCode: 'Reference Code',
      timeRemaining: 'Time Remaining',
      paymentSteps: 'Payment Steps',
      step1: '1. Transfer the exact amount to the card number above',
      step2: '2. Include the reference code in the transfer description',
      step3: '3. Wait for SMS confirmation (usually within 5 minutes)',
      step4: '4. Your subscription will be activated automatically',
      copyCode: 'Copy Reference Code',
      paymentExpired: 'Payment time expired. Please try again.',
      paymentSuccess: 'Payment instructions ready. Complete payment within 30 minutes.',
      paymentError: 'Payment initiation failed',
      processingPayment: 'Processing payment...',
      paymentHistory: 'Payment History',
      transactionId: 'Transaction ID',
      status: 'Status',
      date: 'Date',
      pending: 'Pending',
      completed: 'Completed',
      failed: 'Failed',
      cancelled: 'Cancelled',
      mostPopular: 'Most Popular',
      active: 'Active',
      nextBilling: 'Next billing',
      multiChannelSupport: 'Multi-Channel Support',
      multiChannelDesc: 'Voice, SMS, and Telegram integration',
      visualWorkflowBuilder: 'Visual Workflow Builder',
      visualWorkflowDesc: 'Drag-and-drop Invocation Editor',
      realtimeAnalytics: 'Real-time Analytics',
      realtimeAnalyticsDesc: 'Comprehensive performance insights',
      prioritySupport: 'Priority Support',
      prioritySupportDesc: 'Dedicated assistance channel',
      advancedFeatures: 'Advanced Features',
      advancedFeaturesDesc: 'Early access to new capabilities',
      subscribeNow: 'Subscribe Now',
      loading: 'The Scribe is preparing subscription options...'
    },
    uz: {
      title: 'Kotibingizning Kuchini Tanlang',
      subtitle: 'Aloqa ehtiyojlaringizga mos keladigan darajani tanlang',
      currentPlan: 'Joriy Reja',
      selectPlan: 'Rejani Tanlash',
      upgrade: 'Yangilash',
      downgrade: 'Pasaytirish',
      features: 'Xususiyatlar',
      contextMemory: 'Kontekst Xotirasi',
      unlimited: 'Cheksiz',
      minutes: 'daqiqa',
      hour: 'soat',
      tokens: 'tokenlar',
      apprentice: 'Shogird',
      journeyman: 'Hunarmand',
      masterScribe: 'Usta Kotib',
      apprenticeDesc: 'AI sayohatini boshlayotgan kichik bizneslar uchun mukammal',
      journeymanDesc: 'O\'rtacha qo\'ng\'iroq hajmiga ega o\'sib borayotgan bizneslar uchun ideal',
      masterScribeDesc: 'Yuqori hajmli operatsiyalarga ega korxonalar uchun yakuniy kuch',
      paymentInstructions: 'To\'lov Ko\'rsatmalari',
      bankDetails: 'Bank Ma\'lumotlari',
      cardNumber: 'Karta Raqami',
      bankName: 'Bank Nomi',
      cardholder: 'Karta Egasi',
      amount: 'Miqdor',
      referenceCode: 'Ma\'lumotnoma Kodi',
      timeRemaining: 'Qolgan Vaqt',
      paymentSteps: 'To\'lov Qadamlari',
      step1: '1. Yuqoridagi karta raqamiga aniq miqdorni o\'tkazing',
      step2: '2. O\'tkazma tavsifiga ma\'lumotnoma kodini kiriting',
      step3: '3. SMS tasdiqlashini kuting (odatda 5 daqiqa ichida)',
      step4: '4. Obunangiz avtomatik ravishda faollashtiriladi',
      copyCode: 'Ma\'lumotnoma Kodini Nusxalash',
      paymentExpired: 'To\'lov vaqti tugadi. Qaytadan urinib ko\'ring.',
      paymentSuccess: 'To\'lov ko\'rsatmalari tayyor. 30 daqiqa ichida to\'lovni amalga oshiring.',
      paymentError: 'To\'lov boshlanmadi',
      processingPayment: 'To\'lov qayta ishlanmoqda...',
      paymentHistory: 'To\'lov Tarixi',
      transactionId: 'Tranzaksiya ID',
      status: 'Holat',
      date: 'Sana',
      pending: 'Kutilmoqda',
      completed: 'Tugallangan',
      failed: 'Muvaffaqiyatsiz',
      cancelled: 'Bekor qilingan',
      mostPopular: 'Eng Mashhur',
      active: 'Faol',
      nextBilling: 'Keyingi to\'lov',
      multiChannelSupport: 'Ko\'p Kanalli Qo\'llab-quvvatlash',
      multiChannelDesc: 'Ovoz, SMS va Telegram integratsiyasi',
      visualWorkflowBuilder: 'Vizual Ish Oqimi Quruvchisi',
      visualWorkflowDesc: 'Sudrab-tashlash Chaqiriq Muharriri',
      realtimeAnalytics: 'Real vaqt Tahlili',
      realtimeAnalyticsDesc: 'Keng qamrovli ishlash ma\'lumotlari',
      prioritySupport: 'Ustuvor Qo\'llab-quvvatlash',
      prioritySupportDesc: 'Maxsus yordam kanali',
      advancedFeatures: 'Ilg\'or Xususiyatlar',
      advancedFeaturesDesc: 'Yangi imkoniyatlarga erta kirish',
      subscribeNow: 'Hozir Obuna Bo\'lish',
      loading: 'Kotib obuna variantlarini tayyorlamoqda...'
    },
    ru: {
      title: 'Выберите Силу Вашего Писца',
      subtitle: 'Выберите уровень, соответствующий вашим коммуникационным потребностям',
      currentPlan: 'Текущий План',
      selectPlan: 'Выбрать План',
      upgrade: 'Повысить',
      downgrade: 'Понизить',
      features: 'Функции',
      contextMemory: 'Контекстная Память',
      unlimited: 'Неограниченно',
      minutes: 'минут',
      hour: 'час',
      tokens: 'токенов',
      apprentice: 'Ученик',
      journeyman: 'Подмастерье',
      masterScribe: 'Мастер Писец',
      apprenticeDesc: 'Идеально для малого бизнеса, начинающего путь с ИИ',
      journeymanDesc: 'Идеально для растущего бизнеса с умеренным объемом звонков',
      masterScribeDesc: 'Максимальная мощность для предприятий с высокообъемными операциями',
      paymentInstructions: 'Инструкции по Оплате',
      bankDetails: 'Банковские Реквизиты',
      cardNumber: 'Номер Карты',
      bankName: 'Название Банка',
      cardholder: 'Держатель Карты',
      amount: 'Сумма',
      referenceCode: 'Код Ссылки',
      timeRemaining: 'Оставшееся Время',
      paymentSteps: 'Шаги Оплаты',
      step1: '1. Переведите точную сумму на номер карты выше',
      step2: '2. Включите код ссылки в описание перевода',
      step3: '3. Дождитесь SMS подтверждения (обычно в течение 5 минут)',
      step4: '4. Ваша подписка будет активирована автоматически',
      copyCode: 'Копировать Код Ссылки',
      paymentExpired: 'Время оплаты истекло. Пожалуйста, попробуйте снова.',
      paymentSuccess: 'Инструкции по оплате готовы. Завершите оплату в течение 30 минут.',
      paymentError: 'Инициация оплаты не удалась',
      processingPayment: 'Обработка платежа...',
      paymentHistory: 'История Платежей',
      transactionId: 'ID Транзакции',
      status: 'Статус',
      date: 'Дата',
      pending: 'В ожидании',
      completed: 'Завершено',
      failed: 'Неудачно',
      cancelled: 'Отменено',
      mostPopular: 'Самый Популярный',
      active: 'Активен',
      nextBilling: 'Следующий платеж',
      multiChannelSupport: 'Многоканальная Поддержка',
      multiChannelDesc: 'Интеграция голоса, SMS и Telegram',
      visualWorkflowBuilder: 'Визуальный Конструктор Рабочих Процессов',
      visualWorkflowDesc: 'Редактор Вызовов с перетаскиванием',
      realtimeAnalytics: 'Аналитика в Реальном Времени',
      realtimeAnalyticsDesc: 'Комплексная аналитика производительности',
      prioritySupport: 'Приоритетная Поддержка',
      prioritySupportDesc: 'Выделенный канал помощи',
      advancedFeatures: 'Расширенные Функции',
      advancedFeaturesDesc: 'Ранний доступ к новым возможностям',
      subscribeNow: 'Подписаться Сейчас',
      loading: 'Писец готовит варианты подписки...'
    }
  },

  // Invocation Editor
  invocationEditor: {
    en: {
      title: 'The Invocation Editor',
      subtitle: 'Craft Your Scribe\'s Behavior',
      canvas: 'Canvas',
      bookOfInvocations: 'Book of Invocations',
      saveScript: 'Save Script',
      loadScript: 'Load Script',
      clearCanvas: 'Clear Canvas',
      invocationPalette: 'Invocation Palette',
      configurationScroll: 'Configuration Scroll',
      theSpark: 'The Spark (Origin/Trigger)',
      theWorking: 'The Working (What Happens)',
      theConsequence: 'The Consequence (Outcome)',
      theNextStitch: 'The Next Stitch (What Should Happen Next)',
      paymentRitual: 'The Payment Ritual',
      messenger: 'The Messenger',
      telegramChanneler: 'The Telegram Channeler',
      finalWord: 'The Final Word',
      scribesReply: 'The Scribe\'s Reply',
      dragToCanvas: 'Drag invocations to the canvas to build your workflow',
      connectNodes: 'Connect nodes to define the flow of logic',
      doubleClickToEdit: 'Double-click nodes to configure their behavior',
      scriptSaved: 'Script saved successfully',
      scriptLoaded: 'Script loaded successfully',
      canvasCleared: 'Canvas cleared',
      invalidConnection: 'Invalid connection',
      nodeConfigured: 'Node configured successfully'
    },
    uz: {
      title: 'Chaqiriq Muharriri',
      subtitle: 'Kotibingizning Xatti-harakatini Yarating',
      canvas: 'Kanvas',
      bookOfInvocations: 'Chaqiriqlar Kitobi',
      saveScript: 'Skriptni Saqlash',
      loadScript: 'Skriptni Yuklash',
      clearCanvas: 'Kanvasni Tozalash',
      invocationPalette: 'Chaqiriq Palitasi',
      configurationScroll: 'Konfiguratsiya Varaqasi',
      theSpark: 'Uchqun (Kelib chiqish/Tetik)',
      theWorking: 'Ish (Nima sodir bo\'ladi)',
      theConsequence: 'Oqibat (Natija)',
      theNextStitch: 'Keyingi Tikuv (Keyin nima bo\'lishi kerak)',
      paymentRitual: 'To\'lov Marosimi',
      messenger: 'Xabarchi',
      telegramChanneler: 'Telegram Kanalchi',
      finalWord: 'Yakuniy So\'z',
      scribesReply: 'Kotibning Javobi',
      dragToCanvas: 'Ish oqimini yaratish uchun chaqiriqlarni kanvasga torting',
      connectNodes: 'Mantiq oqimini belgilash uchun tugunlarni ulang',
      doubleClickToEdit: 'Xatti-harakatlarini sozlash uchun tugunlarni ikki marta bosing',
      scriptSaved: 'Skript muvaffaqiyatli saqlandi',
      scriptLoaded: 'Skript muvaffaqiyatli yuklandi',
      canvasCleared: 'Kanvas tozalandi',
      invalidConnection: 'Noto\'g\'ri ulanish',
      nodeConfigured: 'Tugun muvaffaqiyatli sozlandi'
    },
    ru: {
      title: 'Редактор Вызовов',
      subtitle: 'Создайте Поведение Вашего Писца',
      canvas: 'Холст',
      bookOfInvocations: 'Книга Вызовов',
      saveScript: 'Сохранить Скрипт',
      loadScript: 'Загрузить Скрипт',
      clearCanvas: 'Очистить Холст',
      invocationPalette: 'Палитра Вызовов',
      configurationScroll: 'Свиток Конфигурации',
      theSpark: 'Искра (Происхождение/Триггер)',
      theWorking: 'Работа (Что Происходит)',
      theConsequence: 'Последствие (Результат)',
      theNextStitch: 'Следующий Стежок (Что Должно Произойти Далее)',
      paymentRitual: 'Ритуал Оплаты',
      messenger: 'Посланник',
      telegramChanneler: 'Telegram Канальщик',
      finalWord: 'Последнее Слово',
      scribesReply: 'Ответ Писца',
      dragToCanvas: 'Перетащите вызовы на холст для создания рабочего процесса',
      connectNodes: 'Соедините узлы для определения потока логики',
      doubleClickToEdit: 'Дважды щелкните узлы для настройки их поведения',
      scriptSaved: 'Скрипт успешно сохранен',
      scriptLoaded: 'Скрипт успешно загружен',
      canvasCleared: 'Холст очищен',
      invalidConnection: 'Недопустимое соединение',
      nodeConfigured: 'Узел успешно настроен'
    }
  },

  // Navigation
  navigation: {
    en: {
      dashboard: 'Dashboard',
      invocationEditor: 'Invocation Editor',
      sessions: 'Sessions',
      statistics: 'Statistics',
      subscription: 'Subscription',
      profile: 'Profile',
      settings: 'Settings',
      logout: 'Logout'
    },
    uz: {
      dashboard: 'Boshqaruv Paneli',
      invocationEditor: 'Chaqiriq Muharriri',
      sessions: 'Seanslar',
      statistics: 'Statistika',
      subscription: 'Obuna',
      profile: 'Profil',
      settings: 'Sozlamalar',
      logout: 'Chiqish'
    },
    ru: {
      dashboard: 'Панель Управления',
      invocationEditor: 'Редактор Вызовов',
      sessions: 'Сессии',
      statistics: 'Статистика',
      subscription: 'Подписка',
      profile: 'Профиль',
      settings: 'Настройки',
      logout: 'Выйти'
    }
  },

  // Time and date formatting
  time: {
    en: {
      seconds: 'seconds',
      minutes: 'minutes',
      hours: 'hours',
      days: 'days',
      weeks: 'weeks',
      months: 'months',
      years: 'years',
      ago: 'ago',
      justNow: 'just now',
      today: 'today',
      yesterday: 'yesterday',
      tomorrow: 'tomorrow'
    },
    uz: {
      seconds: 'soniya',
      minutes: 'daqiqa',
      hours: 'soat',
      days: 'kun',
      weeks: 'hafta',
      months: 'oy',
      years: 'yil',
      ago: 'oldin',
      justNow: 'hozir',
      today: 'bugun',
      yesterday: 'kecha',
      tomorrow: 'ertaga'
    },
    ru: {
      seconds: 'секунд',
      minutes: 'минут',
      hours: 'часов',
      days: 'дней',
      weeks: 'недель',
      months: 'месяцев',
      years: 'лет',
      ago: 'назад',
      justNow: 'только что',
      today: 'сегодня',
      yesterday: 'вчера',
      tomorrow: 'завтра'
    }
  },

  // Support Chat
  support: {
    en: {
      chatTitle: 'AI Support Assistant',
      chatSubtitle: 'Ask me anything about Aetherium',
      placeholder: 'Type your question here...',
      send: 'Send',
      minimize: 'Minimize',
      close: 'Close',
      typing: 'Assistant is typing...',
      error: 'Sorry, I encountered an error. Please try again.',
      welcome: 'Hello! I\'m your AI assistant. How can I help you with Aetherium today?',
      helpButton: 'Need Help?',
      poweredBy: 'Powered by Gemini AI',
      connecting: 'Connecting...',
      reconnect: 'Reconnect',
      offline: 'You appear to be offline',
      clearChat: 'Clear Chat',
      newConversation: 'New Conversation'
    },
    uz: {
      chatTitle: 'AI Yordam Yordamchisi',
      chatSubtitle: 'Aetherium haqida har qanday savol bering',
      placeholder: 'Savolingizni shu yerga yozing...',
      send: 'Yuborish',
      minimize: 'Kichraytirish',
      close: 'Yopish',
      typing: 'Yordamchi yozmoqda...',
      error: 'Kechirasiz, xatolik yuz berdi. Iltimos, qayta urinib ko\'ring.',
      welcome: 'Salom! Men sizning AI yordamchingizman. Bugun Aetherium bo\'yicha qanday yordam bera olaman?',
      helpButton: 'Yordam kerakmi?',
      poweredBy: 'Gemini AI tomonidan quvvatlanadi',
      connecting: 'Ulanmoqda...',
      reconnect: 'Qayta ulanish',
      offline: 'Siz oflayn ko\'rinasiz',
      clearChat: 'Chatni Tozalash',
      newConversation: 'Yangi Suhbat'
    },
    ru: {
      chatTitle: 'AI Помощник Поддержки',
      chatSubtitle: 'Задайте любой вопрос об Aetherium',
      placeholder: 'Введите ваш вопрос здесь...',
      send: 'Отправить',
      minimize: 'Свернуть',
      close: 'Закрыть',
      typing: 'Помощник печатает...',
      error: 'Извините, произошла ошибка. Пожалуйста, попробуйте снова.',
      welcome: 'Привет! Я ваш AI помощник. Как я могу помочь вам с Aetherium сегодня?',
      helpButton: 'Нужна помощь?',
      poweredBy: 'Работает на Gemini AI',
      connecting: 'Подключение...',
      reconnect: 'Переподключиться',
      offline: 'Вы находитесь в автономном режиме',
      clearChat: 'Очистить Чат',
      newConversation: 'Новый Разговор'
    }
  },

  // Statistics page
  statistics: {
    en: {
      title: 'The Scribe\'s Analytics',
      subtitle: 'Deep insights into your AI communication performance',
      period: 'Period',
      last7Days: 'Last 7 days',
      last30Days: 'Last 30 days',
      last90Days: 'Last 90 days',
      loadingAnalysis: 'The Scribe is analyzing the data...',
      totalCalls: 'Total Calls',
      positiveInteractions: 'Positive Interactions',
      totalDuration: 'Total Duration',
      currentPeriod: 'Current Period',
      previousPeriod: 'Previous Period',
      dailyPerformance: 'Daily Performance Trends',
      hourlyActivity: 'Hourly Activity Distribution',
      outcomeDistribution: 'Outcome Distribution',
      durationAnalysis: 'Call Duration Analysis',
      performanceInsights: 'Performance Insights',
      peakHours: 'Peak Hours',
      successRate: 'Success Rate',
      avgDuration: 'Avg Duration',
      totalSessions: 'Total Sessions',
      calls: 'Calls',
      minutes: 'minutes',
      hour: 'Hour'
    },
    uz: {
      title: 'Kotibning Analitikasi',
      subtitle: 'AI aloqa samaradorligingizga chuqur nazar',
      period: 'Davr',
      last7Days: 'Oxirgi 7 kun',
      last30Days: 'Oxirgi 30 kun',
      last90Days: 'Oxirgi 90 kun',
      loadingAnalysis: 'Kotib ma\'lumotlarni tahlil qilmoqda...',
      totalCalls: 'Jami Qo\'ng\'iroqlar',
      positiveInteractions: 'Ijobiy Muloqotlar',
      totalDuration: 'Jami Davomiylik',
      currentPeriod: 'Joriy Davr',
      previousPeriod: 'Oldingi Davr',
      dailyPerformance: 'Kunlik Ishlash Tendentsiyalari',
      hourlyActivity: 'Soatlik Faoliyat Taqsimoti',
      outcomeDistribution: 'Natija Taqsimoti',
      durationAnalysis: 'Qo\'ng\'iroq Davomiyligi Tahlili',
      performanceInsights: 'Ishlash Tushunchalari',
      peakHours: 'Eng Yuqori Soatlar',
      successRate: 'Muvaffaqiyat Darajasi',
      avgDuration: 'O\'rtacha Davomiylik',
      totalSessions: 'Jami Seanslar',
      calls: 'Qo\'ng\'iroqlar',
      minutes: 'daqiqa',
      hour: 'Soat'
    },
    ru: {
      title: 'Аналитика Писца',
      subtitle: 'Глубокие инсайты в производительность вашего ИИ общения',
      period: 'Период',
      last7Days: 'Последние 7 дней',
      last30Days: 'Последние 30 дней',
      last90Days: 'Последние 90 дней',
      loadingAnalysis: 'Писец анализирует данные...',
      totalCalls: 'Всего Звонков',
      positiveInteractions: 'Положительные Взаимодействия',
      totalDuration: 'Общая Продолжительность',
      currentPeriod: 'Текущий Период',
      previousPeriod: 'Предыдущий Период',
      dailyPerformance: 'Ежедневные Тенденции Производительности',
      hourlyActivity: 'Почасовое Распределение Активности',
      outcomeDistribution: 'Распределение Результатов',
      durationAnalysis: 'Анализ Продолжительности Звонков',
      performanceInsights: 'Инсайты Производительности',
      peakHours: 'Пиковые Часы',
      successRate: 'Уровень Успеха',
      avgDuration: 'Средняя Продолжительность',
      totalSessions: 'Всего Сессий',
      calls: 'Звонки',
      minutes: 'минут',
      hour: 'Час'
    }
  },

  // Sessions page
  sessions: {
    en: {
      title: 'Session History',
      subtitle: 'Review all conversations and interactions',
      loadingSessions: 'Loading session history...',
      noSessions: 'No sessions found',
      searchPlaceholder: 'Search sessions...',
      filterByType: 'Filter by type',
      filterByStatus: 'Filter by status',
      allTypes: 'All Types',
      allStatuses: 'All Statuses',
      voice: 'Voice',
      sms: 'SMS',
      telegram: 'Telegram',
      completed: 'Completed',
      active: 'Active',
      failed: 'Failed',
      pending: 'Pending',
      sessionId: 'Session ID',
      caller: 'Caller',
      duration: 'Duration',
      status: 'Status',
      outcome: 'Outcome',
      timestamp: 'Timestamp',
      viewDetails: 'View Details',
      hideDetails: 'Hide Details',
      sessionDetails: 'Session Details',
      conversationHistory: 'Conversation History',
      summary: 'Summary',
      exportSessions: 'Export Sessions',
      refreshSessions: 'Refresh Sessions',
      loadMore: 'Load More',
      positive: 'Positive',
      negative: 'Negative',
      neutral: 'Neutral',
      unknown: 'Unknown'
    },
    uz: {
      title: 'Seanslar Tarixi',
      subtitle: 'Barcha suhbatlar va muloqotlarni ko\'rib chiqing',
      loadingSessions: 'Seanslar tarixi yuklanmoqda...',
      noSessions: 'Seanslar topilmadi',
      searchPlaceholder: 'Seanslarni qidirish...',
      filterByType: 'Tur bo\'yicha filtrlash',
      filterByStatus: 'Holat bo\'yicha filtrlash',
      allTypes: 'Barcha Turlar',
      allStatuses: 'Barcha Holatlar',
      voice: 'Ovoz',
      sms: 'SMS',
      telegram: 'Telegram',
      completed: 'Tugallangan',
      active: 'Faol',
      failed: 'Muvaffaqiyatsiz',
      pending: 'Kutilmoqda',
      sessionId: 'Seans ID',
      caller: 'Qo\'ng\'iroq Qiluvchi',
      duration: 'Davomiylik',
      status: 'Holat',
      outcome: 'Natija',
      timestamp: 'Vaqt Belgisi',
      viewDetails: 'Tafsilotlarni Ko\'rish',
      hideDetails: 'Tafsilotlarni Yashirish',
      sessionDetails: 'Seans Tafsilotlari',
      conversationHistory: 'Suhbat Tarixi',
      summary: 'Xulosa',
      exportSessions: 'Seanslarni Eksport Qilish',
      refreshSessions: 'Seanslarni Yangilash',
      loadMore: 'Ko\'proq Yuklash',
      positive: 'Ijobiy',
      negative: 'Salbiy',
      neutral: 'Neytral',
      unknown: 'Noma\'lum'
    },
    ru: {
      title: 'История Сессий',
      subtitle: 'Просмотр всех разговоров и взаимодействий',
      loadingSessions: 'Загрузка истории сессий...',
      noSessions: 'Сессии не найдены',
      searchPlaceholder: 'Поиск сессий...',
      filterByType: 'Фильтр по типу',
      filterByStatus: 'Фильтр по статусу',
      allTypes: 'Все Типы',
      allStatuses: 'Все Статусы',
      voice: 'Голос',
      sms: 'SMS',
      telegram: 'Telegram',
      completed: 'Завершено',
      active: 'Активно',
      failed: 'Неудачно',
      pending: 'Ожидание',
      sessionId: 'ID Сессии',
      caller: 'Звонящий',
      duration: 'Продолжительность',
      status: 'Статус',
      outcome: 'Результат',
      timestamp: 'Временная Метка',
      viewDetails: 'Просмотр Деталей',
      hideDetails: 'Скрыть Детали',
      sessionDetails: 'Детали Сессии',
      conversationHistory: 'История Разговора',
      summary: 'Резюме',
      exportSessions: 'Экспорт Сессий',
      refreshSessions: 'Обновить Сессии',
      loadMore: 'Загрузить Еще',
      positive: 'Положительный',
      negative: 'Отрицательный',
      neutral: 'Нейтральный',
      unknown: 'Неизвестно'
    }
  }
}

// Translation utility functions
export const getTranslation = (category, key, language = DEFAULT_LANGUAGE) => {
  try {
    const categoryTranslations = translations[category]
    if (!categoryTranslations) {
      console.warn(`Translation category '${category}' not found`)
      return key
    }

    const languageTranslations = categoryTranslations[language]
    if (!languageTranslations) {
      console.warn(`Language '${language}' not found in category '${category}', falling back to ${DEFAULT_LANGUAGE}`)
      return categoryTranslations[DEFAULT_LANGUAGE]?.[key] || key
    }

    const translation = languageTranslations[key]
    if (!translation) {
      console.warn(`Translation key '${key}' not found in '${category}.${language}', falling back to ${DEFAULT_LANGUAGE}`)
      return categoryTranslations[DEFAULT_LANGUAGE]?.[key] || key
    }

    return translation
  } catch (error) {
    console.error('Translation error:', error)
    return key
  }
}

// Shorthand function for easier usage
export const t = getTranslation

// Get all translations for a category in a specific language
export const getCategoryTranslations = (category, language = DEFAULT_LANGUAGE) => {
  return translations[category]?.[language] || {}
}

// Check if a language is supported
export const isLanguageSupported = (language) => {
  return Object.keys(SUPPORTED_LANGUAGES).includes(language)
}

// Get browser language preference
export const getBrowserLanguage = () => {
  const browserLang = navigator.language || navigator.userLanguage
  const langCode = browserLang.split('-')[0].toLowerCase()
  return isLanguageSupported(langCode) ? langCode : DEFAULT_LANGUAGE
}

// Format time with translations
export const formatTimeWithTranslation = (seconds, language = DEFAULT_LANGUAGE) => {
  const timeTranslations = translations.time[language] || translations.time[DEFAULT_LANGUAGE]
  
  if (seconds < 60) {
    return `${seconds} ${timeTranslations.seconds}`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    return `${minutes} ${timeTranslations.minutes}`
  } else if (seconds < 86400) {
    const hours = Math.floor(seconds / 3600)
    return `${hours} ${timeTranslations.hours}`
  } else {
    const days = Math.floor(seconds / 86400)
    return `${days} ${timeTranslations.days}`
  }
}

// Format relative time (e.g., "5 minutes ago")
export const formatRelativeTime = (date, language = DEFAULT_LANGUAGE) => {
  const timeTranslations = translations.time[language] || translations.time[DEFAULT_LANGUAGE]
  const now = new Date()
  const diffInSeconds = Math.floor((now - new Date(date)) / 1000)
  
  if (diffInSeconds < 60) {
    return timeTranslations.justNow
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60)
    return `${minutes} ${timeTranslations.minutes} ${timeTranslations.ago}`
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600)
    return `${hours} ${timeTranslations.hours} ${timeTranslations.ago}`
  } else if (diffInSeconds < 604800) {
    const days = Math.floor(diffInSeconds / 86400)
    return `${days} ${timeTranslations.days} ${timeTranslations.ago}`
  } else {
    return new Date(date).toLocaleDateString()
  }
}