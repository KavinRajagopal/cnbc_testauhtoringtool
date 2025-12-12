"""Build markdown coverage reports for GitHub."""

import logging
from datetime import datetime
from app.coverage.coverage_models import CoverageReport

logger = logging.getLogger(__name__)


class CoverageReportBuilder:
    """Generate formatted markdown reports from coverage data."""
    
    def build_issue_comment(self, report: CoverageReport) -> str:
        """
        Build markdown report for GitHub issue comment.
        
        Args:
            report: CoverageReport object
            
        Returns:
            Formatted markdown string
        """
        if not report.success:
            return self._build_error_report(report)
        
        parts = []
        
        # Header
        parts.append("## 📊 Test Coverage Report\n")
        
        # Summary
        parts.append(self._build_summary(report))
        
        # Module breakdown
        if report.modules:
            parts.append("\n---\n")
            parts.append(self._build_module_table(report))
        
        # New test coverage
        if report.test_file_path:
            parts.append("\n---\n")
            parts.append(self._build_test_coverage_section(report))
        
        # Gaps
        if report.gaps:
            parts.append("\n---\n")
            parts.append(self._build_gaps_section(report))
        
        # Recommendations
        if report.recommendations:
            parts.append("\n---\n")
            parts.append(self._build_recommendations_section(report))
        
        # Footer
        parts.append(self._build_footer(report))
        
        return "".join(parts)
    
    def _build_error_report(self, report: CoverageReport) -> str:
        """Build report for failed coverage run."""
        return f"""## ⚠️ Coverage Analysis Failed

Could not run coverage analysis for this test generation.

**Error**: {report.error_message or 'Unknown error'}

**Note**: Test generation was successful. The coverage analysis is supplementary and this error does not affect the generated tests.

---
*Coverage tool: {report.tool}*
"""
    
    def _build_summary(self, report: CoverageReport) -> str:
        """Build summary section."""
        before = report.before_coverage
        after = report.after_coverage
        gain = report.coverage_gain
        
        # Choose emoji based on gain
        if gain > 20:
            emoji = "🎉🎉🎉"
            message = "Excellent improvement! These tests significantly increased coverage."
        elif gain > 10:
            emoji = "🎉"
            message = "Great work! Notable coverage improvement."
        elif gain > 5:
            emoji = "✅"
            message = "Good! Tests added meaningful coverage."
        elif gain > 0:
            emoji = ""
            message = "Tests added some coverage."
        elif gain == 0:
            emoji = ""
            message = "Coverage unchanged."
        else:
            emoji = "⚠️"
            message = "Warning: Coverage decreased. Please review test execution."
        
        summary = f"""### Summary
- **Before**: {before:.1f}% coverage
- **After**: {after:.1f}% coverage  
- **Change**: {gain:+.1f}% {emoji}

"""
        
        if message:
            summary += f"{message}\n"
        
        return summary
    
    def _build_module_table(self, report: CoverageReport) -> str:
        """Build module coverage table."""
        parts = ["### Coverage by Module\n\n"]
        parts.append("| Module | Before | After | Change |\n")
        parts.append("|--------|--------|-------|--------|\n")
        
        # Sort by change (biggest improvements first)
        sorted_modules = sorted(
            report.modules,
            key=lambda m: m.change,
            reverse=True
        )
        
        for module in sorted_modules[:10]:  # Top 10 modules
            before = module.before
            after = module.after
            change = module.change
            
            # Format change
            if change > 0:
                change_str = f"+{change:.0f}% ✅"
            elif change < 0:
                change_str = f"{change:.0f}% ⚠️"
            else:
                change_str = "-"
            
            # Shorten file path
            file_path = module.file_path
            if len(file_path) > 50:
                file_path = "..." + file_path[-47:]
            
            parts.append(
                f"| `{file_path}` | {before:.0f}% | {after:.0f}% | {change_str} |\n"
            )
        
        return "".join(parts)
    
    def _build_test_coverage_section(self, report: CoverageReport) -> str:
        """Build new test coverage section."""
        parts = ["### New Test Coverage\n\n"]
        parts.append(f"**Generated test file**: `{report.test_file_path}`\n\n")
        
        if report.modules:
            parts.append("Functions/modules affected by new tests:\n")
            
            # Show modules with improvements
            improved = [m for m in report.modules if m.change > 0]
            
            if improved:
                for module in improved[:5]:
                    parts.append(f"- ✅ `{module.file_path}` - {module.after:.0f}% coverage\n")
            else:
                parts.append("- ℹ️ No significant coverage changes detected\n")
        
        return "".join(parts)
    
    def _build_gaps_section(self, report: CoverageReport) -> str:
        """Build uncovered code gaps section."""
        parts = ["### Uncovered Code Sections\n\n"]
        
        # Group by file
        by_file = {}
        for gap in report.gaps:
            if gap.file_path not in by_file:
                by_file[gap.file_path] = []
            by_file[gap.file_path].append(gap)
        
        for file_path, gaps in list(by_file.items())[:5]:  # Top 5 files
            parts.append(f"#### `{file_path}`\n")
            
            for gap in gaps[:3]:  # Top 3 gaps per file
                if gap.line_start == gap.line_end:
                    line_str = f"Line {gap.line_start}"
                else:
                    line_str = f"Lines {gap.line_start}-{gap.line_end}"
                
                parts.append(f"- **{line_str}**: ")
                
                if gap.function_name:
                    parts.append(f"Function `{gap.function_name}()` - {gap.reason}\n")
                else:
                    parts.append(f"{gap.reason}\n")
            
            parts.append("\n")
        
        return "".join(parts)
    
    def _build_recommendations_section(self, report: CoverageReport) -> str:
        """Build recommendations section."""
        parts = ["### Recommendations\n\n"]
        parts.append("Consider adding tests for:\n")
        
        for i, rec in enumerate(report.recommendations, 1):
            parts.append(f"{i}. {rec}\n")
        
        return "".join(parts)
    
    def _build_footer(self, report: CoverageReport) -> str:
        """Build report footer."""
        timestamp = report.timestamp.strftime("%Y-%m-%d %H:%M UTC")
        
        return f"""
---

**Coverage Tool**: {report.tool}  
**Test Framework**: {report.framework}  
**Generated**: {timestamp}
"""


