"""Repository compatibility checker."""

import logging
from pathlib import Path
from typing import List

from .models import CompatibilityReport

logger = logging.getLogger(__name__)


class CompatibilityChecker:
    """
    Check if a repository is compatible with the test authoring tool.
    
    Checks for supported languages, frameworks, and potential issues.
    """
    
    SUPPORTED_LANGUAGES = ["Python", "JavaScript", "TypeScript"]
    SUPPORTED_FRAMEWORKS = ["pytest", "unittest", "jest", "playwright", "mocha", "vitest"]
    
    def __init__(self):
        """Initialize compatibility checker."""
        pass
    
    def check(self, repo_path: Path, framework: str, language: str) -> CompatibilityReport:
        """
        Check repository compatibility.
        
        Args:
            repo_path: Path to repository
            framework: Detected test framework
            language: Detected programming language
            
        Returns:
            CompatibilityReport with compatibility status and any warnings
        """
        warnings = []
        errors = []
        recommendations = []
        
        # Check language
        if language not in self.SUPPORTED_LANGUAGES:
            errors.append(f"Language '{language}' is not supported")
            errors.append(f"Supported languages: {', '.join(self.SUPPORTED_LANGUAGES)}")
        
        # Check framework
        if framework not in self.SUPPORTED_FRAMEWORKS:
            warnings.append(f"Framework '{framework}' has limited support")
            warnings.append(f"Fully supported frameworks: {', '.join(self.SUPPORTED_FRAMEWORKS)}")
        
        # Check repository size
        try:
            total_size = sum(f.stat().st_size for f in repo_path.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            
            if size_mb > 500:
                warnings.append(f"Large repository ({size_mb:.1f}MB) may take longer to analyze")
            elif size_mb > 1000:
                errors.append(f"Repository too large ({size_mb:.1f}MB). Consider analyzing specific directories.")
        except Exception as e:
            logger.warning(f"Failed to calculate repository size: {e}")
        
        # Check for test directory
        test_dirs = ['tests', 'test', '__tests__', 'e2e']
        has_test_dir = any((repo_path / d).exists() for d in test_dirs)
        
        if not has_test_dir:
            warnings.append("No test directory found. Tool will create one.")
            recommendations.append("Create a 'tests' or 'test' directory for better organization")
        
        # Determine compatibility
        compatible = len(errors) == 0
        
        return CompatibilityReport(
            compatible=compatible,
            language=language,
            framework=framework,
            warnings=warnings,
            errors=errors,
            recommendations=recommendations
        )
    
    def get_compatibility_summary(self, report: CompatibilityReport) -> str:
        """
        Get human-readable compatibility summary.
        
        Args:
            report: CompatibilityReport object
            
        Returns:
            Formatted summary string
        """
        lines = []
        lines.append("Repository Compatibility Check:")
        lines.append("")
        
        if report.compatible:
            lines.append("✓ Repository is compatible!")
        else:
            lines.append("✗ Repository has compatibility issues")
        
        lines.append("")
        
        if report.language:
            symbol = "✓" if report.language in self.SUPPORTED_LANGUAGES else "✗"
            lines.append(f"{symbol} Language: {report.language}")
        
        if report.framework:
            symbol = "✓" if report.framework in self.SUPPORTED_FRAMEWORKS else "⚠"
            lines.append(f"{symbol} Framework: {report.framework}")
        
        if report.errors:
            lines.append("")
            lines.append("Errors:")
            for error in report.errors:
                lines.append(f"  ✗ {error}")
        
        if report.warnings:
            lines.append("")
            lines.append("Warnings:")
            for warning in report.warnings:
                lines.append(f"  ⚠ {warning}")
        
        if report.recommendations:
            lines.append("")
            lines.append("Recommendations:")
            for rec in report.recommendations:
                lines.append(f"  • {rec}")
        
        return "\n".join(lines)

