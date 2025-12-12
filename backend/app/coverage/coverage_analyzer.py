"""Main coverage analyzer orchestrator."""

import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from app.coverage.coverage_models import CoverageReport, ModuleCoverage
from app.coverage.python_coverage import PythonCoverageRunner
from app.coverage.javascript_coverage import JavaScriptCoverageRunner
from app.coverage.gap_analyzer import GapAnalyzer

logger = logging.getLogger(__name__)


class CoverageAnalyzer:
    """
    Main coverage analysis orchestrator.
    Coordinates coverage runs, gap analysis, and reporting.
    """
    
    def __init__(self):
        """Initialize coverage analyzer."""
        self.enabled = os.getenv("ENABLE_COVERAGE_ANALYSIS", "false").lower() == "true"
        self.include_gaps = os.getenv("COVERAGE_INCLUDE_GAPS", "true").lower() == "true"
        self.include_recommendations = os.getenv(
            "COVERAGE_INCLUDE_RECOMMENDATIONS",
            "true"
        ).lower() == "true"
        
        logger.info(f"Coverage Analyzer initialized (enabled: {self.enabled})")
    
    def analyze(
        self,
        repo_url: str,
        test_file_path: str,
        framework_config: Dict[str, Any],
        branch_name: str = "main"
    ) -> CoverageReport:
        """
        Main analysis method.
        
        Args:
            repo_url: GitHub repository URL or path
            test_file_path: Path to the generated test file
            framework_config: Test framework configuration
            branch_name: Branch to analyze
            
        Returns:
            CoverageReport with before/after comparison and gaps
        """
        if not self.enabled:
            logger.info("Coverage analysis disabled")
            return self._create_disabled_report(framework_config)
        
        temp_dir = None
        
        try:
            logger.info(f"Starting coverage analysis for {repo_url}")
            
            # Clone repository to temp directory
            temp_dir = self._clone_repository(repo_url, branch_name)
            
            if not temp_dir:
                raise Exception("Failed to clone repository")
            
            # Detect language
            language = self._detect_language(framework_config)
            
            # Get appropriate coverage runner
            runner = self._get_coverage_runner(language, temp_dir)
            
            if not runner:
                raise Exception(f"No coverage runner for language: {language}")
            
            # Check dependencies
            if not runner.check_dependencies():
                logger.warning(f"Coverage dependencies not available for {language}")
                return self._create_error_report(
                    framework_config,
                    "Coverage tool not available. Install pytest-cov or jest."
                )
            
            # Install dependencies
            self._install_dependencies(temp_dir, language)
            
            # Run coverage BEFORE (without new test)
            logger.info("Running coverage analysis - BEFORE")
            before_data = runner.run_coverage(exclude_test=test_file_path)
            
            # Run coverage AFTER (with new test)
            logger.info("Running coverage analysis - AFTER")
            after_data = runner.run_coverage()
            
            # Calculate module-level changes
            modules = self._calculate_module_changes(before_data, after_data)
            
            # Analyze gaps
            gaps = []
            recommendations = []
            
            if self.include_gaps:
                gap_analyzer = GapAnalyzer(temp_dir)
                gaps = gap_analyzer.identify_gaps(after_data)
                
                if self.include_recommendations:
                    recommendations = gap_analyzer.generate_recommendations(gaps)
            
            # Build report
            report = CoverageReport(
                before_coverage=before_data.total_coverage,
                after_coverage=after_data.total_coverage,
                coverage_gain=after_data.total_coverage - before_data.total_coverage,
                modules=modules,
                gaps=gaps,
                recommendations=recommendations,
                tool=self._get_tool_name(language),
                framework=framework_config.get('framework', 'unknown'),
                test_file_path=test_file_path,
                success=True
            )
            
            logger.info(
                f"Coverage analysis complete: "
                f"{report.before_coverage:.1f}% → {report.after_coverage:.1f}% "
                f"({report.coverage_gain:+.1f}%)"
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Coverage analysis failed: {e}", exc_info=True)
            return self._create_error_report(framework_config, str(e))
        
        finally:
            # Cleanup
            if temp_dir:
                self._cleanup(temp_dir)
    
    def _clone_repository(self, repo_url: str, branch: str) -> Optional[str]:
        """Clone repository to temporary directory."""
        try:
            import git
            
            temp_dir = tempfile.mkdtemp(prefix="coverage_")
            logger.info(f"Cloning {repo_url} to {temp_dir}")
            
            # Shallow clone for speed
            git.Repo.clone_from(
                repo_url,
                temp_dir,
                branch=branch,
                depth=1
            )
            
            return temp_dir
            
        except Exception as e:
            logger.error(f"Failed to clone repository: {e}")
            return None
    
    def _detect_language(self, framework_config: Dict[str, Any]) -> str:
        """Detect language from framework config."""
        framework = framework_config.get('framework', '').lower()
        
        if framework in ['pytest', 'unittest']:
            return 'python'
        elif framework in ['jest', 'mocha', 'vitest', 'playwright']:
            return 'javascript'
        else:
            return 'python'  # Default
    
    def _get_coverage_runner(self, language: str, repo_path: str):
        """Get appropriate coverage runner."""
        if language == 'python':
            return PythonCoverageRunner(repo_path)
        elif language == 'javascript':
            return JavaScriptCoverageRunner(repo_path)
        else:
            return None
    
    def _get_tool_name(self, language: str) -> str:
        """Get coverage tool name."""
        if language == 'python':
            return os.getenv("PYTHON_COVERAGE_TOOL", "pytest-cov")
        elif language == 'javascript':
            return os.getenv("JS_COVERAGE_TOOL", "jest/nyc")
        else:
            return "unknown"
    
    def _install_dependencies(self, repo_path: str, language: str):
        """Install project dependencies."""
        try:
            if language == 'python':
                # Try to install requirements
                req_file = Path(repo_path) / "requirements.txt"
                if req_file.exists():
                    logger.info("Installing Python dependencies...")
                    import subprocess
                    subprocess.run(
                        ["pip", "install", "-q", "-r", "requirements.txt"],
                        cwd=repo_path,
                        timeout=120,
                        capture_output=True
                    )
            
            elif language == 'javascript':
                # Try to install npm packages
                package_json = Path(repo_path) / "package.json"
                if package_json.exists():
                    logger.info("Installing JavaScript dependencies...")
                    import subprocess
                    subprocess.run(
                        ["npm", "install", "--silent"],
                        cwd=repo_path,
                        timeout=180,
                        capture_output=True
                    )
        
        except Exception as e:
            logger.warning(f"Failed to install dependencies: {e}")
    
    def _calculate_module_changes(self, before_data, after_data) -> list:
        """Calculate per-module coverage changes."""
        modules = []
        
        # Get all file paths
        all_files = set(before_data.files.keys()) | set(after_data.files.keys())
        
        for file_path in all_files:
            before_cov = self._get_file_coverage(before_data.files.get(file_path, {}))
            after_cov = self._get_file_coverage(after_data.files.get(file_path, {}))
            
            module = ModuleCoverage(
                file_path=file_path,
                before=before_cov,
                after=after_cov,
                change=after_cov - before_cov
            )
            
            modules.append(module)
        
        return modules
    
    def _get_file_coverage(self, file_data: Dict[str, Any]) -> float:
        """Extract coverage percentage for a file."""
        if not file_data:
            return 0.0
        
        # Python format
        if 'summary' in file_data:
            return file_data['summary'].get('percent_covered', 0.0)
        
        # JavaScript format
        if 's' in file_data:
            statements = file_data['s']
            if not statements:
                return 0.0
            covered = sum(1 for v in statements.values() if v > 0)
            return (covered / len(statements)) * 100
        
        return 0.0
    
    def _cleanup(self, temp_dir: str):
        """Clean up temporary directory."""
        try:
            if temp_dir and Path(temp_dir).exists():
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {temp_dir}: {e}")
    
    def _create_disabled_report(self, framework_config: Dict[str, Any]) -> CoverageReport:
        """Create report for disabled coverage."""
        return CoverageReport(
            before_coverage=0.0,
            after_coverage=0.0,
            coverage_gain=0.0,
            tool="disabled",
            framework=framework_config.get('framework', 'unknown'),
            success=False,
            error_message="Coverage analysis is disabled"
        )
    
    def _create_error_report(
        self,
        framework_config: Dict[str, Any],
        error_message: str
    ) -> CoverageReport:
        """Create report for failed coverage run."""
        return CoverageReport(
            before_coverage=0.0,
            after_coverage=0.0,
            coverage_gain=0.0,
            tool=framework_config.get('framework', 'unknown'),
            framework=framework_config.get('framework', 'unknown'),
            success=False,
            error_message=error_message
        )


