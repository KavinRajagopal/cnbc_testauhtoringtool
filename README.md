# GitHub Test Authoring Tool

An intelligent test automation platform that provides AI-powered test generation, coverage analysis, and test optimization for GitHub repositories.

**🚀 New: Interactive Onboarding** - Get started in 3-5 minutes with our guided setup process that validates your credentials and auto-detects your repository configuration!

## 🎯 Overview

This tool provides **three independent capabilities** to enhance your testing workflow:

### 1️⃣ **Test Case Generation**
Generate comprehensive test cases automatically from GitHub issues with acceptance criteria.
- Analyzes your repository structure
- Detects your test framework (pytest, jest, playwright, etc.)
- Searches for relevant code using GitHub Code Search API
- Generates tests using OpenAI with codebase context
- Creates a PR with the generated tests
- Posts results as comments on the issue

### 2️⃣ **Test Coverage Analysis**
Measure and analyze test coverage to identify gaps in your test suite.
- Runs coverage analysis on your test suite
- Compares before/after coverage when new tests are added
- Identifies specific uncovered code sections (lines, functions, branches)
- Generates comprehensive coverage reports
- Posts coverage reports to GitHub issues

### 3️⃣ **Test Optimization**
Analyze your test suite for quality and efficiency improvements.
- Detects similar test cases (>70% similarity threshold)
- Identifies redundant or outdated tests
- Provides AI-powered optimization suggestions
- Recommends parameterization and fixture improvements
- Generates quality scores with actionable recommendations

Each functionality can be **enabled/disabled independently** via configuration.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Test Authoring Tool                   │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Core Capabilities                      │ │
│  │                                                           │ │
│  │  1️⃣ Test Generation    2️⃣ Coverage Analysis    3️⃣ Optimization │ │
│  │     │                      │                      │       │ │
│  │     ├─ Issue Parser       ├─ Python Coverage    ├─ Similarity   │ │
│  │     ├─ Code Search        ├─ JS Coverage        ├─ Redundancy   │ │
│  │     ├─ AI Generation      ├─ Gap Analyzer       ├─ AI Suggestions│ │
│  │     └─ Test Writer        └─ Report Builder     └─ Quality Score │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────────┐    ┌─────────────────────────────┐ │
│  │  GitHub Data Reader    │    │   GitHub Publisher          │ │
│  │                        │    │                             │ │
│  │  • Fetch Issues        │    │  • Create Branches          │ │
│  │  • Search Code         │    │  • Commit Files             │ │
│  │  • Clone Repository    │    │  • Create Pull Requests     │ │
│  │  • Detect Framework    │    │  • Post Issue Comments      │ │
│  └────────────────────────┘    └─────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                  Supporting Tools                         │ │
│  │                                                           │ │
│  │  • OpenAI Integration    • Framework Detector            │ │
│  │  • AST Analyzer          • Coverage Tools Runner         │ │
│  │  • Embeddings Engine     • Markdown Report Builder       │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

                    ▲                          │
                    │                          ▼
            ┌───────────────┐          ┌──────────────┐
            │ GitHub Issues │          │ GitHub Repo  │
            │   + PRs       │          │  (Tests +    │
            └───────────────┘          │   Reports)   │
                                       └──────────────┘
```

## ✨ Three Core Features

### 🤖 Feature 1: Test Case Generation
**Endpoint**: `POST /github/generate-tests`

Automatically generates test cases from GitHub issue acceptance criteria:
- Fetches issue details and acceptance criteria
- Detects test framework (pytest, jest, playwright, mocha, vitest, unittest)
- Searches for relevant code using GitHub Code Search API
- Generates tests using OpenAI with codebase context
- Creates branch + commits tests + opens PR
- Posts results as issue comment

**Use Case**: You create a GitHub issue with acceptance criteria → Tool generates complete test suite

---

### 📊 Feature 2: Test Coverage Analysis
**Endpoint**: `POST /github/analyze-coverage`

Measures test coverage and identifies gaps:
- Runs coverage analysis (Python: pytest-cov, JavaScript: jest/nyc)
- Compares before/after coverage when tests are added
- Identifies uncovered lines, functions, and branches
- Generates per-module coverage breakdown
- Posts comprehensive coverage report to GitHub issue

**Use Case**: Understand what parts of your code are tested and what needs coverage

---

### 🎯 Feature 3: Test Case Optimization
**Endpoint**: `POST /github/optimize-tests`

Analyzes test suite quality and suggests improvements:
- **Similarity Detection**: Flags tests >70% similar using embeddings
- **Redundancy Detection**: Identifies duplicate or outdated tests via AST analysis
- **AI Suggestions**: Recommends parameterization, fixture improvements, better assertions
- **Quality Score**: Provides overall quality rating with actionable recommendations

**Use Case**: Clean up your test suite, reduce duplication, improve maintainability

---

## 🔧 Supporting Capabilities

All three features leverage:
- **GitHub Integration**: Read issues, search code, create PRs, post comments
- **Framework Detection**: Auto-detect test framework from repository
- **AI-Powered Analysis**: OpenAI GPT-4 for intelligent generation and suggestions
- **Multi-Language Support**: Python (pytest/unittest) and JavaScript/TypeScript (jest/playwright/mocha/vitest)

## 📋 Prerequisites

Before you start, ensure you have:

### Required
- **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- **pip** - Python package manager (comes with Python)
- **git** - For repository operations

### API Credentials (Collected during onboarding)
- **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)
  - Make sure you have credits added to your account
  - The onboarding script will test this with a real API call
  
- **GitHub Personal Access Token** - [Create one here](https://github.com/settings/tokens)
  - Required permissions: `repo` (full control), `workflow`
  - The onboarding script will verify these permissions

### Target Repository
- **GitHub Repository** - The repo you want to generate tests for
  - Must contain code in a supported language (Python or JavaScript/TypeScript)
  - Must use a supported test framework (pytest, jest, playwright, mocha, vitest, unittest)
  - You need read/write access (the onboarding script will verify this)

## 🚀 Quick Start

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/KavinRajagopal/cnbc_testauhtoringtool.git
cd cnbc_testauhtoringtool

# Install Python dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Run Interactive Onboarding ✨ NEW

```bash
# Run the onboarding script
python onboard.py
```

**The onboarding script will:**
- ✅ Validate your OpenAI API key with a real API call
- ✅ Validate your GitHub token and check permissions
- ✅ Verify repository access (reads your target repo)
- ✅ Clone and analyze your repository structure (shallow clone)
- ✅ Auto-detect your test framework (pytest, jest, playwright, etc.)
- ✅ Check repository compatibility (language, framework, size)
- ✅ Guide you through optional configuration (optimization, coverage)
- ✅ Generate `.env` file with all your settings
- ✅ Create `.tool_state.json` to track configuration and usage
- ✅ Allow re-running to update existing configuration

**Choose your setup method:**
- **Option 1: Guided Setup** (Recommended) - 3-5 minutes
  - Step-by-step with real-time validation and auto-detection
  - Retry logic for credential errors
  - Configuration summary with edit capability
- **Option 2: Manual Setup** - 1-2 minutes
  - For experienced users who prefer editing `.env` directly
  - Shows examples and references

**See [ONBOARDING_GUIDE.md](ONBOARDING_GUIDE.md) for detailed walkthrough with screenshots.**

### 3. Start the Service

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

You should see configuration loaded from your `.tool_state.json` and `.env`:
```
INFO:     Started server process
INFO:     Starting GitHub Test Authoring Tool API
INFO:     Configuration loaded successfully.
INFO:     Current GitHub Repo: owner/repository-name
INFO:     OpenAI Model: gpt-4o-mini
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Note**: If configuration is missing, the server will show an error. Run `python onboard.py` to configure.

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

### 5. Use the Features

#### Option A: Generate Tests from Issue

```bash
curl -X POST http://localhost:8000/github/generate-tests \
  -H "Content-Type: application/json" \
  -d '{"issue_number": 123}'
```

**What happens:**
1. Fetches issue #123 from GitHub
2. Detects test framework
3. Searches for relevant code
4. Generates tests with AI
5. Creates branch `auto-tests/issue-123`
6. Commits test file
7. Creates pull request
8. (Optional) Runs optimization analysis
9. (Optional) Runs coverage analysis
10. Posts results to issue

#### Option B: Analyze Coverage Only

```bash
curl -X POST http://localhost:8000/github/analyze-coverage \
  -H "Content-Type: application/json" \
  -d '{"test_path": "tests/", "include_gaps": true}'
```

**What happens:**
1. Clones repository locally
2. Runs coverage tools
3. Identifies uncovered code
4. Generates coverage report
5. Posts report to GitHub issue

#### Option C: Optimize Existing Tests

```bash
curl -X POST http://localhost:8000/github/optimize-tests \
  -H "Content-Type: application/json" \
  -d '{"test_path": "tests/", "similarity_threshold": 0.7}'
```

**What happens:**
1. Analyzes all test files
2. Detects similar tests using embeddings
3. Identifies redundant/outdated tests
4. Gets AI optimization suggestions
5. Generates quality report
6. Posts recommendations to GitHub

### 6. Check Results

Check your GitHub repository for:
- **Test Generation**: New branch, pull request, issue comment with test preview
- **Coverage Analysis**: Issue comment with coverage report and gaps
- **Test Optimization**: Issue comment with quality score and recommendations

## 🔄 How Features Work Together

The three features can be used **independently** or **together**:

### Independent Usage

```bash
# Just generate tests
curl -X POST http://localhost:8000/github/generate-tests -d '{"issue_number": 123}'

# Just analyze coverage  
curl -X POST http://localhost:8000/github/analyze-coverage

# Just optimize tests
curl -X POST http://localhost:8000/github/optimize-tests
```

### Combined Usage

When you **generate tests** with optimization and coverage **enabled**:

```bash
# In .env
ENABLE_OPTIMIZATION=true
ENABLE_COVERAGE_ANALYSIS=true

# Single API call
curl -X POST http://localhost:8000/github/generate-tests -d '{"issue_number": 123}'
```

**This will:**
1. Generate tests from issue
2. Analyze the generated tests for quality (optimization)
3. Run coverage to show impact (coverage)
4. Create PR with all three reports

### Typical Workflows

**Workflow 1: New Feature Development**
1. Create GitHub issue with acceptance criteria
2. Call `generate-tests` → Get tests + optimization + coverage
3. Review PR, merge if satisfied

**Workflow 2: Improve Existing Tests**
1. Call `optimize-tests` on existing test suite
2. Review quality report and suggestions
3. Refactor tests based on recommendations
4. Call `analyze-coverage` to verify improvement

**Workflow 3: Coverage Sprint**
1. Call `analyze-coverage` to see current state
2. Identify gaps in coverage report
3. Create issues for uncovered functionality
4. Call `generate-tests` for each issue
5. Re-run `analyze-coverage` to track progress

## 📁 Project Structure

```
cnbc_testauhtoringtool/
├── onboard.py                           # 🎯 Interactive onboarding script (START HERE!)
├── ONBOARDING_GUIDE.md                  # Detailed onboarding walkthrough
│
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI app entry point
│   │   ├── github_webhook.py            # API endpoints & orchestration
│   │   │
│   │   ├── config/                      # ⚙️ Configuration & State Management
│   │   │   ├── state_manager.py         # State tracking (.tool_state.json)
│   │   │   ├── models.py                # Configuration Pydantic models
│   │   │   ├── validator.py             # API credential validators
│   │   │   ├── loader.py                # Config loader (state + .env)
│   │   │   ├── cli_helpers.py           # Terminal UI utilities
│   │   │   └── compatibility.py         # Repository compatibility checker
│   │   │
│   │   ├── github/                      # 📥 GitHub Data Reader
│   │   │   ├── client.py                # GitHub API client (fetch issues, search, clone)
│   │   │   └── code_search.py           # Code context builder
│   │   │
│   │   ├── publisher/                   # 📤 GitHub Publisher
│   │   │   └── git_operations.py        # Git operations (branch, commit, PR, comments)
│   │   │
│   │   ├── coverage/                    # 📊 Feature 2: Coverage Analysis
│   │   │   ├── coverage_analyzer.py     # Main coverage orchestrator
│   │   │   ├── coverage_models.py       # Coverage data models
│   │   │   ├── python_coverage.py       # Python coverage runner (pytest-cov)
│   │   │   ├── javascript_coverage.py   # JavaScript coverage runner (jest/nyc)
│   │   │   ├── gap_analyzer.py          # Identifies uncovered code
│   │   │   └── report_builder.py        # Generates coverage reports
│   │   │
│   │   ├── optimizers/                  # 🎯 Feature 3: Test Optimization
│   │   │   ├── test_optimizer.py        # Main optimization orchestrator
│   │   │   ├── models.py                # Optimization data models
│   │   │   ├── similarity_analyzer.py   # Detects similar tests (embeddings)
│   │   │   ├── redundancy_detector.py   # Finds redundant/outdated tests (AST)
│   │   │   ├── ai_suggestions.py        # AI-powered recommendations
│   │   │   └── report_builder.py        # Generates optimization reports
│   │   │
│   │   ├── llm/                         # 🤖 Feature 1: Test Generation
│   │   │   └── test_author.py           # AI test generator
│   │   │
│   │   ├── detectors/                   # 🔧 Supporting Tools
│   │   │   └── test_framework.py        # Test framework detector
│   │   │
│   │   └── models/                      # 📋 Data Models
│   │       └── github_issue.py          # GitHub issue Pydantic models
│   │
│   ├── requirements.txt                 # Python dependencies
│   └── Dockerfile                       # Container configuration
│
├── docs/                                # 📚 Documentation
│   ├── COVERAGE_GUIDE.md                # Coverage feature deep dive
│   ├── COVERAGE_IMPLEMENTATION.md       # Coverage implementation details
│   ├── TEST_OPTIMIZATION_GUIDE.md       # Optimization feature deep dive
│   ├── TEST_OPTIMIZATION_IMPLEMENTATION.md  # Optimization implementation details
│   ├── OPTIMIZATION_QUICKSTART.md       # Quick setup for optimization
│   └── README.md                        # Documentation index
│
├── examples/                            # 💡 Usage Examples
│   ├── generate_tests_example.sh        # Example API calls
│   └── sample_github_issue.md           # Example issue format
│
├── .env.example                         # Environment template (reference only)
├── .env                                 # Your config (auto-generated by onboard.py)
├── .tool_state.json                     # Tool state (auto-generated, gitignored)
├── docker-compose.yml                   # Docker setup
├── QUICK_START.md                       # Quick start guide
├── CHANGELOG.md                         # Version history
└── README.md                            # This file
```

## 🔌 API Endpoints

### 1️⃣ Generate Tests from Issue

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
  "optimization_report": {
    "quality_score": 8,
    "similar_tests": 0,
    "suggestions": ["Consider parameterizing test cases"]
  },
  "coverage_report": {
    "overall_coverage": 85.5,
    "new_coverage": 12.3,
    "uncovered_lines": 47
  }
}
```

**Notes:**
- Optimization report included if `ENABLE_OPTIMIZATION=true`
- Coverage report included if `ENABLE_COVERAGE_ANALYSIS=true`

---

### 2️⃣ Analyze Test Coverage

```bash
POST /github/analyze-coverage
Content-Type: application/json

{
  "repo_override": "owner/repo",  // optional
  "test_path": "tests/",          // optional, defaults to all tests
  "include_gaps": true            // optional, defaults to true
}
```

**Response:**
```json
{
  "success": true,
  "overall_coverage": 85.5,
  "modules": [
    {
      "name": "src/auth.py",
      "coverage": 92.3,
      "lines_covered": 120,
      "lines_total": 130
    }
  ],
  "uncovered_gaps": [
    {
      "file": "src/auth.py",
      "lines": [45, 46, 47],
      "reason": "Error handling not tested"
    }
  ],
  "recommendations": ["Add tests for error handling in auth module"]
}
```

---

### 3️⃣ Optimize Test Suite

```bash
POST /github/optimize-tests
Content-Type: application/json

{
  "test_path": "tests/",          // optional, defaults to all tests
  "similarity_threshold": 0.7,    // optional, defaults to 0.7
  "repo_override": "owner/repo"   // optional
}
```

**Response:**
```json
{
  "success": true,
  "quality_score": 7,
  "similar_tests": [
    {
      "test1": "test_login_valid_user",
      "test2": "test_login_authenticated_user",
      "similarity": 0.85
    }
  ],
  "redundant_tests": [
    {
      "test": "test_old_feature",
      "reason": "References deleted module 'old_api.py'"
    }
  ],
  "ai_suggestions": [
    "Consider parameterizing test_login_* tests",
    "Extract common setup into fixture"
  ]
}
```

---

### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "service": "github-test-authoring-tool",
  "features": {
    "test_generation": true,
    "coverage_analysis": true,
    "test_optimization": true
  }
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

## 🔄 Updating Configuration

To update your configuration (change API keys, switch repos, enable/disable features):

```bash
# Re-run the onboarding script
python onboard.py
```

The script will:
- Detect existing configuration
- Offer to keep or update each setting
- Backup your old configuration
- Generate new `.env` and `.tool_state.json` files

## 🐛 Troubleshooting

### Missing Configuration

**Error**: `Configuration not found` or `Missing environment variables`

**Solution**: 
```bash
# Run onboarding to create configuration
python onboard.py
```

### Invalid Configuration

**Error**: `Failed to load configuration` or `Invalid API key`

**Solution**:
```bash
# Re-run onboarding to update configuration
python onboard.py

# The script will validate your credentials in real-time
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

### Configuration Files

The tool uses two configuration sources:

1. **`.env`** - Environment variables (auto-generated by `onboard.py`)
   - Contains API keys, repository info, and feature toggles
   - Gitignored for security
   
2. **`.tool_state.json`** - Tool state (auto-generated by `onboard.py`)
   - Tracks configuration history
   - Records usage statistics
   - Enables re-configuration
   - Gitignored for security

**Both files are created automatically during onboarding. You should not need to edit them manually.**

### Core Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | Yes | OpenAI API key | - |
| `OPENAI_MODEL` | No | Model to use | `gpt-4o-mini` |
| `GITHUB_TOKEN` | Yes | GitHub personal access token | - |
| `GITHUB_REPO` | Yes | Target repository (owner/repo) | - |
| `LOG_LEVEL` | No | Logging level | `INFO` |

### Feature Toggles

Enable/disable each of the three core features:

```bash
# Feature 1: Test Generation (always available)
# No toggle needed - this is the base feature

# Feature 2: Coverage Analysis (optional)
ENABLE_COVERAGE_ANALYSIS=true
PYTHON_COVERAGE_TOOL=pytest-cov
JAVASCRIPT_COVERAGE_TOOL=jest
COVERAGE_TIMEOUT_SECONDS=300
COVERAGE_INCLUDE_GAPS=true

# Feature 3: Test Optimization (optional)
ENABLE_OPTIMIZATION=true
ENABLE_SIMILARITY_DETECTION=true
ENABLE_AI_SUGGESTIONS=true
ENABLE_REDUNDANCY_DETECTION=true
SIMILARITY_THRESHOLD=0.7
```

**Note**: Test generation always runs. Coverage and optimization are optional add-ons that enhance the results.

### Customizing Test Generation

To modify test generation behavior, edit:

**Configuration Models**: `backend/app/config/models.py`
- Add new configuration options
- Modify validation rules
- Extend feature settings

**Framework Detection**: `backend/app/detectors/test_framework.py`
- Add new frameworks
- Modify detection patterns
- Change test directory conventions

**Repository Compatibility**: `backend/app/config/compatibility.py`
- Add language support
- Modify framework detection
- Adjust size limits

**AI Prompts**: `backend/app/llm/test_author.py`
- Adjust system prompts
- Modify temperature (creativity)
- Change token limits

**Code Search**: `backend/app/github/code_search.py`
- Modify keyword extraction
- Adjust number of files searched
- Change context building logic

## 📚 Documentation

### Getting Started
- **[Onboarding Guide](ONBOARDING_GUIDE.md)** - Complete setup walkthrough with guided or manual options
- **[Quick Start Guide](QUICK_START.md)** - Fast setup instructions

### Feature Guides
- **[Test Optimization Guide](docs/TEST_OPTIMIZATION_GUIDE.md)** - Similarity detection, AI suggestions, redundancy detection
- **[Test Optimization Implementation](docs/TEST_OPTIMIZATION_IMPLEMENTATION.md)** - Technical implementation details
- **[Coverage Integration Guide](docs/COVERAGE_GUIDE.md)** - Before/after coverage, gap analysis
- **[Coverage Implementation](docs/COVERAGE_IMPLEMENTATION.md)** - Technical implementation details
- **[Optimization Quick Start](docs/OPTIMIZATION_QUICKSTART.md)** - Fast setup for optimization features

### Repository Information
- **[Changelog](CHANGELOG.md)** - Version history and updates
- **[Cleanup Summary](CLEANUP_SUMMARY.md)** - Repository cleanup documentation
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
# 1. Complete onboarding first
python onboard.py

# 2. Start with hot reload
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
  
# Analyze coverage
curl -X POST http://localhost:8000/github/analyze-coverage \
  -H "Content-Type: application/json" \
  -d '{"test_path": "tests/"}'
  
# Optimize tests
curl -X POST http://localhost:8000/github/optimize-tests \
  -H "Content-Type: application/json" \
  -d '{"test_path": "tests/"}'
```

### Viewing Logs

```bash
# Logs show each step with configuration info
INFO: Starting GitHub Test Authoring Tool API
INFO: Configuration loaded successfully.
INFO: Current GitHub Repo: owner/repo
INFO: OpenAI Model: gpt-4o-mini
INFO: Fetching issue #1 from GitHub
INFO: Detected framework: pytest
INFO: Found 3 relevant code files
INFO: Generating tests with AI
INFO: Creating branch: auto-tests/issue-1
INFO: Created PR #45: 🤖 Automated Tests for #1
INFO: Updating tool state with usage statistics
```

### State Management

The tool maintains state in `.tool_state.json`:
- **Configuration history**: Track when settings were changed
- **Usage statistics**: Count of tests generated, PRs created
- **Last used**: Timestamp of last operation
- **Repository metadata**: Framework, language, last analysis

View state:
```bash
cat .tool_state.json | python -m json.tool
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
