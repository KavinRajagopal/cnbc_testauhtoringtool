"""Build unified optimization reports in markdown format."""

import logging
from typing import Dict, Any

from app.optimizers.models import OptimizationReport

logger = logging.getLogger(__name__)


class ReportBuilder:
    """
    Generates formatted markdown reports from optimization analysis.
    """
    
    def build_markdown(self, report: OptimizationReport) -> str:
        """
        Build markdown report from optimization results.
        
        Args:
            report: OptimizationReport with all findings
            
        Returns:
            Formatted markdown string
        """
        if not report.has_issues():
            return self._build_clean_report()
        
        parts = []
        
        # Header
        parts.append("## 🔍 Test Case Optimization Report\n")
        parts.append(self._build_summary(report))
        
        # Similar tests section
        if report.similar_pairs:
            parts.append("\n---\n")
            parts.append(self._build_similarity_section(report.similar_pairs))
        
        # AI suggestions section
        if report.optimizations:
            parts.append("\n---\n")
            parts.append(self._build_suggestions_section(report.optimizations))
        
        # Redundancy and outdated section
        if report.redundant_tests or report.outdated_tests:
            parts.append("\n---\n")
            parts.append(self._build_issues_section(
                report.redundant_tests,
                report.outdated_tests
            ))
        
        # Quality score
        parts.append("\n---\n")
        parts.append(self._build_quality_section(report.quality_score))
        
        return "".join(parts)
    
    def _build_clean_report(self) -> str:
        """Build report for tests with no issues."""
        return """## ✅ Test Quality Check Passed

All generated tests look good! No issues detected.

- ✅ No similar tests found
- ✅ No redundancies detected
- ✅ No outdated code identified
- ✅ Code follows best practices

**Quality Score: 10/10** 🎉
"""
    
    def _build_summary(self, report: OptimizationReport) -> str:
        """Build summary section."""
        counts = report.summary_counts()
        
        parts = ["### 📊 Summary\n"]
        
        if counts['similar_tests'] > 0:
            parts.append(f"- ⚠️ **{counts['similar_tests']} similar test(s)** detected (>70% threshold)\n")
        else:
            parts.append("- ✅ No similar tests detected\n")
        
        if counts['optimizations'] > 0:
            parts.append(f"- 💡 **{counts['optimizations']} optimization opportunity(s)** found\n")
        else:
            parts.append("- ✅ No optimization opportunities\n")
        
        if counts['redundant'] > 0:
            parts.append(f"- ⚠️ **{counts['redundant']} redundant test(s)** identified\n")
        
        if counts['outdated'] > 0:
            parts.append(f"- ⚠️ **{counts['outdated']} outdated test(s)** found\n")
        
        return "".join(parts)
    
    def _build_similarity_section(self, similar_pairs) -> str:
        """Build similar tests section."""
        parts = ["### ⚠️ Similar Tests (70%+ similarity)\n\n"]
        
        for i, pair in enumerate(similar_pairs, 1):
            similarity_pct = pair.similarity * 100
            parts.append(f"#### {i}. High Similarity: {similarity_pct:.0f}%\n")
            parts.append(f"**Tests**: `{pair.test1}` ↔️ `{pair.test2}`\n\n")
            parts.append(f"**💡 Recommendation**: {pair.suggestion}\n\n")
            
            if pair.example_code:
                parts.append("**Example:**\n```python\n")
                parts.append(pair.example_code)
                parts.append("\n```\n\n")
        
        return "".join(parts)
    
    def _build_suggestions_section(self, optimizations) -> str:
        """Build optimization suggestions section."""
        parts = ["### 💡 AI-Powered Optimization Suggestions\n\n"]
        
        for i, opt in enumerate(optimizations, 1):
            parts.append(f"#### {i}. {opt.type.title()} Opportunity\n")
            
            if opt.tests:
                tests_str = "`, `".join(opt.tests)
                parts.append(f"**Affected Tests**: `{tests_str}`\n\n")
            
            parts.append(f"**Issue**: {opt.reason}\n\n")
            parts.append(f"**Suggestion**: {opt.suggestion}\n\n")
            
            if opt.code_example:
                parts.append("**Example:**\n```python\n")
                parts.append(opt.code_example)
                parts.append("\n```\n\n")
        
        return "".join(parts)
    
    def _build_issues_section(self, redundant_tests, outdated_tests) -> str:
        """Build redundancy and outdated issues section."""
        parts = ["### ⚠️ Potential Issues\n\n"]
        
        if redundant_tests:
            parts.append("#### Redundant Tests\n\n")
            for test in redundant_tests:
                parts.append(f"- **{test.test}**\n")
                parts.append(f"  - Reason: {test.reason}\n")
                if test.existing_test:
                    parts.append(f"  - Conflicts with: `{test.existing_test}`\n")
                parts.append(f"  - Action: {test.suggestion}\n\n")
        
        if outdated_tests:
            parts.append("#### Outdated References\n\n")
            for test in outdated_tests:
                severity_emoji = "🔴" if test.severity == "high" else "🟡"
                parts.append(f"- **{test.test}** {severity_emoji}\n")
                parts.append(f"  - Issue: {test.issue}\n")
                parts.append(f"  - Fix: {test.fix}\n\n")
        
        return "".join(parts)
    
    def _build_quality_section(self, quality_score: float) -> str:
        """Build quality score section."""
        # Determine rating
        if quality_score >= 9:
            rating = "Excellent"
            emoji = "🎉"
        elif quality_score >= 7:
            rating = "Good"
            emoji = "✅"
        elif quality_score >= 5:
            rating = "Fair"
            emoji = "⚠️"
        else:
            rating = "Needs Improvement"
            emoji = "❌"
        
        return f"""### {emoji} Quality Score: {quality_score:.1f}/10

**Rating**: {rating}

**Breakdown**:
- Tests follow best practices
- Consider addressing suggestions above for optimal quality
"""


