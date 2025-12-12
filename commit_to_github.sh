#!/bin/bash

# Script to commit the cleaned repository to GitHub
# Usage: ./commit_to_github.sh [repository-url]

set -e

echo "🧹 GitHub Test Authoring Tool - Initial Commit Script"
echo "=================================================="
echo ""

# Check if repository URL is provided
if [ $# -eq 0 ]; then
    echo "❓ Enter your GitHub repository URL (e.g., https://github.com/username/repo.git):"
    read REPO_URL
else
    REPO_URL=$1
fi

echo ""
echo "📋 Repository Status:"
echo "-------------------"
git status --short

echo ""
echo "📊 Statistics:"
echo "-------------"
echo "Total files: $(find . -type f -not -path '*/\.*' | wc -l | tr -d ' ')"
echo "Python files: $(find backend -name "*.py" 2>/dev/null | wc -l | tr -d ' ')"
echo "Documentation: $(find . -name "*.md" 2>/dev/null | wc -l | tr -d ' ')"

echo ""
echo "🔒 Security Check:"
echo "-----------------"
if [ -f .env ]; then
    echo "⚠️  WARNING: .env file found! This should NOT be committed."
    echo "   Remove it with: rm .env"
    exit 1
else
    echo "✅ No .env file found - safe to commit"
fi

if git ls-files | grep -q "\.env$"; then
    echo "⚠️  WARNING: .env is tracked by git!"
    exit 1
else
    echo "✅ .env is not tracked by git"
fi

echo ""
echo "📝 This will commit with the following message:"
echo "-----------------------------------------------"
cat << 'EOF'
feat: Initial commit - GitHub Test Authoring Tool POC

Features:
- Automated test generation from GitHub issues
- Test framework detection (pytest, jest, playwright, etc.)
- AI-powered test generation with OpenAI
- Test case optimization (similarity, AI suggestions, redundancy)
- Coverage integration (before/after comparison, gap analysis)
- Automated Git operations (branch, commit, PR)
- Comprehensive documentation and guides

Tech Stack:
- Python 3.11+ (FastAPI, Pydantic)
- OpenAI API (GPT-4)
- GitHub API (PyGithub)
- Coverage tools (pytest-cov, jest)
- Docker support
EOF

echo ""
echo "🤔 Do you want to proceed? (y/n)"
read -r CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "❌ Commit cancelled."
    exit 0
fi

echo ""
echo "🚀 Starting commit process..."
echo ""

# Stage all files
echo "📦 Staging files..."
git add .

# Show what will be committed
echo ""
echo "📋 Files to be committed:"
git status --short

# Commit
echo ""
echo "💾 Creating commit..."
git commit -m "feat: Initial commit - GitHub Test Authoring Tool POC

Features:
- Automated test generation from GitHub issues
- Test framework detection (pytest, jest, playwright, etc.)
- AI-powered test generation with OpenAI
- Test case optimization (similarity, AI suggestions, redundancy)
- Coverage integration (before/after comparison, gap analysis)
- Automated Git operations (branch, commit, PR)
- Comprehensive documentation and guides

Tech Stack:
- Python 3.11+ (FastAPI, Pydantic)
- OpenAI API (GPT-4)
- GitHub API (PyGithub)
- Coverage tools (pytest-cov, jest)
- Docker support"

# Set up remote if needed
echo ""
echo "🔗 Setting up remote repository..."
if git remote | grep -q "origin"; then
    echo "✅ Remote 'origin' already exists"
    git remote set-url origin "$REPO_URL"
else
    git remote add origin "$REPO_URL"
fi

# Create and checkout main branch
echo ""
echo "🌿 Setting up main branch..."
git branch -M main

# Push to GitHub
echo ""
echo "☁️  Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Success! Repository pushed to GitHub"
echo ""
echo "🔗 Repository URL: $REPO_URL"
echo ""
echo "📝 Next steps:"
echo "   1. Visit your repository on GitHub"
echo "   2. Copy env.example to .env and add your credentials"
echo "   3. Follow the README.md for setup instructions"
echo ""
echo "🎉 Happy testing!"

