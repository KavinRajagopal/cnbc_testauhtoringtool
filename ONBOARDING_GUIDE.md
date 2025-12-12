# Onboarding Guide

Complete guide to setting up the GitHub Test Authoring Tool.

## Prerequisites

Before running the onboarding script, ensure you have:

- **Python 3.11+** installed
- **Git** installed
- **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)
- **GitHub Personal Access Token** - [Create one here](https://github.com/settings/tokens)
  - Required permissions: `repo` (full), `workflow`

## Quick Setup

### Option 1: Guided Setup (Recommended - 3-5 minutes)

1. Clone this repository:
```bash
git clone <repo-url>
cd cnbc_testauhtoringtool
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
cd ..
```

3. Run the onboarding script:
```bash
python onboard.py
```

4. Choose option **1** (Guided Setup)

5. Follow the interactive prompts:
   - Enter your OpenAI API key
   - Enter your GitHub token
   - Enter your target repository (format: owner/repo)
   - Review detected configuration
   - Configure optional settings (or skip)
   - Confirm configuration

6. Start using the tool:
```bash
cd backend
uvicorn app.main:app --reload
```

### Option 2: Manual Setup (For experienced users - 1-2 minutes)

1. Clone and install dependencies (same as above)

2. Run onboarding and choose option **2** (Manual Setup)

3. Edit the generated `.env` file with your credentials

4. Start the tool

## Detailed Walkthrough

### Step 1: OpenAI Configuration

The tool will prompt for your OpenAI API key:

```
Step 1/3: OpenAI Configuration
════════════════════════════════

Enter your OpenAI API key (starts with 'sk-'):
> sk-...

⏳ Validating key with OpenAI API...
✓ Valid! Connected to OpenAI successfully.
```

**What happens:**
- Makes a real API call to validate your key
- Checks that you have sufficient credits
- Stores the key securely in `.env`

**Common Errors:**
- **401 Unauthorized**: Key is invalid or expired
  - Solution: Generate a new key at https://platform.openai.com/api-keys
- **429 Rate Limited**: Too many validation attempts
  - Solution: Wait 60 seconds and try again

### Step 2: GitHub Configuration

The tool will validate your GitHub token:

```
Step 2/3: GitHub Configuration
════════════════════════════════

Enter your GitHub Personal Access Token:
> ghp_...

⏳ Validating token with GitHub API...
⏳ Checking permissions...
✓ Valid! Token has required permissions (repo, workflow)
```

**What happens:**
- Calls GitHub API to verify token
- Checks that token has `repo` and `workflow` scopes
- Ensures you can access repositories

**Common Errors:**
- **401 Unauthorized**: Token is invalid
  - Solution: Create new token at https://github.com/settings/tokens
- **403 Forbidden**: Token doesn't have required permissions
  - Solution: Update token to include `repo` and `workflow` scopes

### Step 3: Target Repository

The tool will verify repository access:

```
Step 3/3: Target Repository
════════════════════════════════

Enter repository (format: owner/repo):
> microsoft/playwright

⏳ Checking repository access...
✓ Repository found and accessible!

Repository details:
• Name: playwright
• Language: TypeScript
• Stars: 50.2k
• Last updated: 2 hours ago
```

**What happens:**
- Verifies repository exists
- Checks your token has access
- Retrieves repository metadata

**Common Errors:**
- **404 Not Found**: Repository doesn't exist or name is misspelled
  - Solution: Check spelling and format (owner/repo)
- **403 Forbidden**: Private repo without access
  - Solution: Ensure token has access to private repos

### Step 4: Repository Analysis

The tool performs a shallow clone and detects your setup:

```
Analyzing Repository
════════════════════════════════

⏳ Cloning repository (shallow, latest commit only)...
⏳ Detecting test framework...
⏳ Scanning for existing tests...

✓ Analysis complete!

Detected Configuration:
• Framework: pytest
• Language: Python 3.11
• Test Directory: tests/
• Existing Tests: 42 files
• Source Directory: src/

Does this look correct? (yes/no/override)
```

**What happens:**
- Performs a shallow git clone (only latest commit)
- Scans for test framework config files
- Counts existing test files
- Auto-detects directory structure

**What is Shallow Clone?**
A shallow clone (`git clone --depth=1`) downloads only the latest commit instead of the full history. This is:
- Much faster (seconds vs minutes)
- Uses less disk space  
- Perfect for analyzing current code state

### Step 5: Optional Configuration

Configure advanced settings or skip:

```
Optional Configuration
════════════════════════════════

The following settings are OPTIONAL. You can:
• Configure them now
• Skip all (press 's')
• Configure some (press Enter on each)

Press 's' to skip all, or Enter to continue:
```

**Optional Settings:**
- **Test naming conventions**: Custom patterns for test files
- **Repository structure**: Source and test directory hints
- **Coding standards**: Style guides and linting rules
- **Coverage goals**: Minimum coverage percentages
- **Exclusions**: Directories/files to ignore

**Recommendation:** Skip optional settings for first-time setup. You can always reconfigure later.

### Step 6: Configuration Summary

Review everything before saving:

```
╔═══════════════════════════════════════════════════════════╗
║              CONFIGURATION SUMMARY                        ║
╚═══════════════════════════════════════════════════════════╝

✓ Required Settings (Validated)
═══════════════════════════════════════════════════════════
OpenAI API Key      : sk-...abc (✓ Valid, Model: gpt-4o-mini)
GitHub Token        : ghp_...xyz (✓ Valid, Scopes: repo, workflow)
Target Repository   : microsoft/playwright (✓ Accessible)

✓ Detected Settings
═══════════════════════════════════════════════════════════
Framework           : pytest
Language            : Python 3.11
Test Directory      : tests/
Existing Tests      : 42 files
Source Directory    : src/

═══════════════════════════════════════════════════════════

Does this configuration look correct?

Options:
  [y] Yes, save this configuration
  [n] No, cancel and exit
  [e] Edit specific sections

Your choice:
```

**Options:**
- **[y]** Yes: Save configuration and complete setup
- **[n]** No: Cancel and exit (no changes made)
- **[e]** Edit: Go back and modify specific sections

### Step 7: Setup Complete!

Configuration is saved and you're ready to use the tool:

```
🎉 Setup Complete!

Generated Files:
  ✓ .env (required settings)
  ✓ .tool_state.json (state tracking)

Next Steps:
  1. Start the server:
     $ cd backend
     $ uvicorn app.main:app --reload

  2. Use any of the three features:
     
     Feature 1: Generate Tests
     $ curl -X POST http://localhost:8000/github/generate-tests \
       -d '{"issue_number": 123}'
     
     Feature 2: Analyze Coverage
     $ curl -X POST http://localhost:8000/github/analyze-coverage
     
     Feature 3: Optimize Tests
     $ curl -X POST http://localhost:8000/github/optimize-tests
```

## Re-running Onboarding

If you run `python onboard.py` with an existing configuration:

```
╔═══════════════════════════════════════════════════════════╗
║         Existing Configuration Detected                   ║
╚═══════════════════════════════════════════════════════════╝

Found existing configuration for:
Repository: microsoft/playwright
Configured: 2024-12-10 at 14:30

What would you like to do?

  [e] Edit existing configuration
      → Load current values and modify them
      → Quick way to update settings

  [f] Start fresh (current config will be backed up)
      → Complete new onboarding
      → Old config saved to .env.backup

  [c] Cancel
      → Keep current configuration

Your choice (e/f/c):
```

## Troubleshooting

### "Python 3.11+ required"
**Problem:** Your Python version is too old

**Solution:**
```bash
# Check your version
python3 --version

# Install Python 3.11+ from python.org or use pyenv
pyenv install 3.11
pyenv global 3.11
```

### "ModuleNotFoundError"
**Problem:** Dependencies not installed

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### "Failed to clone repository"
**Problem:** Large repository or network issues

**Solution:**
- Check internet connection
- Try again (shallow clone is resumable)
- For very large repos (>1GB), analysis may timeout

### "Configuration file not found"
**Problem:** `.env` file missing

**Solution:**
```bash
# Run onboarding again
python onboard.py
```

## Configuration Files

### `.env` (Required)
Contains your credentials and configuration. **Never commit this file!**

Located at project root. Example:
```bash
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...
GITHUB_REPO=owner/repo
```

### `.tool_state.json` (Auto-generated)
Tracks tool usage and configuration history. Also git-ignored.

Located at project root. Contains:
- Last configuration date
- Repository details
- Usage statistics (tests generated, coverage runs, etc.)

### `config.json` (Optional)
Advanced optional settings. Only created if you configure optional settings.

## Next Steps

After onboarding:

1. **Start the server**:
```bash
cd backend
uvicorn app.main:app --reload
```

2. **Create a GitHub issue** in your target repository with acceptance criteria

3. **Generate tests** for that issue

4. **Review the PR** that the tool creates

5. **Explore the documentation** in the `docs/` directory

## Getting Help

- **README.md**: Main documentation
- **docs/**: Feature-specific guides
- **GitHub Issues**: Report bugs or request features

---

**Ready to generate tests? Let's go! 🚀**

