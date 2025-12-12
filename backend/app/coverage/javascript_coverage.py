"""JavaScript coverage runner using nyc/jest."""

import logging
import os
import json
import subprocess
from pathlib import Path
from typing import Optional

from app.coverage.coverage_models import CoverageData

logger = logging.getLogger(__name__)


class JavaScriptCoverageRunner:
    """Run nyc/jest coverage for JavaScript projects."""
    
    def __init__(self, repo_path: str):
        """
        Initialize JavaScript coverage runner.
        
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
        Run jest/mocha with coverage.
        
        Args:
            test_path: Specific test file to run (None = all tests)
            exclude_test: Test file to exclude from run
            
        Returns:
            CoverageData with coverage results
        """
        try:
            logger.info(f"Running JavaScript coverage in {self.repo_path}")
            
            # Detect test runner (jest, mocha, vitest)
            test_runner = self._detect_test_runner()
            
            # Build coverage command
            cmd = self._build_coverage_command(test_runner, test_path, exclude_test)
            
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
                f"JavaScript coverage complete: {coverage_data.total_coverage:.1f}%"
            )
            
            return coverage_data
            
        except subprocess.TimeoutExpired:
            logger.error(f"Coverage run timed out after {self.timeout}s")
            return CoverageData(total_coverage=0.0)
        except Exception as e:
            logger.error(f"JavaScript coverage run failed: {e}", exc_info=True)
            return CoverageData(total_coverage=0.0)
    
    def _detect_test_runner(self) -> str:
        """Detect which test runner is used."""
        package_json = self.repo_path / "package.json"
        
        if not package_json.exists():
            return "jest"  # Default
        
        try:
            with open(package_json, 'r') as f:
                data = json.load(f)
            
            scripts = data.get('scripts', {})
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            
            # Check for jest
            if 'jest' in deps or any('jest' in s for s in scripts.values()):
                return "jest"
            
            # Check for vitest
            if 'vitest' in deps:
                return "vitest"
            
            # Check for mocha
            if 'mocha' in deps:
                return "mocha"
            
            return "jest"  # Default
            
        except Exception as e:
            logger.warning(f"Failed to detect test runner: {e}")
            return "jest"
    
    def _build_coverage_command(
        self,
        test_runner: str,
        test_path: Optional[str],
        exclude_test: Optional[str]
    ) -> list:
        """Build coverage command based on test runner."""
        if test_runner == "jest":
            cmd = [
                "npx", "jest",
                "--coverage",
                "--coverageReporters=json",
                "--coverageReporters=text"
            ]
            
            if test_path:
                cmd.append(test_path)
            
            if exclude_test:
                cmd.extend(["--testPathIgnorePatterns", exclude_test])
        
        elif test_runner == "vitest":
            cmd = [
                "npx", "vitest", "run",
                "--coverage",
                "--reporter=json"
            ]
        
        elif test_runner == "mocha":
            cmd = [
                "npx", "nyc",
                "--reporter=json",
                "--reporter=text",
                "mocha"
            ]
            
            if test_path:
                cmd.append(test_path)
        
        else:
            # Generic npm test
            cmd = ["npm", "test", "--", "--coverage"]
        
        return cmd
    
    def _parse_coverage_results(self) -> CoverageData:
        """Parse coverage/coverage-final.json file."""
        coverage_file = self.repo_path / "coverage" / "coverage-final.json"
        
        if not coverage_file.exists():
            # Try alternative locations
            alt_file = self.repo_path / "coverage.json"
            if alt_file.exists():
                coverage_file = alt_file
            else:
                logger.warning("Coverage JSON not found")
                return CoverageData(total_coverage=0.0)
        
        try:
            with open(coverage_file, 'r') as f:
                data = json.load(f)
            
            # Calculate average coverage
            total_coverage = self._calculate_total_coverage(data)
            
            return CoverageData(
                total_coverage=total_coverage,
                files=data,
                summary={"percent_covered": total_coverage}
            )
            
        except Exception as e:
            logger.error(f"Failed to parse coverage JSON: {e}")
            return CoverageData(total_coverage=0.0)
    
    def _calculate_total_coverage(self, data: dict) -> float:
        """Calculate total coverage from Jest/nyc format."""
        if not data:
            return 0.0
        
        total_lines = 0
        covered_lines = 0
        
        for file_path, file_data in data.items():
            if isinstance(file_data, dict):
                # Jest format
                statements = file_data.get('s', {})
                total_lines += len(statements)
                covered_lines += sum(1 for v in statements.values() if v > 0)
        
        if total_lines == 0:
            return 0.0
        
        return (covered_lines / total_lines) * 100
    
    def check_dependencies(self) -> bool:
        """Check if npm and test runner are available."""
        try:
            result = subprocess.run(
                ["npm", "--version"],
                cwd=self.repo_path,
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False


