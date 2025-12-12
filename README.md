# GitHub Test Authoring Tool - POC

An intelligent test authoring system that automatically generates tests from GitHub issues using AI and codebase context.

## 🎯 Overview

This POC automatically generates test cases when you create GitHub issues with acceptance criteria. The tool:
- Analyzes your repository structure
- Detects your test framework (pytest, jest, playwright, etc.)
- Searches for relevant code
- Generates tests using OpenAI with codebase context
- Creates a PR with the generated tests
- Posts results as a comment on the issue

## 🏗️ Architecture

```
┌──────────────┐      ┌──────────────────┐      ┌─────────────┐
│ GitHub Issue │─────>│   FastAPI App    │─────>│   OpenAI    │
│   (Manual)   │      │  (Backend API)   │      │  GPT-4 API  │
└──────────────┘      └──────────────────┘      └─────────────┘
                              │
                              │ Analyzes Repo
                              ▼
                     ┌──────────────────┐
                     │  GitHub Code     │
                     │  Search API      │
                     └──────────────────┘
                              │
                              │ Generates Tests
                              ▼
                     ┌──────────────────┐
                     │   New Branch +   │
                     │   Test Files +   │
                     │   Pull Request   │
                     └──────────────────┘
```

## ✨ Features

- **GitHub Integration**: Fetches issues with acceptance criteria
- **Smart Code Search**: Finds relevant code using GitHub Code Search API
- **Framework Detection**: Auto-detects pytest, jest, playwright, mocha, vitest, unittest
- **AI-Powered**: Uses OpenAI with codebase context for accurate test generation
- **Test Case Optimization** 🆕: Comprehensive quality analysis including:
  - Similarity detection (flags tests >70% similar)
  - AI-powered optimization suggestions
  - Redundancy and outdated code detection
  - Quality score with actionable recommendations
- **Test Coverage Analysis** 🆕: Automatic coverage measurement including:
  - Before/after coverage comparison
  - Per-module coverage breakdown
  - Coverage gap identification
  - Actionable recommendations for uncovered code
- **Auto Publishing**: Creates branch, commits tests, opens PR automatically
- **Issue Comments**: Posts results and PR link directly on the issue
- **Multi-Language**: Supports Python (pytest/unittest) and JavaScript/TypeScript (jest/playwright/mocha/vitest)

## 📋 Prerequisites

- **Python 3.11+**
- **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)
- **GitHub Personal Access Token** - [Create one here](https://github.com/settings/tokens)
  - Required permissions: `repo` (full), `workflow`
- **Target GitHub Repository** - The repo you want to generate tests for

## 🚀 Quick Start

### 1. Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd cnbc_testauhtoringtool

# Install Python dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Configure Environment

```bash
# Copy example environment file
cp env.example .env

# Edit .env with your credentials
nano .env
```

Add your configuration:
```bash
# OpenAI Configuration (Required)
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini

# GitHub Configuration (Required)
GITHUB_TOKEN=ghp_your_actual_token_here
GITHUB_REPO=owner/repository-name
```

### 3. Start the Service

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting GitHub Test Authoring Tool API
INFO:     Application startup complete.
```

### 4. Create a GitHub Issue

Create an issue in your target repository with this format:

**Title**: Add user authentication

**Body**:
```markdown
We need to implement user authentication for the application.

## Acceptance Criteria

- AC1: User can register with email and password
- AC2: User can login with valid credentials
- AC3: User receives error message with invalid credentials
- AC4: User session persists after page reload
- AC5: User can logout successfully
```

### 5. Generate Tests

Trigger test generation using curl or any HTTP client:

```bash
curl -X POST http://localhost:8000/github/generate-tests \
  -H "Content-Type: application/json" \
  -d '{"issue_number": 123}'
```

Replace `123` with your actual issue number.

### 6. Check Results

The tool will:
1. ✅ Fetch the issue from GitHub
2. ✅ Detect your test framework
3. ✅ Search for relevant code
4. ✅ Generate tests with AI
5. ✅ Create branch `auto-tests/issue-123`
6. ✅ Commit test file
7. ✅ Create pull request
8. ✅ Comment on the issue with PR link

Check your repository for:
- New branch: `auto-tests/issue-123`
- Pull request with generated tests
- Comment on the original issue

## 📁 Project Structure

```
cnbc_testauhtoringtool/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI app entry point
│   │   ├── github_webhook.py            # GitHub webhook handler & orchestration
│   │   ├── github/
│   │   │   ├── client.py                # GitHub API client
│   │   │   └── code_search.py           # Code context builder
│   │   ├── llm/
│   │   │   ├── author.py                # Legacy Playwright generator
│   │   │   └── test_author.py           # New framework-agnostic generator
│   │   ├── detectors/
│   │   │   └── test_framework.py        # Test framework detector
│   │   ├── publisher/
│   │   │   └── git_operations.py        # Git operations (branch, PR, etc.)
│   │   └── models/
│   │       ├── github_issue.py          # GitHub issue models
│   │       └── jira_issue.py            # Legacy JIRA models
│   ├── requirements.txt
│   └── Dockerfile
├── .env.example                          # Environment variables template
├── README.md                             # This file
└── playwright.config.ts                  # Playwright configuration
```

## 🔌 API Endpoints

### Generate Tests

```bash
POST /github/generate-tests
Content-Type: application/json

{
  "issue_number": 123,
  "repo_override": "owner/repo"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Tests generated and published successfully",
  "issue_number": 123,
  "branch_name": "auto-tests/issue-123",
  "pull_request_url": "https://github.com/owner/repo/pull/456",
  "test_files": ["tests/test_user_authentication_issue_123.py"],
  "error": null
}
```

### Health Check

```bash
GET /github/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "github-test-generator"
}
```

### Main Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "ok"
}
```

## 🎨 Supported Test Frameworks

The tool automatically detects and generates tests for:

| Framework | Language | Detection | Example Pattern |
|-----------|----------|-----------|-----------------|
| **pytest** | Python | `pytest.ini`, `conftest.py` | `test_*.py` |
| **unittest** | Python | `import unittest` | `test_*.py` |
| **jest** | JavaScript/TypeScript | `jest.config.js`, `package.json` | `*.test.ts` |
| **playwright** | TypeScript | `playwright.config.ts` | `*.spec.ts` |
| **mocha** | JavaScript | `.mocharc.json`, `package.json` | `*.test.js` |
| **vitest** | TypeScript | `vitest.config.ts` | `*.test.ts` |

## 📝 Issue Format Best Practices

For best results, format your GitHub issues like this:

**Title**: Clear feature or bug description

**Body**:
```markdown
Brief description of what needs to be implemented or fixed.

## Acceptance Criteria

- AC1: First testable requirement
- AC2: Second testable requirement
- AC3: Third testable requirement
- AC4: Edge case or error handling
- AC5: Additional requirement

## Additional Context (Optional)

- Related files: `src/auth/login.py`
- Dependencies: User model, Session management
- Edge cases to consider: Invalid credentials, expired tokens
```

The tool extracts acceptance criteria and uses them to generate focused tests.

## 🧪 Example Generated Tests

### Python (pytest)

```python
import pytest
from app.auth import AuthService

def test_user_registration_with_valid_data():
    """AC1: User can register with email and password"""
    # AC: AC1
    auth = AuthService()
    result = auth.register("user@example.com", "SecurePass123!")
    assert result.success is True
    assert result.user_id is not None

def test_user_login_with_valid_credentials():
    """AC2: User can login with valid credentials"""
    # AC: AC2
    auth = AuthService()
    auth.register("user@example.com", "SecurePass123!")
    result = auth.login("user@example.com", "SecurePass123!")
    assert result.authenticated is True
```

### TypeScript (Playwright)

```typescript
import { test, expect } from '@playwright/test';

test.describe('User Authentication', () => {
  test('should allow user registration - AC1', async ({ page }) => {
    // AC: AC1
    await page.goto('/register');
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('SecurePass123!');
    await page.getByRole('button', { name: /register/i }).click();
    await expect(page).toHaveURL(/.*dashboard/);
  });
  
  test('should login with valid credentials - AC2', async ({ page }) => {
    // AC: AC2
    await page.goto('/login');
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('SecurePass123!');
    await page.getByRole('button', { name: /login/i }).click();
    await expect(page.getByText(/welcome/i)).toBeVisible();
  });
});
```

## 🐛 Troubleshooting

### Missing Environment Variables

**Error**: `Missing environment variables: GITHUB_TOKEN, GITHUB_REPO`

**Solution**: 
```bash
# Check your .env file exists
ls -la .env

# Verify variables are set
cat .env | grep GITHUB
```

### GitHub Authentication Failed

**Error**: `Failed to access repository owner/repo: 401 Unauthorized`

**Solution**:
- Verify your `GITHUB_TOKEN` is correct
- Check token has `repo` permissions
- Token might be expired - create a new one

### Framework Not Detected

**Warning**: `No test framework detected`

**Solution**: The tool defaults to `pytest` for Python or `jest` for JavaScript. To improve detection:
- Ensure you have framework config files (e.g., `pytest.ini`, `jest.config.js`)
- Check files are in the repository root or standard locations

### Code Search Returns No Results

**Issue**: Tool can't find relevant code

**Solutions**:
- Ensure repository has indexed code (new repos may take time)
- Use more specific keywords in issue title
- Add relevant file paths in issue description

### Test Generation Failed

**Error**: `Failed to generate tests: ...`

**Possible Causes**:
1. **OpenAI API Key invalid**: Check key in `.env`
2. **Rate limit hit**: Wait a few minutes and retry
3. **Insufficient credits**: Add credits to OpenAI account
4. **Context too large**: Issue body might be too long

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | Yes | OpenAI API key | - |
| `OPENAI_MODEL` | No | Model to use | `gpt-4o-mini` |
| `GITHUB_TOKEN` | Yes | GitHub personal access token | - |
| `GITHUB_REPO` | Yes | Target repository (owner/repo) | - |
| `LOG_LEVEL` | No | Logging level | `INFO` |

### Customizing Test Generation

To modify test generation behavior, edit:

**Framework Detection**: `backend/app/detectors/test_framework.py`
- Add new frameworks
- Modify detection patterns
- Change test directory conventions

**AI Prompts**: `backend/app/llm/test_author.py`
- Adjust system prompts
- Modify temperature (creativity)
- Change token limits

**Code Search**: `backend/app/github/code_search.py`
- Modify keyword extraction
- Adjust number of files searched
- Change context building logic

## 📚 Documentation

For detailed guides on specific features, see:
- **[Test Optimization Guide](docs/TEST_OPTIMIZATION_GUIDE.md)** - Similarity detection, AI suggestions, redundancy detection
- **[Coverage Integration Guide](docs/COVERAGE_GUIDE.md)** - Before/after coverage, gap analysis
- **[Quick Start Guide](docs/OPTIMIZATION_QUICKSTART.md)** - Fast setup for optimization features
- **[All Documentation](docs/)** - Complete documentation index

## 🚀 Future Enhancements

Potential extensions for this POC:

- [ ] **Webhook Integration**: Auto-trigger on issue creation
- [ ] **Docker Deployment**: Deploy to cloud with Docker
- [ ] **Web UI**: Configure repositories and view history
- [ ] **Multi-Repo Support**: Manage multiple repositories
- [ ] **Feedback Loop**: Update tests based on CI results
- [ ] **Custom Templates**: Per-project test templates
- [ ] **Batch Processing**: Generate tests for multiple issues
- [ ] **Test Execution Integration**: Run tests and report results back

## 📚 Development

### Running Locally

```bash
# Start with hot reload
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing the API

```bash
# Health check
curl http://localhost:8000/health

# Generate tests
curl -X POST http://localhost:8000/github/generate-tests \
  -H "Content-Type: application/json" \
  -d '{"issue_number": 1}'
```

### Viewing Logs

```bash
# Logs show each step
INFO: Fetching issue from GitHub
INFO: Detected framework: pytest
INFO: Found 3 relevant code files
INFO: Generating tests with AI
INFO: Creating branch: auto-tests/issue-1
INFO: Created PR #45: 🤖 Automated Tests for #1
```

## 🤝 Contributing

Contributions welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **OpenAI** - GPT models for intelligent test generation
- **GitHub** - API for code search and repository management
- **FastAPI** - Modern Python web framework
- **Playwright** - End-to-end testing framework
- **pytest** - Python testing framework

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check troubleshooting section above
- Review API documentation

---

**Happy Testing! 🎭 Let AI handle the boilerplate, you focus on quality!**
