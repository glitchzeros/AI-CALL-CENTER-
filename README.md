# 🏛️ Aetherium - Advanced AI Communication Platform

**"Where AI Scribes dwell and conversations flow like ink upon parchment"**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://reactjs.org/)

Aetherium is a comprehensive AI-powered communication platform that enables businesses to deploy autonomous AI agents (called "Scribes") capable of conducting natural, context-aware conversations across multiple channels while executing complex automated workflows. Now featuring an advanced admin dashboard for complete system management.

## 🚀 Quick Start

### One-Command Setup
```bash
./start-aetherium.sh
```

That's it! The script will handle everything automatically:
- ✅ Check dependencies
- ✅ Build all Docker images  
- ✅ Start services in correct order
- ✅ Wait for services to be ready
- ✅ Display service status and URLs

### Access Points
| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:12000 | Main web interface |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |

## 🌟 Features

### 🎯 Core Capabilities
- **40 Concurrent Sessions**: Handle up to 40 simultaneous voice calls, SMS, and Telegram interactions
- **Multimodal AI**: Powered by Google's Gemini 2.0 Flash for advanced audio and text processing
- **Visual Workflow Builder**: Intuitive drag-and-drop "Invocation Editor" for creating AI behaviors
- **Multi-Channel Communication**: Voice calls, SMS messaging, and Telegram integration
- **Real-time Analytics**: Comprehensive statistics and conversation monitoring
- **Coffee Paper Aesthetic**: Unique, immersive UI design inspired by a scribe's workspace

### 🛠️ Admin Dashboard (NEW!)
- **API Key Management**: Dynamic allocation and rotation of Gemini API keys
- **GSM Modem Control**: Automatic detection and assignment of GSM modems
- **Company Configuration**: Custom system prompts and AI personalities per company
- **Subscription Management**: Client API key assignments with automatic renewal
- **Real-time Monitoring**: System health, usage statistics, and performance metrics
- **Auto-Configuration**: Smart environment setup with demo/production mode switching

### Technical Architecture
- **GSM Modem Integration**: Direct hardware control of SIM800C modems with dual USB connections
- **Edge TTS Integration**: Microsoft Edge Text-to-Speech with dynamic voice modulation
- **Click Payment Gateway**: Integrated subscription and payment processing
- **PostgreSQL Database**: Robust data storage with advanced triggers and functions
- **Docker Orchestration**: Single-command deployment with `docker compose up -d`

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   Backend API   │    │ Modem Manager   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Telegram Bot   │    │   PostgreSQL    │    │  GSM Hardware   │
│   (Python)      │    │   Database      │    │  (40 Modems)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **Hardware Requirements**:
   - Server with 64GB RAM (recommended for full deployment)
   - NVIDIA Tesla V100 GPU (16GB or 32GB VRAM) - optional for enhanced AI processing
   - 15 PCI 1x slots for USB expansion (for full GSM modem setup)
   - Up to 40 SIM800C GSM modems with dual USB connections (optional)

2. **Software Requirements**:
   - Docker and Docker Compose
   - Linux operating system (Ubuntu Server LTS recommended)
   - Git

### 🎯 Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/Asilbekov/Ozodbek-.git
cd Ozodbek-

# Run the automated setup script
./scripts/docker_setup.sh

# For development mode
./scripts/docker_setup.sh dev
```

### 🔧 Manual Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Asilbekov/Ozodbek-.git
   cd Ozodbek-
   ```

2. **Setup Environment**:
   ```bash
   python3 scripts/setup_environment.py
   ```

3. **Deploy the Platform**:
   ```bash
   docker compose up -d
   ```

### 🌐 Access Points

After successful setup:
- **🎛️ Admin Dashboard**: http://localhost:12000
- **🔧 Backend API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Required Environment Variables

Create a `.env` file with the following variables:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://aetherium_user:your_password@database:5432/aetherium

# Security
JWT_SECRET_KEY=your_32_character_jwt_secret_key_here
ENCRYPTION_KEY=your_32_character_encryption_key_here

# External APIs
GEMINI_API_KEY=your_gemini_api_key_here
CLICK_MERCHANT_ID=your_click_merchant_id
CLICK_SECRET_KEY=your_click_secret_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
SMS_API_KEY=your_sms_api_key
```

### Hardware Setup

1. **Install GSM Modems**:
   - Connect each SIM800C modem with two USB cables
   - One cable for AT command control (`/dev/ttyUSB*`)
   - One cable for audio interface (`/dev/snd/*`)

2. **USB Device Mapping**:
   - The system automatically detects and maps modem pairs
   - Supports up to 40 concurrent modems
   - Requires PCI USB expansion cards for sufficient ports

## 📱 User Guide

### Getting Started

1. **Registration**:
   - Visit the web portal at `http://your-server:12000`
   - Create an account with email and phone verification
   - Receive your unique "Company Number" on first login

2. **Subscription**:
   - Choose from three tiers: Apprentice ($20), Journeyman ($50), Master Scribe ($100)
   - Different context memory limits: 4K, 32K, or unlimited tokens
   - Payment processed via Click API integration

3. **Workflow Creation**:
   - Use the visual "Invocation Editor" to build AI behaviors
   - Drag and drop workflow nodes onto the canvas
   - Configure triggers, actions, and responses
   - Save and activate your Scribe's script

### Core Invocations

- **The Payment Ritual**: Complex payment flow with SMS confirmation
- **The Messenger**: Send SMS messages
- **The Telegram Channeler**: Telegram bot integration
- **The Final Word**: Hang up calls
- **The Scribe's Reply**: AI conversation responses

## 🎨 Coffee Paper Aesthetic

Aetherium features a unique "coffee paper" visual theme:

- **Color Palette**: Beige, khaki, tan, coffee brown, and sienna tones
- **Typography**: Cinzel Decorative for headings, Vollkorn for body text
- **Textures**: Paper grain backgrounds, ink-like borders, coffee stain effects
- **Sounds**: Paper sliding, pen scratching, book closing audio feedback
- **Aging Effects**: UI elements develop visual "wear" with usage

## 🔊 Audio Features

### Voice Processing Pipeline
1. **Voice Activity Detection (VAD)**: Silero VAD for speech segmentation
2. **Noise Reduction**: RNNoise and SpeexDSP for audio cleaning
3. **Speech-to-Text**: Vosk or similar for transcription
4. **Text-to-Speech**: Microsoft Edge TTS with dynamic voice modulation

### Dynamic Voice Adjustment
- **Pitch Control**: Adjust tone based on AI sentiment analysis
- **Rate Control**: Modify speaking speed for emphasis
- **Language Detection**: Automatic voice selection based on detected language
- **Mood Mapping**: AI-driven emotional expression in voice output

## 📊 Analytics & Monitoring

### Real-time Dashboard
- Total calls handled and duration
- Positive/negative interaction percentages
- Active session monitoring
- Call history with AI-generated summaries

### Advanced Analytics
- Hourly distribution patterns
- Outcome analysis by session type
- Trend comparisons over time
- Performance metrics and success rates

## 🤖 AI Integration

### Gemini 2.0 Flash Features
- **Multimodal Processing**: Simultaneous audio and text analysis
- **Context Management**: Subscription-tier based memory limits
- **Language Detection**: Automatic language identification
- **Structured Responses**: Command parsing and workflow triggers

### The Scribe's Dream Journal
- Autonomous meta-analysis of conversation data
- Nightly processing of anonymized logs
- Pattern recognition and insight generation
- Internal intelligence gathering for platform improvement

## 🔒 Security Features

- **JWT Authentication**: Secure user session management
- **Data Encryption**: Bank card numbers and sensitive data encrypted at rest
- **Input Validation**: Comprehensive sanitization of all user inputs
- **API Security**: Rate limiting and CORS protection
- **Audit Logging**: Comprehensive activity tracking

## 🛠️ Development

### Project Structure
```
Ai-call-center-agent-/
├── backend/                 # FastAPI backend service
├── frontend/               # React web application
├── modem-manager/          # GSM modem control service
├── telegram-bot/           # Telegram bot interface
├── database/              # PostgreSQL schema and migrations
├── docker compose.yml     # Orchestration configuration
└── .env.example          # Environment template
```

### Key Technologies
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: React, Tailwind CSS, React Query
- **Hardware**: PySerial, PyAudio, ALSA
- **AI**: Google Gemini API, Edge TTS
- **Communication**: Telegram Bot API, SMS APIs
- **Deployment**: Docker, Docker Compose

## 📋 API Documentation

Once deployed, API documentation is available at:
- **Backend API**: `http://your-server:8000/docs`
- **Modem Manager**: `http://your-server:8001/docs`

## 🔧 Troubleshooting

### Common Issues

1. **Modem Detection Problems**:
   ```bash
   # Check USB devices
   lsusb
   # Check serial ports
   ls -la /dev/ttyUSB*
   # Check audio devices
   ls -la /dev/snd/
   ```

2. **Database Connection Issues**:
   ```bash
   # Check database logs
   docker logs aetherium_database
   # Test connection
   docker exec -it aetherium_database psql -U aetherium_user -d aetherium
   ```

3. **Audio Processing Problems**:
   ```bash
   # Check ALSA devices
   aplay -l
   # Test audio capture
   arecord -l
   ```

### Log Locations
- Backend: `./backend/logs/`
- Modem Manager: `./modem-manager/logs/`
- Telegram Bot: `./telegram-bot/logs/`

## 🤝 Support

For technical support and questions:
1. Check the troubleshooting section above
2. Review Docker container logs
3. Verify environment configuration
4. Ensure hardware connections are secure

## 📄 License

This project is proprietary software. All rights reserved.

## 🎯 The Artisan's Mandate

Aetherium was built with meticulous craftsmanship, following the principle that exceptional software emerges from deep understanding and careful construction rather than iterative testing. Every component was designed to work harmoniously from the first deployment, embodying the philosophy that true artisanship transcends the need for conventional validation methodologies.

**"The Scribe awaits your command. May your conversations flow like ink upon parchment."**