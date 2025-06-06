# Aetherium Manual Translation System

## Overview

The Aetherium platform implements a comprehensive manual translation system that supports multiple languages while maintaining the thematic integrity of "The Scribe's Desk" aesthetic. All translations are manually crafted to ensure cultural authenticity and consistency with the platform's unique character.

## Supported Languages

- **English (en)** - Default language
- **Uzbek (uz)** - O'zbekcha
- **Russian (ru)** - Русский

## Architecture

### Core Components

1. **Translation Data** (`/frontend/src/utils/translations.js`)
   - Centralized translation storage
   - Organized by categories and languages
   - Utility functions for translation retrieval

2. **Translation Hook** (`/frontend/src/hooks/useTranslation.jsx`)
   - React context and hook for translation management
   - Language switching functionality
   - Persistent language preferences

3. **Language Selector Component**
   - Dropdown component for language switching
   - Styled to match coffee paper theme
   - Available in all major UI areas

## Translation Structure

### Category Organization

```javascript
translations = {
  common: {        // Shared UI elements
    en: { ... },
    uz: { ... },
    ru: { ... }
  },
  auth: {          // Authentication pages
    en: { ... },
    uz: { ... },
    ru: { ... }
  },
  dashboard: {     // Dashboard and statistics
    en: { ... },
    uz: { ... },
    ru: { ... }
  },
  subscription: {  // Payment and subscription
    en: { ... },
    uz: { ... },
    ru: { ... }
  },
  navigation: {    // Menu and navigation
    en: { ... },
    uz: { ... },
    ru: { ... }
  },
  invocationEditor: { // Workflow editor
    en: { ... },
    uz: { ... },
    ru: { ... }
  },
  companyNumber: { // Company number page
    en: { ... },
    uz: { ... },
    ru: { ... }
  },
  time: {          // Time and date formatting
    en: { ... },
    uz: { ... },
    ru: { ... }
  }
}
```

### Key Translation Categories

#### Common Translations
- Basic UI elements (save, cancel, loading, etc.)
- Brand names (Aetherium, Scribe)
- Universal actions and states

#### Authentication Translations
- Login and registration forms
- Validation messages
- Verification process
- Password requirements

#### Dashboard Translations
- Statistics labels
- Activity descriptions
- Status indicators
- Time-based content

#### Subscription Translations
- Tier names and descriptions
- Payment instructions
- Bank details and processes
- Transaction statuses

#### Navigation Translations
- Menu items
- Page titles
- Breadcrumbs

## Usage

### Basic Translation

```jsx
import { useTranslation } from '../hooks/useTranslation'

const MyComponent = () => {
  const { t } = useTranslation()
  
  return (
    <div>
      <h1>{t('common', 'aetherium')}</h1>
      <p>{t('auth', 'loginTitle')}</p>
    </div>
  )
}
```

### Language Switching

```jsx
import { useTranslation, LanguageSelector } from '../hooks/useTranslation'

const Header = () => {
  const { currentLanguage, changeLanguage } = useTranslation()
  
  return (
    <div>
      <LanguageSelector className="language-selector" />
      <span>Current: {currentLanguage}</span>
    </div>
  )
}
```

### Time Formatting

```jsx
const { formatTime, formatRelative } = useTranslation()

// Format duration
const duration = formatTime(3600) // "1 hour" / "1 soat" / "1 час"

// Format relative time
const relative = formatRelative(date) // "5 minutes ago" / "5 daqiqa oldin" / "5 минут назад"
```

### Form Validation

```jsx
const { t } = useTranslation()

const validationRules = {
  email: {
    required: t('auth', 'emailRequired'),
    pattern: {
      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
      message: t('auth', 'emailInvalid')
    }
  }
}
```

## Implementation Details

### Language Detection

1. **Saved Preference**: Checks localStorage for `aetherium_language`
2. **Browser Language**: Falls back to browser language preference
3. **Default Fallback**: Uses English if no supported language detected

### Persistence

- Language preference saved to localStorage
- Persists across browser sessions
- Immediate application without page reload

### Fallback Strategy

```javascript
const getTranslation = (category, key, language = DEFAULT_LANGUAGE) => {
  // 1. Try requested language
  // 2. Fall back to default language
  // 3. Return key if no translation found
  // 4. Log warnings for missing translations
}
```

## Styling

### Language Selector Styles

```css
.language-selector {
  background: var(--coffee-beige);
  border: 1px solid var(--coffee-tan);
  border-radius: 4px;
  color: var(--coffee-brown);
  font-family: var(--font-body);
  transition: all 0.3s ease;
}

.language-selector:hover {
  border-color: var(--coffee-sienna);
  background: var(--coffee-khaki);
}
```

### Theme Integration

- Matches coffee paper aesthetic
- Consistent with existing UI elements
- Responsive design support
- Accessibility considerations

## Translation Guidelines

### Manual Translation Principles

1. **Cultural Authenticity**: Translations reflect local cultural context
2. **Thematic Consistency**: Maintains "Scribe's Desk" character
3. **Technical Accuracy**: Preserves technical meaning
4. **User Experience**: Prioritizes clarity and usability

### Language-Specific Considerations

#### Uzbek (uz)
- Uses Latin script
- Formal tone for business context
- Technical terms adapted to local usage
- Cultural references appropriate for Uzbekistan

#### Russian (ru)
- Formal business language
- Technical terminology in Russian
- Appropriate for CIS region users
- Maintains professional tone

#### English (en)
- Base language for all translations
- Technical documentation standard
- International business English
- Thematic language preserved

## Testing

### Translation Test Page

Access `/translation-test` to verify:
- All translation categories loaded
- Language switching functionality
- Time formatting in different languages
- Missing translation detection

### Manual Testing Checklist

- [ ] All pages display correctly in each language
- [ ] Language selector works on all pages
- [ ] Form validation messages translated
- [ ] Time and date formatting appropriate
- [ ] No missing translation warnings in console
- [ ] Language preference persists across sessions

## Maintenance

### Adding New Translations

1. **Add to translations.js**:
   ```javascript
   newCategory: {
     en: { newKey: 'English text' },
     uz: { newKey: 'O\'zbek matni' },
     ru: { newKey: 'Русский текст' }
   }
   ```

2. **Use in components**:
   ```jsx
   {t('newCategory', 'newKey')}
   ```

3. **Test all languages**:
   - Verify display in UI
   - Check text length and layout
   - Validate cultural appropriateness

### Translation Updates

1. Update all three languages simultaneously
2. Maintain consistent meaning across languages
3. Test UI layout with new text lengths
4. Update documentation if needed

## Backend Integration

### API Response Localization

While the frontend handles UI translations, API responses can be localized:

```javascript
// Send language preference in API requests
const apiCall = async () => {
  const response = await fetch('/api/endpoint', {
    headers: {
      'Accept-Language': currentLanguage
    }
  })
}
```

### SMS and Voice Localization

The manual payment system and voice interactions use language detection:

```python
# Backend language detection for SMS/voice
detected_language = context.variables.get("detected_language", "uz")
instruction_texts = {
    "uz": "O'zbek tilidagi matn",
    "ru": "Текст на русском языке", 
    "en": "English text"
}
instruction_text = instruction_texts.get(detected_language, instruction_texts["uz"])
```

## Security Considerations

- No sensitive data in translation files
- Client-side language preference only
- Server-side validation language-agnostic
- Error messages don't expose system details

## Performance

- Translations loaded once at app startup
- No runtime translation API calls
- Minimal bundle size impact
- Efficient language switching

## Accessibility

- Language selector keyboard navigable
- Screen reader compatible
- High contrast mode support
- Reduced motion respect

## Future Enhancements

### Potential Additions

1. **Additional Languages**: Arabic, Turkish, Chinese
2. **Regional Variants**: Different Uzbek dialects
3. **Dynamic Loading**: Load translations on demand
4. **Translation Management**: Admin interface for updates
5. **Pluralization**: Advanced plural form handling
6. **RTL Support**: Right-to-left language support

### Integration Opportunities

1. **Voice Recognition**: Multi-language speech processing
2. **SMS Processing**: Language-aware message analysis
3. **Customer Support**: Localized help content
4. **Documentation**: Multi-language user guides

## Conclusion

The Aetherium manual translation system provides comprehensive multi-language support while maintaining the platform's unique character and ensuring cultural authenticity. The system is designed for maintainability, performance, and user experience across all supported languages.

The manual approach ensures quality control and thematic consistency that automated translation services cannot provide, making it essential for the platform's artisanal character and professional presentation in diverse markets.