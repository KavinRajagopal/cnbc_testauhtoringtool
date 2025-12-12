# Documentation

Comprehensive guides for the GitHub Test Authoring Tool features.

## 📚 Available Guides

### Core Features
- **[Main README](../README.md)** - Overview, setup, and basic usage

### Advanced Features

#### Test Optimization
- **[Test Optimization Guide](TEST_OPTIMIZATION_GUIDE.md)** - Complete guide to test case optimization features
- **[Optimization Quickstart](OPTIMIZATION_QUICKSTART.md)** - Quick setup and usage
- **[Implementation Details](TEST_OPTIMIZATION_IMPLEMENTATION.md)** - Technical implementation reference

**Key Features:**
- Similarity detection (>70% threshold)
- AI-powered suggestions for improvements
- Redundancy and outdated test detection
- Quality scoring and recommendations

#### Test Coverage
- **[Coverage Guide](COVERAGE_GUIDE.md)** - Complete guide to coverage integration
- **[Coverage Implementation](COVERAGE_IMPLEMENTATION.md)** - Technical implementation reference

**Key Features:**
- Before/after coverage comparison
- Per-module coverage breakdown
- Coverage gap identification
- Support for Python (pytest-cov) and JavaScript (jest/nyc)

## 🚀 Quick Navigation

### Getting Started
1. Start with the [Main README](../README.md) for setup
2. Review [Optimization Quickstart](OPTIMIZATION_QUICKSTART.md) to enable quality analysis
3. Check [Coverage Guide](COVERAGE_GUIDE.md) to enable coverage reporting

### Configuration
All features can be enabled/disabled via `.env` file:
```bash
# Test Optimization
ENABLE_OPTIMIZATION=true
ENABLE_SIMILARITY_DETECTION=true
ENABLE_AI_SUGGESTIONS=true
ENABLE_REDUNDANCY_DETECTION=true

# Test Coverage
ENABLE_COVERAGE_ANALYSIS=true
COVERAGE_TIMEOUT_SECONDS=300
```

### Troubleshooting
Each guide includes a dedicated troubleshooting section for feature-specific issues.

## 📖 Reading Order

**For New Users:**
1. Main README → Setup → Generate first tests
2. Optimization Quickstart → Enable optimization features
3. Coverage Guide → Enable coverage analysis

**For Developers:**
1. Implementation Details documents for architecture
2. Source code in `backend/app/`
3. Configuration options in `env.example`

---

**Need Help?** Open an issue on GitHub or check the troubleshooting sections in each guide.

