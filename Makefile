.PHONY: help install start test clean setup-env verify

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	@echo "Installing Python dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "✅ Dependencies installed"

setup-env: ## Create .env file from example
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "✅ Created .env file. Please edit it with your API keys."; \
	else \
		echo "⚠️  .env file already exists. Skipping."; \
	fi

verify: ## Verify setup and configuration
	@echo "Running setup verification..."
	python test_setup.py

start: ## Start backend server
	@echo "Starting GitHub Test Authoring Tool..."
	cd backend && python -m uvicorn app.main:app --reload --port 8000

start-docker: ## Start backend with Docker Compose
	@echo "Starting with Docker..."
	docker-compose up --build

stop-docker: ## Stop Docker services
	docker-compose down

test-generate: ## Test generation with example (usage: make test-generate ISSUE=1)
	@echo "Generating tests for issue #$(ISSUE)..."
	curl -X POST http://localhost:8000/github/generate-tests \
		-H "Content-Type: application/json" \
		-d '{"issue_number": $(ISSUE)}'

health: ## Check backend health
	@echo "Checking backend health..."
	@curl -s http://localhost:8000/health | python -m json.tool

clean: ## Clean generated files and caches
	@echo "Cleaning Python caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaning Docker volumes..."
	docker-compose down -v 2>/dev/null || true
	@echo "✅ Cleaned"

logs: ## Show Docker logs
	docker-compose logs -f backend








