# Aetherium Architecture Documentation

## System Overview

Aetherium is a comprehensive AI-powered call center platform designed to handle 40 concurrent voice, SMS, and Telegram interactions through a sophisticated microservices architecture.

## Core Principles

### The Artisan's Mandate
- **No Testing Paradigm**: Built with meticulous craftsmanship to work correctly from first deployment
- **Single Command Deployment**: Entire system operational with `docker-compose up -d`
- **Coffee Paper Aesthetic**: Unique visual theme throughout the user interface
- **Multimodal AI**: Advanced audio and text processing via Gemini 2.0 Flash

## Service Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AETHERIUM PLATFORM                      │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React)     │  Backend API (FastAPI)                 │
│  - Coffee Paper UI    │  - Authentication                      │
│  - Invocation Editor  │  - Workflow Engine                     │
│  - Real-time Stats    │  - AI Integration                      │
│  - WebSocket Client   │  - Payment Processing                  │
├─────────────────────────────────────────────────────────────────┤
│  Modem Manager        │  Telegram Bot        │  Database       │
│  - GSM Control        │  - Bot Interface     │  - PostgreSQL   │
│  - Audio Processing   │  - Message Routing   │  - 15+ Tables   │
│  - SMS Handling       │  - User Linking      │  - Triggers     │
│  - Call Management    │  - Workflow Trigger  │  - Functions    │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

### Voice Call Flow
```
Incoming Call → GSM Modem → Modem Manager → Audio Processing Pipeline
     ↓
Voice Activity Detection → Noise Reduction → Speech-to-Text
     ↓
Backend API → Workflow Engine → Gemini AI → Response Generation
     ↓
Text-to-Speech → Audio Enhancement → GSM Modem → Caller
```

### SMS Flow
```
Incoming SMS → GSM Modem → SMS Handler → Backend API
     ↓
User Identification → Session Management → Workflow Engine
     ↓
AI Processing → Response Generation → SMS Handler → GSM Modem
```

### Workflow Execution Flow
```
User Input → Session Context → Workflow Engine → Invocation Execution
     ↓
Payment Ritual | Send SMS | AI Response | Telegram | Hang Up
     ↓
Result Processing → Next Node Selection → Continue/Complete
```

## Component Details

### Frontend (React)

**Location**: `/frontend/`

**Key Features**:
- Coffee paper aesthetic with custom CSS
- Visual workflow builder (Invocation Editor)
- Real-time statistics dashboard
- WebSocket integration for live updates
- Sound effects for user interactions

**Technology Stack**:
- React 18 with hooks
- Tailwind CSS for styling
- React Query for data fetching
- React Router for navigation
- Recharts for analytics visualization

**Key Components**:
```
src/
├── components/
│   ├── Layout.jsx              # Main layout with navigation
│   ├── ProtectedRoute.jsx      # Authentication guard
│   └── InvocationEditor/       # Visual workflow builder
├── pages/
│   ├── DashboardPage.jsx       # Main dashboard
│   ├── InvocationEditorPage.jsx # Workflow editor
│   ├── StatisticsPage.jsx      # Analytics
│   └── SessionsPage.jsx        # Call history
├── hooks/
│   ├── useAuth.jsx             # Authentication state
│   └── useSound.jsx            # Audio feedback
└── services/
    └── api.js                  # API client
```

### Backend API (FastAPI)

**Location**: `/backend/`

**Key Features**:
- JWT-based authentication
- Workflow execution engine
- AI integration (Gemini, Edge TTS)
- Payment processing (Click API)
- Real-time WebSocket updates

**Technology Stack**:
- FastAPI with async/await
- SQLAlchemy ORM with PostgreSQL
- Pydantic for data validation
- JWT for authentication
- WebSocket for real-time updates

**Architecture**:
```
backend/
├── main.py                     # FastAPI application
├── database/
│   ├── connection.py           # Database connection
│   └── init.sql               # Schema initialization
├── models/                     # SQLAlchemy models
├── routers/                    # API endpoints
├── services/                   # Business logic
│   ├── gemini_client.py        # AI integration
│   ├── edge_tts_client.py      # Text-to-speech
│   ├── workflow_engine.py      # Workflow execution
│   └── payment_service.py      # Payment processing
└── utils/                      # Utilities
```

### Modem Manager (Python)

**Location**: `/modem-manager/`

**Key Features**:
- GSM modem control via AT commands
- Audio processing pipeline
- Voice activity detection
- Noise reduction and enhancement
- Call and SMS handling

**Technology Stack**:
- PySerial for modem communication
- PyAudio for audio capture/playback
- WebRTC VAD for voice detection
- Librosa for audio processing
- FastAPI for service interface

**Components**:
```
modem-manager/
├── main.py                     # Service entry point
├── device_manager.py           # USB device detection
├── modem_controller.py         # AT command interface
├── audio_processor.py          # Audio enhancement
├── call_handler.py             # Voice call management
└── sms_handler.py              # SMS processing
```

### Database Schema

**Technology**: PostgreSQL 15

**Key Tables**:
- `users` - User accounts and authentication
- `subscription_tiers` - Service tier definitions
- `user_subscriptions` - Active subscriptions
- `scribe_workflows` - Workflow definitions
- `communication_sessions` - Call/SMS sessions
- `session_messages` - Conversation history
- `call_statistics` - Performance metrics
- `payment_transactions` - Payment records
- `telegram_chats` - Telegram integrations
- `dream_journal` - AI meta-analysis

**Advanced Features**:
- Triggers for automatic statistics updates
- Functions for complex queries
- JSONB for flexible workflow storage
- Encryption for sensitive data

## AI Integration

### Gemini 2.0 Flash Integration

**Multimodal Processing**:
- Simultaneous audio and text analysis
- Context-aware conversation management
- Language detection and response
- Structured command parsing

**Implementation**:
```python
# Multimodal request structure
request = {
    "audio_data": base64_encoded_audio,
    "prompt_text": context + user_input + instructions,
    "model": "gemini-2.0-flash",
    "temperature": 0.7
}
```

### Edge TTS Integration

**Dynamic Voice Modulation**:
- Language-specific voice selection
- Pitch and rate adjustment based on context
- Emotional expression mapping
- High-quality speech synthesis

**Voice Settings**:
```python
voice_settings = {
    "language": detected_language,
    "voice": selected_voice_id,
    "pitch": mood_to_pitch_mapping[detected_mood],
    "rate": context_to_rate_mapping[conversation_state]
}
```

## Workflow Engine

### Invocation Types

1. **The Payment Ritual** (`payment_ritual`)
   - Complex payment flow with SMS confirmation
   - Bank card number encryption
   - Reassurance script for skeptical users
   - AI-powered SMS analysis

2. **The Messenger** (`send_sms`)
   - SMS sending via GSM modems
   - Dynamic content with variables
   - Delivery confirmation

3. **The Telegram Channeler** (`telegram_send`)
   - Telegram message sending
   - Bot integration
   - Multi-channel coordination

4. **The Final Word** (`hang_up`)
   - Call termination
   - Session cleanup
   - Statistics recording

5. **The Scribe's Reply** (`ai_response`)
   - AI conversation generation
   - Context-aware responses
   - Multimodal processing

### Execution Engine

**State Management**:
```python
@dataclass
class ExecutionContext:
    session_id: int
    workflow_id: int
    current_node_id: str
    execution_history: List[Dict]
    variables: Dict[str, Any]
    status: ExecutionStatus
```

**Node Execution**:
1. Load workflow definition
2. Find current node
3. Execute invocation handler
4. Process result
5. Determine next nodes
6. Continue or wait

## Security Architecture

### Authentication & Authorization
- JWT tokens with configurable expiration
- Password hashing with bcrypt
- Role-based access control
- Session management

### Data Protection
- AES encryption for sensitive data
- Secure API key management
- Input validation and sanitization
- SQL injection prevention

### Network Security
- HTTPS enforcement in production
- CORS configuration
- Rate limiting
- Request/response logging

## Performance Considerations

### Concurrency
- 40 simultaneous voice sessions
- Async/await throughout the stack
- Connection pooling for database
- Queue-based audio processing

### Memory Management
- 64GB RAM allocation
- Efficient audio buffering
- Context length management by subscription tier
- Garbage collection optimization

### Storage
- NVMe SSD for high-speed access
- Database query optimization
- Audio file temporary storage
- Log rotation and archival

## Monitoring & Observability

### Logging
- Structured logging with JSON format
- Service-specific log files
- Centralized log aggregation
- Error tracking and alerting

### Metrics
- Real-time performance statistics
- Call quality metrics
- System resource monitoring
- Business intelligence dashboards

### Health Checks
- Service availability monitoring
- Database connection health
- Hardware status verification
- API endpoint validation

## Deployment Architecture

### Container Orchestration
```yaml
services:
  database:          # PostgreSQL with persistent storage
  backend-api:       # FastAPI with business logic
  web-frontend:      # React SPA with Nginx
  modem-manager:     # Hardware interface service
  telegram-bot:      # Telegram integration
```

### Hardware Integration
- PCI USB expansion for 40 modems
- Dual USB connections per modem
- NVIDIA Tesla V100 for AI processing
- Enterprise-grade storage

### Network Configuration
- Internal Docker network
- Port mapping for external access
- SSL termination
- Load balancing (if scaled)

## Scalability Considerations

### Horizontal Scaling
- Stateless service design
- Database connection pooling
- Load balancer integration
- Container orchestration ready

### Vertical Scaling
- GPU utilization for AI processing
- Memory optimization
- CPU core allocation
- Storage performance tuning

## Development Workflow

### Code Organization
- Microservices architecture
- Clear separation of concerns
- Consistent naming conventions
- Comprehensive documentation

### Quality Assurance
- Type hints throughout Python code
- Input validation with Pydantic
- Error handling and recovery
- Performance optimization

### Deployment Pipeline
- Single command deployment
- Environment configuration
- Health check verification
- Rollback capabilities

## Future Enhancements

### Planned Features
- Multi-language support expansion
- Advanced analytics and reporting
- Integration with additional channels
- Enhanced workflow capabilities

### Scalability Improvements
- Kubernetes deployment option
- Multi-region support
- Advanced load balancing
- Microservice mesh integration

---

*"The Scribe's architecture flows like ink upon parchment, each component crafted with artisanal precision to create a harmonious symphony of AI-powered communication."*