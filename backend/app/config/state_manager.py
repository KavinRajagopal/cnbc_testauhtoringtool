"""State manager for tracking tool configuration and usage."""

import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Path to state file (root of project)
STATE_FILE_PATH = Path(__file__).parent.parent.parent.parent / ".tool_state.json"


class UsageStats(BaseModel):
    """Usage statistics for the tool."""
    tests_generated: int = 0
    coverage_analyses: int = 0
    optimizations_run: int = 0
    last_used: Optional[str] = None


class ConfigurationSnapshot(BaseModel):
    """Snapshot of configuration at a point in time."""
    repo: Optional[str] = None
    framework: Optional[str] = None
    language: Optional[str] = None
    last_validated: Optional[str] = None


class ToolState(BaseModel):
    """Complete tool state."""
    version: str = "1.0.0"
    last_configured: Optional[str] = None
    configuration: Optional[ConfigurationSnapshot] = Field(default_factory=ConfigurationSnapshot)
    usage_stats: UsageStats = Field(default_factory=UsageStats)
    setup_method: Optional[str] = None  # "guided" or "manual"
    onboarding_completed: bool = False


class StateManager:
    """
    Thread-safe state manager for the tool.
    
    This is the tool's "notepad" - tracks configuration and usage
    to provide a stateful experience across runs.
    """
    
    def __init__(self, state_file: Optional[Path] = None):
        """Initialize state manager."""
        self.state_file = state_file or STATE_FILE_PATH
        self._lock = threading.Lock()
        self._state: Optional[ToolState] = None
    
    def load(self) -> ToolState:
        """
        Load state from file.
        
        Returns:
            ToolState object (creates new if file doesn't exist)
        """
        with self._lock:
            try:
                if self.state_file.exists():
                    with open(self.state_file, 'r') as f:
                        data = json.load(f)
                        self._state = ToolState(**data)
                        logger.info(f"Loaded state from {self.state_file}")
                else:
                    logger.info("No state file found, creating new state")
                    self._state = ToolState()
                    self.save(self._state)
            except Exception as e:
                logger.warning(f"Failed to load state: {e}. Creating new state.")
                self._state = ToolState()
                
            return self._state
    
    def save(self, state: ToolState) -> None:
        """
        Save state to file.
        
        Args:
            state: ToolState object to save
        """
        with self._lock:
            try:
                # Ensure parent directory exists
                self.state_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Write state to file
                with open(self.state_file, 'w') as f:
                    json.dump(state.model_dump(), f, indent=2)
                
                self._state = state
                logger.debug(f"Saved state to {self.state_file}")
            except Exception as e:
                logger.error(f"Failed to save state: {e}")
    
    def update_configuration(
        self,
        repo: Optional[str] = None,
        framework: Optional[str] = None,
        language: Optional[str] = None,
        setup_method: Optional[str] = None
    ) -> None:
        """
        Update configuration in state.
        
        Args:
            repo: Repository name
            framework: Test framework
            language: Programming language
            setup_method: How it was set up ("guided" or "manual")
        """
        state = self.load()
        
        if not state.configuration:
            state.configuration = ConfigurationSnapshot()
        
        if repo:
            state.configuration.repo = repo
        if framework:
            state.configuration.framework = framework
        if language:
            state.configuration.language = language
        
        state.configuration.last_validated = datetime.now().isoformat()
        state.last_configured = datetime.now().isoformat()
        
        if setup_method:
            state.setup_method = setup_method
        
        state.onboarding_completed = True
        
        self.save(state)
        logger.info(f"Updated configuration: repo={repo}, framework={framework}")
    
    def update_after_test_generation(self, issue_number: int) -> None:
        """
        Update state after test generation.
        
        Args:
            issue_number: GitHub issue number
        """
        state = self.load()
        state.usage_stats.tests_generated += 1
        state.usage_stats.last_used = datetime.now().isoformat()
        self.save(state)
        logger.debug(f"Updated state after test generation for issue #{issue_number}")
    
    def update_after_coverage(self) -> None:
        """Update state after coverage analysis."""
        state = self.load()
        state.usage_stats.coverage_analyses += 1
        state.usage_stats.last_used = datetime.now().isoformat()
        self.save(state)
        logger.debug("Updated state after coverage analysis")
    
    def update_after_optimization(self) -> None:
        """Update state after test optimization."""
        state = self.load()
        state.usage_stats.optimizations_run += 1
        state.usage_stats.last_used = datetime.now().isoformat()
        self.save(state)
        logger.debug("Updated state after optimization")
    
    def get_last_config(self) -> Optional[ConfigurationSnapshot]:
        """
        Get the last saved configuration.
        
        Returns:
            ConfigurationSnapshot or None
        """
        state = self.load()
        return state.configuration if state.configuration else None
    
    def is_configured(self) -> bool:
        """
        Check if tool has been configured.
        
        Returns:
            True if onboarding completed
        """
        state = self.load()
        return state.onboarding_completed


# Global state manager instance
_state_manager = StateManager()


def load_state() -> ToolState:
    """Load current tool state."""
    return _state_manager.load()


def save_state(state: ToolState) -> None:
    """Save tool state."""
    _state_manager.save(state)


def update_state(operation: str, data: Optional[Dict[str, Any]] = None) -> None:
    """
    Update state after an operation.
    
    Args:
        operation: Operation type ("test_generation", "coverage", "optimization", "configuration")
        data: Additional data for the operation
    """
    if operation == "test_generation":
        issue_number = data.get("issue_number", 0) if data else 0
        _state_manager.update_after_test_generation(issue_number)
    elif operation == "coverage":
        _state_manager.update_after_coverage()
    elif operation == "optimization":
        _state_manager.update_after_optimization()
    elif operation == "configuration":
        if data:
            _state_manager.update_configuration(
                repo=data.get("repo"),
                framework=data.get("framework"),
                language=data.get("language"),
                setup_method=data.get("setup_method")
            )

