# Test Optimization - Quick Start Guide

Get the Test Case Optimization feature running in 5 minutes!

## 🚀 Quick Setup

### Step 1: Install Dependency
```bash
cd backend
pip install numpy==1.26.0
```

### Step 2: Update Configuration
Add to your `.env` file:
```bash
# Test Case Optimization Feature
ENABLE_TEST_OPTIMIZATION=true

# Similarity Detection
SIMILARITY_THRESHOLD=0.70
SIMILARITY_USE_EMBEDDINGS=true

# AI Suggestions
ENABLE_AI_SUGGESTIONS=true
AI_OPTIMIZATION_MODEL=gpt-4o-mini

# Redundancy Detection
CHECK_REDUNDANT_TESTS=true
CHECK_OUTDATED_IMPORTS=true
```

### Step 3: Start Backend
```bash
cd backend
python3 -m uvicorn app.main:app --reload --port 8000
```

### Step 4: Generate Tests
```bash
curl -X POST http://localhost:8000/github/generate-tests \
  -H "Content-Type: application/json" \
  -d '{"issue_number": 1}'
```

### Step 5: Check Results
Go to your GitHub repository and check the created PR. You'll see:

```markdown
## 🔍 Test Case Optimization Report

### 📊 Summary
- ✅ No similar tests detected
- 💡 **2 optimization opportunities** found

### 💡 AI-Powered Optimization Suggestions
...

### ✅ Quality Score: 8.5/10
```

---

## ⚙️ Configuration Options

### Reduce Costs
Disable AI suggestions (saves ~$0.001-0.005 per run):
```bash
ENABLE_AI_SUGGESTIONS=false
```

Disable embeddings (saves ~$0.0001 per run):
```bash
SIMILARITY_USE_EMBEDDINGS=false
```

### Adjust Sensitivity
Lower similarity threshold to catch more similar tests:
```bash
SIMILARITY_THRESHOLD=0.60  # 60% instead of 70%
```

### Disable Entirely
```bash
ENABLE_TEST_OPTIMIZATION=false
```

---

## 📊 Understanding Reports

### Quality Scores

| Score | Rating | Meaning |
|-------|--------|---------|
| 9-10 | Excellent 🎉 | No issues found |
| 7-8.9 | Good ✅ | Minor suggestions |
| 5-6.9 | Fair ⚠️ | Several issues |
| <5 | Needs Work ❌ | Major issues |

### Report Sections

1. **Similar Tests**: Tests that are >70% alike (can be consolidated)
2. **AI Suggestions**: Improvement opportunities (parametrization, fixtures, etc.)
3. **Redundant Tests**: Duplicates of existing tests
4. **Outdated Code**: References to removed modules

---

## 🐛 Troubleshooting

### "No report in PR"
✅ Check: `ENABLE_TEST_OPTIMIZATION=true`  
✅ Verify: OpenAI API key is valid

### "Similarity not detecting duplicates"
✅ Check: `SIMILARITY_USE_EMBEDDINGS=true`  
✅ Verify: OpenAI has available quota

### "AI suggestions are empty"
✅ Check: `ENABLE_AI_SUGGESTIONS=true`  
✅ Verify: Model name is correct (`gpt-4o-mini`)

### "Import errors"
```bash
pip install numpy==1.26.0
```

---

## 💡 Pro Tips

1. **First Run**: Keep all optimizations enabled to see full capabilities
2. **Cost Optimization**: Disable AI suggestions after initial testing
3. **Threshold Tuning**: Start with 0.70, lower if needed
4. **Review Patterns**: Look for recurring suggestions to improve test patterns

---

## 📚 Learn More

- Full Guide: `TEST_OPTIMIZATION_GUIDE.md`
- Implementation Details: `TEST_OPTIMIZATION_IMPLEMENTATION.md`
- Main README: `README.md`

---

## ✅ Checklist

- [ ] numpy installed
- [ ] .env updated with optimization settings
- [ ] Backend running
- [ ] OpenAI API key has credits
- [ ] GitHub token has repo access
- [ ] Test generation works
- [ ] PR shows optimization report

---

**Status**: Ready to use!  
**Time to setup**: ~5 minutes  
**Cost per run**: ~$0.001-0.006 (with all features enabled)


