"""Python coverage runner using pytest-cov."""

import logging
import os
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from app.coverage.coverage_models import CoverageData

logger = logging.getLogger(__name__)


class PythonCoverageRunner:
    """Run coverage.py for Python projects."""
    
    def __init__(self, repo_path: str):
        """
        Initialize Python coverage runner.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        self.timeout = int(os.getenv("COVERAGE_TIMEOUT", "300"))
    
    def run_coverage(
        self,
        test_path: Optional[str] = None,
        exclude_test: Optional[str] = None
    ) -> CoverageData:
        """
        Run pytest with coverage.
        
        Args:
            test_path: Specific test file to run (None = all tests)
            exclude_test: Test file to exclude from run
            
        Returns:
            CoverageData with coverage results
        """
        try:
            logger.info(f"Running Python coverage in {self.repo_path}")
            
            # Find source directory
            src_dir = self._find_source_directory()
            
            # Build pytest command
            cmd = self._build_coverage_command(src_dir, test_path, exclude_test)
            
            logger.info(f"Coverage command: {' '.join(cmd)}")
            
            # Run coverage
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Parse coverage results
            coverage_data = self._parse_coverage_results()
            
            logger.info(
                f"Python coverage complete: {coverage_data.total_coverage:.1f}%"
            )
            
            return coverage_data
            
        except subprocess.TimeoutExpired:
            logger.error(f"Coverage run timed out after {self.timeout}s")
            return CoverageData(total_coverage=0.0)
        except Exception as e:
            logger.error(f"Python coverage run failed: {e}", exc_info=True)
            return CoverageData(total_coverage=0.0)
    
    def _find_source_directory(self) -> str:
        """Find the main source directory."""
        # Common Python source directories
        candidates = ["src", "app", self.repo_path.name.replace("-", "_")]
        
        for candidate in candidates:
            if (self.repo_path / candidate).exists():
                return candidate
        
        # Default to current directory
        return "."
    
    def _build_coverage_command(
        self,
        src_dir: str,
        test_path: Optional[str],
        exclude_test: Optional[str]
    ) -> list:
        """Build pytest coverage command."""
        cmd = [
            "python", "-m", "pytest",
            f"--cov={src_dir}",
            "--cov-report=json",
            "--cov-report=term",
            "-v"
        ]
        
        if test_path:
            cmd.append(test_path)
        
        if exclude_test:
            cmd.extend(["--ignore", exclude_test])
        
        return cmd
    
    def _parse_coverage_results(self) -> CoverageData:
        """Parse coverage.json file."""
        coverage_file = self.repo_path / "coverage.json"
        
        if not coverage_file.exists():
            logger.warning("coverage.json not found")
            return CoverageData(total_coverage=0.0)
        
        try:
            with open(coverage_file, 'r') as f:
                data = json.load(f)
            
            total_coverage = data.get('totals', {}).get('percent_covered', 0.0)
            
            return CoverageData(
                total_coverage=total_coverage,
                files=data.get('files', {}),
                summary=data.get('totals', {})
            )
            
        except Exception as e:
            logger.error(f"Failed to parse coverage.json: {e}")
            return CoverageData(total_coverage=0.0)
    
    def check_dependencies(self) -> bool:
        """Check if pytest and pytest-cov are available."""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--version"],
                cwd=self.repo_path,
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False


