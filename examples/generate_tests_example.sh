#!/bin/bash
# Example script to generate tests for a GitHub issue

# Configuration
API_URL="http://localhost:8000"
ISSUE_NUMBER="${1:-1}"  # Default to issue #1 if not provided

echo "=================================="
echo "GitHub Test Generation Example"
echo "=================================="
echo ""
echo "Configuration:"
echo "  API URL: $API_URL"
echo "  Issue Number: #$ISSUE_NUMBER"
echo ""

# Check if backend is running
echo "Checking if backend is running..."
if ! curl -s -f "$API_URL/health" > /dev/null; then
    echo "❌ Backend is not running!"
    echo ""
    echo "Please start the backend first:"
    echo "  cd backend"
    echo "  python -m uvicorn app.main:app --reload --port 8000"
    echo ""
    exit 1
fi

echo "✅ Backend is running"
echo ""

# Generate tests
echo "Generating tests for issue #$ISSUE_NUMBER..."
echo ""

response=$(curl -s -X POST "$API_URL/github/generate-tests" \
  -H "Content-Type: application/json" \
  -d "{\"issue_number\": $ISSUE_NUMBER}")

# Parse response
success=$(echo "$response" | grep -o '"success":[^,]*' | cut -d':' -f2)

if [ "$success" = "true" ]; then
    echo "✅ Test generation successful!"
    echo ""
    
    # Extract details
    pr_url=$(echo "$response" | grep -o '"pull_request_url":"[^"]*"' | cut -d'"' -f4)
    branch=$(echo "$response" | grep -o '"branch_name":"[^"]*"' | cut -d'"' -f4)
    test_files=$(echo "$response" | grep -o '"test_files":\[[^]]*\]' | sed 's/.*\[\(.*\)\].*/\1/')
    
    echo "Details:"
    echo "  Branch: $branch"
    echo "  Test Files: $test_files"
    echo "  Pull Request: $pr_url"
    echo ""
    echo "🎉 Check your repository for the new PR!"
else
    echo "❌ Test generation failed"
    echo ""
    echo "Response:"
    echo "$response" | python -m json.tool 2>/dev/null || echo "$response"
    echo ""
fi


