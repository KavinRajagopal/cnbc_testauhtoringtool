"""Test framework detection for repositories."""

import logging
import re
from typing import Optional, Dict, Any
from app.github.client import GitHubClient

logger = logging.getLogger(__name__)


class TestFrameworkDetector:
    """Detect test framework used in a repository."""
    
    # Framework signatures: files to check and patterns to look for
    FRAMEWORK_SIGNATURES = {
        "pytest": {
            "files": ["pytest.ini", "pyproject.toml", "setup.cfg", "conftest.py", "requirements.txt"],
            "patterns": [r"pytest", r"^import pytest", r"^from pytest"],
            "test_patterns": ["test_*.py", "*_test.py"],
            "test_dirs": ["tests", "test"],
            "template": "pytest"
        },
        "unittest": {
            "files": ["tests/__init__.py", "test/__init__.py"],
            "patterns": [r"import unittest", r"from unittest"],
            "test_patterns": ["test_*.py", "*_test.py"],
            "test_dirs": ["tests", "test"],
            "template": "unittest"
        },
        "jest": {
            "files": ["jest.config.js", "jest.config.ts", "package.json"],
            "patterns": [r'"jest"', r"jest\.config", r"@jest/globals"],
            "test_patterns": ["*.test.js", "*.test.ts", "*.spec.js", "*.spec.ts"],
            "test_dirs": ["__tests__", "tests", "test"],
            "template": "jest"
        },
        "playwright": {
            "files": ["playwright.config.ts", "playwright.config.js"],
            "patterns": [r"@playwright/test", r"playwright\.config"],
            "test_patterns": ["*.spec.ts", "*.spec.js", "*.test.ts"],
            "test_dirs": ["tests", "e2e", "test"],
            "template": "playwright"
        },
        "mocha": {
            "files": ["mocha.opts", ".mocharc.json", "package.json"],
            "patterns": [r'"mocha"', r"require\(['\"]mocha['\"]\)"],
            "test_patterns": ["*.test.js", "*.spec.js"],
            "test_dirs": ["test", "tests"],
            "template": "mocha"
        },
        "vitest": {
            "files": ["vitest.config.ts", "vitest.config.js", "package.json"],
            "patterns": [r'"vitest"', r"vitest\.config"],
            "test_patterns": ["*.test.ts", "*.spec.ts"],
            "test_dirs": ["tests", "test"],
            "template": "vitest"
        }
    }
    
    def __init__(self, github_client: GitHubClient):
        """
        Initialize detector.
        
        Args:
            github_client: Initialized GitHub client.
        """
        self.client = github_client
    
    def _check_file_exists(self, file_path: str) -> bool:
        """Check if a file exists in the repository."""
        content = self.client.get_file_content(file_path)
        return content is not None
    
    def _check_patterns_in_file(self, file_path: str, patterns: list) -> bool:
        """Check if any pattern matches in a file."""
        content = self.client.get_file_content(file_path)
        if not content:
            return False
        
        for pattern in patterns:
            if re.search(pattern, content, re.MULTILINE):
                return True
        
        return False
    
    def _detect_framework(self) -> Optional[str]:
        """
        Detect which test framework is used.
        
        Returns:
            Framework name or None if not detected.
        """
        scores = {framework: 0 for framework in self.FRAMEWORK_SIGNATURES}
        
        for framework, signature in self.FRAMEWORK_SIGNATURES.items():
            # Check for signature files
            for file_path in signature["files"]:
                if self._check_file_exists(file_path):
                    scores[framework] += 2
                    logger.info(f"Found {framework} signature file: {file_path}")
                    
                    # Check patterns in the file
                    if self._check_patterns_in_file(file_path, signature["patterns"]):
                        scores[framework] += 3
                        logger.info(f"Found {framework} pattern in {file_path}")
            
            # Check test directories
            for test_dir in signature["test_dirs"]:
                if self._check_file_exists(test_dir):
                    scores[framework] += 1
        
        # Return framework with highest score
        if max(scores.values()) > 0:
            detected = max(scores, key=scores.get)
            logger.info(f"Detected test framework: {detected} (score: {scores[detected]})")
            return detected
        
        logger.warning("No test framework detected")
        return None
    
    def _get_test_directory(self, framework: str) -> str:
        """
        Determine the test directory for the framework.
        
        Args:
            framework: Framework name.
            
        Returns:
            Test directory path.
        """
        if framework not in self.FRAMEWORK_SIGNATURES:
            return "tests"
        
        # Check which test directory exists
        for test_dir in self.FRAMEWORK_SIGNATURES[framework]["test_dirs"]:
            if self._check_file_exists(test_dir):
                return test_dir
        
        # Default to first option
        return self.FRAMEWORK_SIGNATURES[framework]["test_dirs"][0]
    
    def _get_test_file_pattern(self, framework: str) -> str:
        """
        Get the test file naming pattern.
        
        Args:
            framework: Framework name.
            
        Returns:
            Test file pattern (e.g., "test_*.py").
        """
        if framework not in self.FRAMEWORK_SIGNATURES:
            return "test_*.py"
        
        patterns = self.FRAMEWORK_SIGNATURES[framework]["test_patterns"]
        return patterns[0]  # Return first/primary pattern
    
    def detect(self) -> Dict[str, Any]:
        """
        Detect test framework and return configuration.
        
        Returns:
            Dictionary with framework info:
            {
                "framework": "pytest",
                "test_dir": "tests",
                "test_pattern": "test_*.py",
                "template": "pytest"
            }
        """
        framework = self._detect_framework()
        
        if not framework:
            # Default to pytest for Python or jest for JavaScript
            # Check if there's a package.json (JavaScript project)
            if self._check_file_exists("package.json"):
                framework = "jest"
                logger.info("Defaulting to jest for JavaScript project")
            else:
                framework = "pytest"
                logger.info("Defaulting to pytest for Python project")
        
        test_dir = self._get_test_directory(framework)
        test_pattern = self._get_test_file_pattern(framework)
        
        config = {
            "framework": framework,
            "test_dir": test_dir,
            "test_pattern": test_pattern,
            "template": self.FRAMEWORK_SIGNATURES[framework]["template"]
        }
        
        logger.info(f"Test framework configuration: {config}")
        return config


