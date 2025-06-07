# Contributing to Aetherium

Welcome to the Aetherium project! We're excited that you're interested in contributing to our AI call center platform. This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for everyone.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Git** (2.30+)
- **Node.js** (18+) and **npm** (8+) for frontend development
- **Python** (3.11+) for backend development
- **PostgreSQL** (15+) for database development

### Initial Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/Aetherium.git
   cd Aetherium
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/Aetherium.git
   ```
4. **Run the setup script**:
   ```bash
   ./scripts/setup.sh
   ```

## Development Setup

### Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your development settings:
   ```bash
   # Development settings
   ENVIRONMENT=development
   LOG_LEVEL=DEBUG
   
   # API Keys (get from respective services)
   GEMINI_API_KEY=your_gemini_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   ```

### Development Mode

Start the application in development mode:

```bash
./scripts/start.sh --dev
```

This will:
- Enable hot reloading for frontend and backend
- Start development tools (PgAdmin, Redis Commander, MailHog)
- Use development-specific configurations
- Enable debug logging

### Development URLs

When running in development mode, you can access:

- **Frontend**: http://localhost:12000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PgAdmin**: http://localhost:5050 (admin@aetherium.dev / admin123)
- **Redis Commander**: http://localhost:8081
- **MailHog**: http://localhost:8025

## Contributing Guidelines

### Branch Naming

Use descriptive branch names with prefixes:

- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Critical fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

Examples:
- `feature/workflow-builder-ui`
- `bugfix/session-timeout-issue`
- `docs/api-documentation-update`

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(auth): add two-factor authentication

fix(sessions): resolve memory leak in session cleanup

docs(api): update authentication endpoints documentation

test(payments): add unit tests for payment processing
```

### Code Organization

#### Backend Structure
```
backend/
├── main.py                 # FastAPI application entry point
├── models/                 # Database models
├── routers/               # API route handlers
├── services/              # Business logic services
├── utils/                 # Utility functions and helpers
├── database/              # Database configuration and migrations
└── tests/                 # Test files
```

#### Frontend Structure
```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   ├── pages/            # Page components
│   ├── hooks/            # Custom React hooks
│   ├── services/         # API services
│   ├── utils/            # Utility functions
│   ├── styles/           # CSS and styling
│   └── types/            # TypeScript type definitions
└── public/               # Static assets
```

## Code Style

### Backend (Python)

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 88 characters (Black formatter default)
- **Import organization**: Use `isort` for import sorting
- **Type hints**: Required for all public functions
- **Docstrings**: Use Google-style docstrings

Example:
```python
from typing import List, Optional
from fastapi import HTTPException

async def get_user_sessions(
    user_id: str,
    limit: int = 20,
    offset: int = 0
) -> List[Session]:
    """
    Retrieve user sessions with pagination.
    
    Args:
        user_id: The unique identifier for the user
        limit: Maximum number of sessions to return
        offset: Number of sessions to skip
        
    Returns:
        List of user sessions
        
    Raises:
        HTTPException: If user is not found
    """
    # Implementation here
    pass
```

### Frontend (TypeScript/JavaScript)

We use Prettier and ESLint for code formatting:

- **Prettier**: Automatic code formatting
- **ESLint**: Code linting and error detection
- **TypeScript**: Strict type checking enabled

Example:
```typescript
interface UserSession {
  id: string;
  userId: string;
  sessionType: 'voice' | 'sms' | 'telegram';
  status: 'active' | 'completed' | 'failed';
  startTime: string;
  endTime?: string;
}

const getUserSessions = async (
  userId: string,
  options: {
    limit?: number;
    offset?: number;
  } = {}
): Promise<UserSession[]> => {
  const { limit = 20, offset = 0 } = options;
  
  const response = await api.get(`/users/${userId}/sessions`, {
    params: { limit, offset }
  });
  
  return response.data;
};
```

### CSS/Styling

We use Tailwind CSS with custom coffee paper theme:

- **Utility-first**: Use Tailwind utility classes
- **Custom components**: Create reusable component classes
- **Responsive design**: Mobile-first approach
- **Coffee paper theme**: Use predefined color palette

Example:
```jsx
const SessionCard = ({ session }) => (
  <div className="bg-gradient-to-br from-amber-50 to-orange-100 rounded-lg border-2 border-amber-200 p-6 shadow-lg">
    <h3 className="text-xl font-['Cinzel_Decorative'] text-amber-800 mb-2">
      {session.title}
    </h3>
    <p className="text-amber-700 font-['Vollkorn'] leading-relaxed">
      {session.description}
    </p>
  </div>
);
```

## Testing

### Backend Testing

We use pytest for backend testing:

```bash
# Run all tests
cd backend
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_auth.py

# Run with verbose output
python -m pytest -v
```

Test categories:
- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete user workflows

### Frontend Testing

We use Jest and React Testing Library:

```bash
# Run all tests
cd frontend
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- LoginPage.test.jsx

# Run in watch mode
npm test -- --watch
```

### Test Guidelines

1. **Write tests first** (TDD approach when possible)
2. **Test behavior, not implementation**
3. **Use descriptive test names**
4. **Mock external dependencies**
5. **Aim for high test coverage** (>80%)

Example test:
```python
def test_user_registration_with_valid_data(client, sample_user_data):
    """Test successful user registration with valid data."""
    response = client.post("/api/auth/register", json=sample_user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["user"]["email"] == sample_user_data["email"]
    assert "password" not in data["user"]
```

## Pull Request Process

### Before Submitting

1. **Update your branch** with the latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests** and ensure they pass:
   ```bash
   # Backend tests
   cd backend && python -m pytest
   
   # Frontend tests
   cd frontend && npm test
   ```

3. **Run linting** and fix any issues:
   ```bash
   # Backend
   cd backend && python -m flake8 . && python -m black . && python -m isort .
   
   # Frontend
   cd frontend && npm run lint && npm run format
   ```

4. **Update documentation** if needed

### Pull Request Template

When creating a pull request, use this template:

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by at least one maintainer
3. **Testing** in development environment
4. **Documentation** review if applicable
5. **Approval** and merge by maintainer

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Ubuntu 20.04]
 - Browser [e.g. chrome, safari]
 - Version [e.g. 22]

**Additional context**
Add any other context about the problem here.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

## Documentation

### Types of Documentation

1. **Code documentation**: Inline comments and docstrings
2. **API documentation**: OpenAPI/Swagger specifications
3. **User documentation**: User guides and tutorials
4. **Developer documentation**: Setup and contribution guides

### Documentation Standards

- **Clear and concise**: Write for your audience
- **Up-to-date**: Keep documentation current with code changes
- **Examples**: Include practical examples
- **Searchable**: Use clear headings and structure

### Updating Documentation

When making changes that affect:
- **API endpoints**: Update OpenAPI specifications
- **User interface**: Update user guides
- **Setup process**: Update installation instructions
- **Configuration**: Update environment variable documentation

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Discord**: Real-time chat (link in README)
- **Email**: security@aetherium.ai for security issues

### Getting Help

1. **Check existing documentation** first
2. **Search existing issues** for similar problems
3. **Ask in GitHub Discussions** for general questions
4. **Create an issue** for bugs or feature requests

### Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **GitHub contributors** page

## Security

### Reporting Security Issues

**Do not** report security vulnerabilities through public GitHub issues.

Instead, email us at: security@aetherium.ai

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Guidelines

- **Never commit secrets** (API keys, passwords, etc.)
- **Use environment variables** for configuration
- **Follow security best practices** in code
- **Keep dependencies updated**

## License

By contributing to Aetherium, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Aetherium! Your efforts help make this project better for everyone. 🌟

*"Where AI Scribes dwell and conversations flow like ink upon parchment"*