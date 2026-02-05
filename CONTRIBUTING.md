# Contributing to Dynamic Content Blocks System

Thank you for considering contributing to the Dynamic Content Blocks System! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Project Structure](#project-structure)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Commit Messages](#commit-messages)
8. [Pull Request Process](#pull-request-process)
9. [Documentation](#documentation)
10. [Community](#community)

---

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes**:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes**:
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

---

## Getting Started

### Ways to Contribute

- 🐛 **Bug Reports**: Found a bug? Report it!
- ✨ **Feature Requests**: Have an idea? Suggest it!
- 📝 **Documentation**: Improve or translate docs
- 🔧 **Code**: Fix bugs or implement features
- 🧪 **Testing**: Add or improve tests
- 🎨 **Design**: Improve UI/UX

### Before You Start

1. **Check existing issues**: Someone might be working on it already
2. **Open an issue**: Discuss your idea before investing time
3. **Ask questions**: Use GitHub Discussions for questions
4. **Follow guidelines**: Review this document

---

## Development Setup

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Git
- Your favorite IDE (VS Code, PyCharm, etc.)

### Initial Setup

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/data10.git
cd data10

# 3. Add upstream remote
git remote add upstream https://github.com/original/data10.git

# 4. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 6. Start infrastructure
docker-compose up -d

# 7. Wait for services to be ready
sleep 30

# 8. Run tests to verify setup
pytest

# 9. Download NLP models (if working on ML features)
python scripts/setup_nlp_models.py
```

### Development Workflow

```bash
# 1. Create a feature branch
git checkout -b feature/my-awesome-feature

# 2. Make your changes
# Edit files...

# 3. Run tests
pytest

# 4. Run linters
black app/
flake8 app/
mypy app/

# 5. Commit changes
git add .
git commit -m "Add awesome feature"

# 6. Push to your fork
git push origin feature/my-awesome-feature

# 7. Open a Pull Request on GitHub
```

---

## Project Structure

```
data10/
├── app/                          # Main application
│   ├── api/                      # API endpoints
│   │   ├── auth.py              # Authentication
│   │   ├── audit.py             # Audit logging
│   │   ├── blocks.py            # Block management
│   │   ├── documents.py         # Document assembly
│   │   ├── search.py            # Search endpoints
│   │   ├── ml.py                # ML/NLP endpoints
│   │   ├── versions.py          # Version control
│   │   └── bulk.py              # Bulk operations
│   ├── core/                     # Core utilities
│   │   ├── security.py          # Security utilities
│   │   └── config.py            # Configuration
│   ├── middleware/               # Middleware
│   │   ├── audit_middleware.py  # Audit logging
│   │   ├── metrics_middleware.py # Metrics collection
│   │   └── rate_limiter.py      # Rate limiting
│   ├── models/                   # Data models
│   │   ├── block.py             # Block models
│   │   ├── document.py          # Document models
│   │   ├── auth.py              # Auth models
│   │   └── audit.py             # Audit models
│   ├── repositories/             # Database access
│   │   ├── neo4j_repo.py        # Neo4j repository
│   │   ├── mongo_repo.py        # MongoDB repository
│   │   ├── elasticsearch_repo.py # Elasticsearch
│   │   └── redis_repo.py        # Redis repository
│   ├── services/                 # Business logic
│   │   ├── block_service.py     # Block management
│   │   ├── assembly_service.py  # Document assembly
│   │   ├── search_service.py    # Search service
│   │   ├── nlp_service.py       # NLP/ML service
│   │   ├── auth_service.py      # Authentication
│   │   ├── audit_service.py     # Audit logging
│   │   └── metrics_service.py   # Metrics
│   └── main.py                   # Application entry point
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── scripts/                      # Utility scripts
├── docs/                         # Documentation
├── k8s/                          # Kubernetes manifests
├── monitoring/                   # Monitoring configuration
└── examples/                     # Example code
```

### Key Components

**API Layer** (`app/api/`):
- REST endpoints
- Request validation
- Response formatting

**Service Layer** (`app/services/`):
- Business logic
- Data processing
- Orchestration

**Repository Layer** (`app/repositories/`):
- Database operations
- Data access abstraction

**Models** (`app/models/`):
- Pydantic models
- Data validation
- Schema definitions

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

**Line Length**:
- Maximum line length: 100 characters
- Prefer readability over strict adherence

**Imports**:
```python
# Standard library
import os
from datetime import datetime

# Third-party
from fastapi import FastAPI, Depends
from pydantic import BaseModel

# Local
from app.models import Block
from app.services import block_service
```

**Type Hints**:
```python
# Always use type hints
def create_block(title: str, content: str) -> Block:
    """Create a new block."""
    return Block(title=title, content=content)

# Use Optional for nullable values
from typing import Optional

def get_block(id: str) -> Optional[Block]:
    """Get block by ID."""
    return block_service.get(id)
```

**Docstrings**:
```python
def complex_function(param1: str, param2: int) -> dict:
    """
    Brief description of function.

    Detailed description if needed. Explain what the function does,
    when to use it, and any important details.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative

    Example:
        >>> result = complex_function("test", 42)
        >>> print(result)
        {'status': 'success'}
    """
    if param2 < 0:
        raise ValueError("param2 must be non-negative")

    return {"status": "success", "param1": param1}
```

**Naming Conventions**:
```python
# Variables and functions: snake_case
user_name = "John"
def get_user_name():
    pass

# Classes: PascalCase
class BlockService:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30

# Private: prefix with underscore
def _internal_function():
    pass
```

### Code Quality Tools

**Black** (Code Formatting):
```bash
# Format code
black app/

# Check formatting
black --check app/
```

**Flake8** (Linting):
```bash
# Run linter
flake8 app/

# Configuration in .flake8
[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv
ignore = E203,W503
```

**MyPy** (Type Checking):
```bash
# Type check
mypy app/

# Configuration in mypy.ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

**Pre-commit Hooks**:
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Testing Guidelines

### Test Structure

```python
# tests/unit/test_block_service.py
import pytest
from app.services.block_service import BlockService

class TestBlockService:
    """Test BlockService class."""

    def test_create_block_success(self):
        """Test successful block creation."""
        service = BlockService()
        block = service.create_block(
            title="Test",
            content="Content"
        )
        assert block.title == "Test"

    def test_create_block_empty_title(self):
        """Test block creation with empty title."""
        service = BlockService()
        with pytest.raises(ValueError):
            service.create_block(title="", content="Content")
```

### Testing Best Practices

**1. Test Naming**:
- Use descriptive names: `test_<what>_<condition>_<expected>`
- Examples: `test_login_invalid_password_raises_error`

**2. Arrange-Act-Assert**:
```python
def test_calculate_total():
    # Arrange
    items = [10, 20, 30]

    # Act
    total = calculate_total(items)

    # Assert
    assert total == 60
```

**3. Fixtures**:
```python
@pytest.fixture
def sample_block():
    """Create a sample block for testing."""
    return Block(
        id="block_123",
        title="Sample",
        content="Content"
    )

def test_update_block(sample_block):
    """Test updating a block."""
    sample_block.title = "Updated"
    assert sample_block.title == "Updated"
```

**4. Mocking**:
```python
from unittest.mock import Mock, patch

def test_api_call_with_mock():
    """Test API call with mocked response."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'status': 'ok'}

        result = fetch_data()

        assert result == {'status': 'ok'}
        mock_get.assert_called_once()
```

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/unit/test_block_service.py

# Specific test
pytest tests/unit/test_block_service.py::TestBlockService::test_create_block

# With coverage
pytest --cov=app --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run only failed tests
pytest --lf
```

### Test Coverage Requirements

- Minimum coverage: 80%
- New features: 90%+ coverage
- Critical paths: 95%+ coverage

---

## Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

**Simple commit**:
```
feat(auth): add JWT token refresh endpoint
```

**Detailed commit**:
```
fix(search): correct Elasticsearch query timeout

The search query was timing out for large datasets.
Increased timeout from 10s to 30s and added retry logic.

Fixes #123
```

**Breaking change**:
```
feat(api): change authentication to OAuth2

BREAKING CHANGE: JWT tokens are now required for all endpoints.
Old API key authentication is no longer supported.

Migration guide: docs/migration-to-oauth2.md
```

---

## Pull Request Process

### Before Creating PR

1. ✅ All tests pass
2. ✅ Code is formatted (black)
3. ✅ No linting errors (flake8)
4. ✅ Type checking passes (mypy)
5. ✅ Documentation updated
6. ✅ CHANGELOG updated

### PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests pass locally

## Related Issues
Fixes #123
Related to #456
```

### Review Process

1. **Automated checks**: Must pass CI/CD
2. **Code review**: At least 1 approval required
3. **Testing**: All tests must pass
4. **Documentation**: Updated if needed
5. **Merge**: Squash and merge to main

### After Merge

- Delete feature branch
- Update local main branch
- Close related issues

---

## Documentation

### Types of Documentation

**Code Documentation**:
- Docstrings for all public functions/classes
- Inline comments for complex logic
- Type hints for all parameters

**API Documentation**:
- OpenAPI/Swagger auto-generated
- Example requests/responses
- Error codes explained

**User Documentation**:
- README.md: Quick start guide
- docs/: Detailed guides
- DEPLOYMENT_GUIDE.md: Production setup

**Developer Documentation**:
- CONTRIBUTING.md: This file
- Architecture documentation
- Design decisions

### Writing Good Documentation

**Be Clear and Concise**:
```markdown
# Bad
This function does stuff with blocks.

# Good
Creates a new content block with the given title and content.
Returns the created block with a generated ID.
```

**Include Examples**:
```markdown
## Example

```python
# Create a block
block = create_block(
    title="§ 5 SGB IX",
    content="Menschen mit Behinderungen..."
)

# Use the block
document = assemble_document([block])
```
```

**Keep Documentation Updated**:
- Update docs when changing code
- Review docs during code review
- Remove outdated information

---

## Community

### Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and ideas
- **Stack Overflow**: Tag with `dynamic-content-blocks`

### Communication Channels

- **GitHub**: Primary communication
- **Email**: For security issues only
- **Chat**: Discord/Slack (if available)

### Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the Dynamic Content Blocks System! 🎉

**Happy Coding!**
