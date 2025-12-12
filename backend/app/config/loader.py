"""Configuration loader with state integration."""

import json
import logging
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from .models import (
    RequiredConfig, OptionalConfig, FullConfiguration,
    RepoStructure, CoverageGoals, Exclusions, CodingStandards,
    TestConventions, ValidationResult
)
from .state_manager import StateManager

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class ConfigLoader:
    """
    Configuration loader that reads from .env and config.json.
    
    Integrates with state management to provide a complete configuration
    for the application.
    """
    
    def __init__(self, env_file: Optional[Path] = None, config_file: Optional[Path] = None):
        """
        Initialize configuration loader.
        
        Args:
            env_file: Path to .env file (default: project root)
            config_file: Path to config.json file (default: project root)
        """
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.env_file = env_file or self.project_root / ".env"
        self.config_file = config_file or self.project_root / "config.json"
        self.state_manager = StateManager()
        self._config: Optional[FullConfiguration] = None
    
    def load(self) -> FullConfiguration:
        """
        Load configuration from all sources.
        
        Returns:
            FullConfiguration object
            
        Raises:
            ConfigurationError: If required configuration is missing or invalid
        """
        # Load .env file
        if not self.env_file.exists():
            raise ConfigurationError(
                f"Configuration file not found: {self.env_file}\n\n"
                f"Please run the onboarding script:\n"
                f"  $ python onboard.py"
            )
        
        load_dotenv(self.env_file)
        
        # Load required configuration
        required = self._load_required_config()
        
        # Load optional configuration
        optional = self._load_optional_config()
        
        # Load repository info from state
        state = self.state_manager.load()
        repo_info = None
        if state.configuration:
            from .models import RepositoryInfo
            repo_info = RepositoryInfo(
                framework=state.configuration.framework or "unknown",
                language=state.configuration.language or "unknown",
                test_directory="tests",
                existing_test_count=0,
                detected_at=state.configuration.last_validated or ""
            )
        
        self._config = FullConfiguration(
            required=required,
            optional=optional,
            repository_info=repo_info
        )
        
        logger.info(f"Configuration loaded for repository: {required.github_repo}")
        return self._config
    
    def _load_required_config(self) -> RequiredConfig:
        """
        Load required configuration from environment.
        
        Returns:
            RequiredConfig object
            
        Raises:
            ConfigurationError: If required variables are missing
        """
        missing = []
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            missing.append("OPENAI_API_KEY")
        
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            missing.append("GITHUB_TOKEN")
        
        github_repo = os.getenv("GITHUB_REPO")
        if not github_repo:
            missing.append("GITHUB_REPO")
        
        if missing:
            raise ConfigurationError(
                f"Missing required environment variables: {', '.join(missing)}\n\n"
                f"Please run the onboarding script:\n"
                f"  $ python onboard.py"
            )
        
        return RequiredConfig(
            openai_api_key=openai_key,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            github_token=github_token,
            github_repo=github_repo
        )
    
    def _load_optional_config(self) -> OptionalConfig:
        """
        Load optional configuration from environment and config.json.
        
        Returns:
            OptionalConfig object with defaults for missing values
        """
        optional = OptionalConfig()
        
        # Load from config.json if exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Parse repository structure
                if "repository" in config_data:
                    repo_data = config_data["repository"]
                    optional.repo_structure = RepoStructure(
                        source_directory=repo_data.get("source_dir"),
                        test_directory=repo_data.get("test_dir"),
                        test_file_pattern=repo_data.get("test_pattern")
                    )
                
                # Parse test conventions
                if "test_conventions" in config_data:
                    conv_data = config_data["test_conventions"]
                    optional.test_conventions = TestConventions(
                        naming_pattern=conv_data.get("naming_pattern"),
                        test_prefix=conv_data.get("test_prefix"),
                        test_suffix=conv_data.get("test_suffix"),
                        class_prefix=conv_data.get("class_prefix"),
                        method_prefix=conv_data.get("method_prefix"),
                        fixture_directory=conv_data.get("fixture_directory")
                    )
                
                # Parse coding standards
                if "coding_standards" in config_data:
                    std_data = config_data["coding_standards"]
                    optional.coding_standards = CodingStandards(
                        style_guide=std_data.get("style_guide"),
                        linter_config=std_data.get("linter_config"),
                        max_line_length=std_data.get("max_line_length"),
                        max_complexity=std_data.get("max_complexity"),
                        docstring_required=std_data.get("docstring_required")
                    )
                
                # Parse coverage goals
                if "coverage_goals" in config_data:
                    cov_data = config_data["coverage_goals"]
                    optional.coverage_goals = CoverageGoals(
                        minimum_percent=cov_data.get("minimum_percent"),
                        per_module_minimum=cov_data.get("per_module_minimum"),
                        fail_under=cov_data.get("fail_under"),
                        exclude_patterns=cov_data.get("exclude_patterns", [])
                    )
                
                # Parse exclusions
                if "exclusions" in config_data:
                    excl_data = config_data["exclusions"]
                    optional.exclusions = Exclusions(
                        directories=excl_data.get("directories", []),
                        files=excl_data.get("files", [])
                    )
                
                logger.info("Loaded optional configuration from config.json")
            
            except Exception as e:
                logger.warning(f"Failed to load config.json: {e}. Using defaults.")
        
        # Override with environment variables if present
        if os.getenv("SOURCE_DIRECTORY"):
            if not optional.repo_structure:
                optional.repo_structure = RepoStructure()
            optional.repo_structure.source_directory = os.getenv("SOURCE_DIRECTORY")
        
        if os.getenv("TEST_DIRECTORY"):
            if not optional.repo_structure:
                optional.repo_structure = RepoStructure()
            optional.repo_structure.test_directory = os.getenv("TEST_DIRECTORY")
        
        if os.getenv("MINIMUM_COVERAGE_PERCENT"):
            if not optional.coverage_goals:
                optional.coverage_goals = CoverageGoals()
            optional.coverage_goals.minimum_percent = int(os.getenv("MINIMUM_COVERAGE_PERCENT"))
        
        if os.getenv("EXCLUDE_DIRECTORIES"):
            if not optional.exclusions:
                optional.exclusions = Exclusions()
            optional.exclusions.directories = os.getenv("EXCLUDE_DIRECTORIES").split(',')
        
        return optional
    
    def validate_on_startup(self) -> ValidationResult:
        """
        Validate that configuration exists and is minimally valid.
        
        Returns:
            ValidationResult indicating if config is valid
        """
        try:
            config = self.load()
            return ValidationResult(
                success=True,
                error_message=None
            )
        except ConfigurationError as e:
            return ValidationResult(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            return ValidationResult(
                success=False,
                error_message=f"Unexpected configuration error: {str(e)}"
            )
    
    def get_state(self):
        """
        Get current tool state.
        
        Returns:
            ToolState object
        """
        return self.state_manager.load()
    
    def reload(self):
        """Reload configuration from files."""
        self._config = None
        return self.load()


# Global configuration loader instance
_config_loader = ConfigLoader()


def get_config() -> FullConfiguration:
    """Get the current configuration."""
    return _config_loader.load()


def reload_config() -> FullConfiguration:
    """Reload configuration from files."""
    return _config_loader.reload()

