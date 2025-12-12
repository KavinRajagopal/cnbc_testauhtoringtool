#!/bin/bash

# Pre-commit verification script
# Checks everything is safe before pushing to GitHub

echo "🔍 Pre-Commit Verification"
echo "=========================="
echo ""

ERRORS=0
WARNINGS=0

# Check 1: No .env files
echo "1️⃣  Checking for .env files..."
if [ -f .env ] || [ -f .env.bak ]; then
    echo "   ❌ CRITICAL: .env files found!"
    echo "   These contain secrets and must NOT be committed."
    echo "   Run: rm .env .env.bak"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ No .env files found"
fi

# Check 2: No __pycache__
echo "2️⃣  Checking for Python cache..."
PYCACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYCACHE_COUNT" -gt 0 ]; then
    echo "   ⚠️  Warning: $PYCACHE_COUNT __pycache__ directories found"
    echo "   These are in .gitignore but should be cleaned"
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ No cache directories found"
fi

# Check 3: .gitignore exists
echo "3️⃣  Checking .gitignore..."
if [ ! -f .gitignore ]; then
    echo "   ❌ CRITICAL: .gitignore missing!"
    ERRORS=$((ERRORS + 1))
else
    if grep -q "^\.env$" .gitignore; then
        echo "   ✅ .gitignore properly configured"
    else
        echo "   ❌ CRITICAL: .env not in .gitignore!"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check 4: Required files exist
echo "4️⃣  Checking required files..."
REQUIRED_FILES=(
    "README.md"
    "CHANGELOG.md"
    "LICENSE"
    "env.example"
    "backend/requirements.txt"
    "backend/app/main.py"
    "docs/README.md"
)

MISSING=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "   ❌ Missing: $file"
        MISSING=$((MISSING + 1))
    fi
done

if [ $MISSING -eq 0 ]; then
    echo "   ✅ All required files present"
else
    echo "   ❌ $MISSING required files missing"
    ERRORS=$((ERRORS + 1))
fi

# Check 5: No API keys in code
echo "5️⃣  Scanning for API keys in code..."
if grep -r "sk-" --include="*.py" --include="*.md" backend/ 2>/dev/null | grep -v "sk-your" | grep -v "sk-xxx" | grep -q "sk-"; then
    echo "   ⚠️  Warning: Possible API key found in code!"
    echo "   Please review and remove any hardcoded keys"
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ No API keys detected in code"
fi

# Check 6: Documentation complete
echo "6️⃣  Checking documentation..."
DOC_COUNT=$(find docs -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
if [ "$DOC_COUNT" -lt 5 ]; then
    echo "   ⚠️  Warning: Only $DOC_COUNT docs found (expected 7+)"
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ Documentation complete ($DOC_COUNT files)"
fi

# Check 7: Git status
echo "7️⃣  Checking git status..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    UNTRACKED=$(git status --porcelain | grep "^??" | wc -l | tr -d ' ')
    MODIFIED=$(git status --porcelain | grep "^ M" | wc -l | tr -d ' ')
    echo "   ✅ Git repository initialized"
    echo "   📊 Untracked files: $UNTRACKED"
    echo "   📊 Modified files: $MODIFIED"
else
    echo "   ❌ Not a git repository"
    ERRORS=$((ERRORS + 1))
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "VERIFICATION SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo "✅ No critical errors found"
else
    echo "❌ $ERRORS critical error(s) found"
fi

if [ $WARNINGS -eq 0 ]; then
    echo "✅ No warnings"
else
    echo "⚠️  $WARNINGS warning(s) found"
fi

echo ""

if [ $ERRORS -eq 0 ]; then
    echo "🎉 SAFE TO COMMIT!"
    echo ""
    echo "Next steps:"
    echo "  1. Review changes: git status"
    echo "  2. Commit: ./commit_to_github.sh [repo-url]"
    echo "  3. Or manually: git add . && git commit && git push"
    exit 0
else
    echo "❌ NOT SAFE TO COMMIT"
    echo ""
    echo "Please fix the errors above before committing."
    exit 1
fi

