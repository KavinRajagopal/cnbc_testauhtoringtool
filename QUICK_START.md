# Quick Start Guide

Get your GitHub Test Authoring Tool running in 5 minutes!

## ⚡ Super Quick Setup

### 1. Install Dependencies (1 min)
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment (2 min)
```bash
# Copy template
cp env.example .env

# Edit with your credentials
nano .env
```

Required values:
```bash
OPENAI_API_KEY=sk-your-key-here
GITHUB_TOKEN=ghp_your-token-here
GITHUB_REPO=owner/repository-name
```

### 3. Start the Server (30 sec)
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 4. Generate Tests (1 min)
```bash
# Create an issue in your GitHub repo, then:
curl -X POST http://localhost:8000/github/generate-tests \
  -H "Content-Type: application/json" \
  -d '{"issue_number": YOUR_ISSUE_NUMBER}'
```

That's it! Check your repo for a new PR with generated tests. 🎉

## 📋 Prerequisites Checklist

- [ ] Python 3.11+
- [ ] OpenAI API Key ([Get one](https://platform.openai.com/api-keys))
- [ ] GitHub Personal Access Token with `repo` and `workflow` permissions ([Create one](https://github.com/settings/tokens))
- [ ] Target GitHub repository

## 🎯 Quick Feature Enable

### Enable Test Optimization
Add to `.env`:
```bash
ENABLE_OPTIMIZATION=true
```

### Enable Coverage Analysis
Add to `.env`:
```bash
ENABLE_COVERAGE_ANALYSIS=true
```

## 🔧 Troubleshooting

### "Missing environment variables"
→ Check `.env` file exists and has all required values

### "401 Unauthorized" 
→ Verify your `GITHUB_TOKEN` is correct and has `repo` permissions

### "OpenAI API error"
→ Check your `OPENAI_API_KEY` and ensure you have credits

### Server won't start
→ Make sure port 8000 is available: `lsof -i :8000`

## 📚 Next Steps

1. **Read the main README**: `README.md` for comprehensive docs
2. **Enable optimization**: See `docs/OPTIMIZATION_QUICKSTART.md`
3. **Configure coverage**: See `docs/COVERAGE_GUIDE.md`
4. **Customize behavior**: Edit files in `backend/app/`

## 💡 Tips

- Use clear acceptance criteria in your GitHub issues (AC1, AC2, etc.)
- Start with Python/pytest for easiest setup
- Check PR comments for optimization suggestions
- Coverage analysis works best with existing test infrastructure

## 🆘 Need Help?

- Check the [full documentation](README.md)
- Review [troubleshooting guides](docs/)
- Open an issue on GitHub

---

**Happy Testing! 🚀**

