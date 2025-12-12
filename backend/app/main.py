"""FastAPI application entry point."""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GitHub Test Authoring Tool",
    description="Automatically generate tests from GitHub issues using AI",
    version="1.0.0",
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting GitHub Test Authoring Tool API")
    
    try:
        # Load and validate configuration
        from app.config.loader import ConfigLoader
        
        config_loader = ConfigLoader()
        validation_result = config_loader.validate_on_startup()
        
        if not validation_result.success:
            logger.error("=" * 60)
            logger.error("Configuration Error!")
            logger.error("=" * 60)
            logger.error(validation_result.error_message)
            logger.error("")
            logger.error("Please run the onboarding script to configure the tool:")
            logger.error("  $ python onboard.py")
            logger.error("=" * 60)
            # Don't exit - let the app start but warn user
            return
        
        # Load configuration and state
        config = config_loader.load()
        state = config_loader.get_state()
        
        # Display configuration info
        logger.info("=" * 60)
        logger.info("Configuration loaded successfully!")
        logger.info("=" * 60)
        logger.info(f"Repository: {config.required.github_repo}")
        
        if state.configuration:
            logger.info(f"Framework: {state.configuration.framework}")
            logger.info(f"Language: {state.configuration.language}")
        
        # Check which features are enabled
        features_enabled = []
        features_enabled.append("Test Generation")
        
        if os.getenv("ENABLE_COVERAGE_ANALYSIS", "false").lower() == "true":
            features_enabled.append("Coverage Analysis")
        
        if os.getenv("ENABLE_TEST_OPTIMIZATION", "true").lower() == "true":
            features_enabled.append("Test Optimization")
        
        logger.info(f"Features enabled: {', '.join(features_enabled)}")
        
        if state.usage_stats:
            logger.info(f"Usage stats: {state.usage_stats.tests_generated} tests generated, "
                       f"{state.usage_stats.coverage_analyses} coverage analyses, "
                       f"{state.usage_stats.optimizations_run} optimizations")
        
        logger.info("=" * 60)
        logger.info("Ready to generate tests! 🚀")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error("Configuration Error!")
        logger.error("=" * 60)
        logger.error(f"Failed to load configuration: {str(e)}")
        logger.error("")
        logger.error("Please run the onboarding script to configure the tool:")
        logger.error("  $ python onboard.py")
        logger.error("=" * 60)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Import and include GitHub routes
from app.github_webhook import router as github_router

app.include_router(github_router, prefix="/github", tags=["github"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)








