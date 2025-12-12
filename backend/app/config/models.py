"""Configuration models for the GitHub Test Authoring Tool."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """Result of a configuration validation."""
    success: bool
    error_message: Optional[str] = None
    retry_suggestion: Optional[str] = None
    attempts_remaining: int = 3
    api_response: Optional[Dict[str, Any]] = None


class RequiredConfig(BaseModel):
    """Required configuration settings."""
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    github_token: str
    github_repo: str


class TestConventions(BaseModel):
    """Test naming and structure conventions."""
    naming_pattern: Optional[str] = None
    test_prefix: Optional[str] = None
    test_suffix: Optional[str] = None
    class_prefix: Optional[str] = None
    method_prefix: Optional[str] = None
    fixture_directory: Optional[str] = None


class RepoStructure(BaseModel):
    """Repository structure hints."""
    source_directory: Optional[str] = None
    test_directory: Optional[str] = None
    test_file_pattern: Optional[str] = None


class CodingStandards(BaseModel):
    """Coding standards and style guide settings."""
    style_guide: Optional[str] = None
    linter_config: Optional[str] = None
    max_line_length: Optional[int] = None
    max_complexity: Optional[int] = None
    docstring_required: Optional[bool] = None


class CoverageGoals(BaseModel):
    """Coverage goals and thresholds."""
    minimum_percent: Optional[int] = None
    per_module_minimum: Optional[int] = None
    fail_under: Optional[int] = None
    exclude_patterns: Optional[List[str]] = Field(default_factory=list)


class Exclusions(BaseModel):
    """Files and directories to exclude from analysis."""
    directories: Optional[List[str]] = Field(default_factory=list)
    files: Optional[List[str]] = Field(default_factory=list)


class OptionalConfig(BaseModel):
    """Optional configuration settings."""
    test_conventions: Optional[TestConventions] = None
    repo_structure: Optional[RepoStructure] = None
    coding_standards: Optional[CodingStandards] = None
    coverage_goals: Optional[CoverageGoals] = None
    exclusions: Optional[Exclusions] = None


class RepositoryInfo(BaseModel):
    """Information detected from repository analysis."""
    framework: str
    language: str
    test_directory: str
    existing_test_count: int = 0
    detected_at: str
    source_directory: Optional[str] = None
    repo_size_mb: Optional[float] = None


class ConfigurationSummary(BaseModel):
    """Complete configuration summary for display and confirmation."""
    required: RequiredConfig
    optional: OptionalConfig = Field(default_factory=OptionalConfig)
    detected: Optional[RepositoryInfo] = None
    
    def get_masked_openai_key(self) -> str:
        """Get masked OpenAI key for display."""
        key = self.required.openai_api_key
        if len(key) > 10:
            return f"{key[:7]}...{key[-3:]}"
        return "***"
    
    def get_masked_github_token(self) -> str:
        """Get masked GitHub token for display."""
        token = self.required.github_token
        if len(token) > 10:
            return f"{token[:7]}...{token[-3:]}"
        return "***"


class FullConfiguration(BaseModel):
    """Complete configuration loaded from all sources."""
    required: RequiredConfig
    optional: OptionalConfig = Field(default_factory=OptionalConfig)
    repository_info: Optional[RepositoryInfo] = None


class CompatibilityReport(BaseModel):
    """Repository compatibility check report."""
    compatible: bool
    language: Optional[str] = None
    framework: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

