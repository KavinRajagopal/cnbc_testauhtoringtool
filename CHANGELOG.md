# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Test Coverage Integration** (Dec 2024)
  - Before/after coverage comparison
  - Coverage gap analysis
  - Support for Python (pytest-cov) and JavaScript (jest/nyc)
  - Markdown coverage reports posted to GitHub issues
  - Configurable coverage tools and timeouts
  
- **Test Case Optimization** (Dec 2024)
  - Similarity detection using embeddings (>70% threshold)
  - AI-powered test improvement suggestions
  - Redundancy and outdated test detection
  - Quality scoring with actionable recommendations
  - Comprehensive optimization reports in PRs

- **GitHub Integration** (Nov 2024)
  - Automated test generation from GitHub issues
  - Framework detection (pytest, jest, playwright, mocha, vitest, unittest)
  - Smart code search using GitHub Code Search API
  - Automated Git operations (branching, committing, PR creation)
  - Issue commenting with results

### Changed
- **Documentation Organization** (Dec 2024)
  - Created `docs/` directory for better organization
  - Consolidated feature-specific guides
  - Added comprehensive documentation index
  - Updated README with clear feature overview

### Removed
- Legacy JIRA integration components
- Mock application directories
- Temporary test repositories
- Redundant configuration files
- Sensitive `.env` files from repository

## Version History

### v0.3.0 - Coverage Integration (Dec 2024)
**Features:**
- Local repository cloning for coverage analysis
- Python coverage with `pytest-cov`
- JavaScript coverage with `jest`/`nyc`
- Gap identification with line-level precision
- Module-level coverage breakdown

**Configuration:**
- 11 new environment variables for coverage control
- Configurable timeouts and tool selection
- Toggle for gap analysis and recommendations

### v0.2.0 - Test Optimization (Dec 2024)
**Features:**
- Similarity analyzer with embeddings
- AI-powered suggestions for improvements
- Redundancy detection via AST analysis
- Outdated test identification
- Quality scoring system

**Configuration:**
- Individual toggles for each optimization component
- Configurable similarity threshold
- Customizable AI model selection

### v0.1.0 - Initial GitHub POC (Nov 2024)
**Features:**
- GitHub issue parsing
- Test framework detection
- AI-powered test generation
- Automated PR creation
- Basic FastAPI backend

**Configuration:**
- Environment-based configuration
- OpenAI integration
- GitHub API integration

## Configuration Changes

### Environment Variables Added

#### Coverage (v0.3.0)
```bash
ENABLE_COVERAGE_ANALYSIS=false
PYTHON_COVERAGE_TOOL=pytest-cov
JAVASCRIPT_COVERAGE_TOOL=jest
COVERAGE_TIMEOUT_SECONDS=300
COVERAGE_MIN_THRESHOLD=80
COVERAGE_INCLUDE_GAPS=true
COVERAGE_INCLUDE_BRANCH=true
COVERAGE_INCLUDE_RECOMMENDATIONS=true
PYTHON_COVERAGE_COMMAND=pytest --cov
JAVASCRIPT_COVERAGE_COMMAND=npm test -- --coverage
COVERAGE_FAIL_UNDER=false
```

#### Optimization (v0.2.0)
```bash
ENABLE_OPTIMIZATION=true
ENABLE_SIMILARITY_DETECTION=true
ENABLE_AI_SUGGESTIONS=true
ENABLE_REDUNDANCY_DETECTION=true
SIMILARITY_THRESHOLD=0.7
OPTIMIZATION_MODEL=gpt-4o-mini
```

#### Core (v0.1.0)
```bash
OPENAI_API_KEY=required
OPENAI_MODEL=gpt-4o-mini
GITHUB_TOKEN=required
GITHUB_REPO=owner/repository
LOG_LEVEL=INFO
```

## Dependencies Added

### Python Packages
- `PyGithub==2.1.1` - GitHub API client
- `GitPython==3.1.40` - Git operations
- `openai==1.3.0` - AI test generation
- `fastapi==0.109.0` - Web framework
- `pydantic==2.5.3` - Data validation
- `numpy>=1.24.0` - Embeddings calculations
- `coverage==7.3.2` - Python coverage analysis

## Migration Notes

### From v0.2.0 to v0.3.0
- Install new `coverage` package: `pip install -r backend/requirements.txt`
- Add coverage configuration to `.env` (optional, defaults provided)
- Coverage analysis runs automatically when `ENABLE_COVERAGE_ANALYSIS=true`

### From v0.1.0 to v0.2.0
- Install new `numpy` package: `pip install -r backend/requirements.txt`
- Add optimization configuration to `.env` (optional, defaults provided)
- Optimization runs automatically when `ENABLE_OPTIMIZATION=true`

## Breaking Changes

None - all features are backward compatible with toggles.

## Known Issues

### Coverage Analysis
- Large repositories may exceed timeout (increase `COVERAGE_TIMEOUT_SECONDS`)
- Local cloning requires disk space (cleaned up automatically)
- Coverage tools must be installed in target repository

### Test Optimization
- Similarity detection requires OpenAI embeddings (uses API quota)
- Large test files may take longer to analyze
- AST analysis only supports Python syntax

## Future Enhancements

See [README.md](README.md) for planned features.

## Contributors

This project was developed as a POC for automated test generation.

---

**For detailed feature guides, see the [docs/](docs/) directory.**

