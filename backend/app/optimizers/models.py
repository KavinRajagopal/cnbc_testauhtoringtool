"""Data models for test optimization."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TestCase(BaseModel):
    """Represents a single test case."""
    name: str
    code: str
    line_start: int
    line_end: int
    docstring: Optional[str] = None


class SimilarTestPair(BaseModel):
    """Pair of similar tests."""
    test1: str
    test2: str
    similarity: float
    suggestion: str
    example_code: Optional[str] = None


class OptimizationSuggestion(BaseModel):
    """AI-powered optimization suggestion."""
    type: str  # parameterization, fixture, assertion, etc.
    tests: List[str]
    reason: str
    suggestion: str
    code_example: Optional[str] = None


class RedundantTest(BaseModel):
    """Test identified as redundant."""
    test: str
    reason: str
    existing_test: Optional[str] = None
    suggestion: str


class OutdatedTest(BaseModel):
    """Test identified as outdated."""
    test: str
    issue: str
    fix: str
    severity: str  # low, medium, high


class OptimizationReport(BaseModel):
    """Complete optimization analysis report."""
    similar_pairs: List[SimilarTestPair] = Field(default_factory=list)
    optimizations: List[OptimizationSuggestion] = Field(default_factory=list)
    redundant_tests: List[RedundantTest] = Field(default_factory=list)
    outdated_tests: List[OutdatedTest] = Field(default_factory=list)
    quality_score: float = 10.0
    
    def to_markdown(self) -> str:
        """Convert report to markdown format."""
        from app.optimizers.report_builder import ReportBuilder
        builder = ReportBuilder()
        return builder.build_markdown(self)
    
    def has_issues(self) -> bool:
        """Check if report has any issues."""
        return bool(
            self.similar_pairs or 
            self.optimizations or 
            self.redundant_tests or 
            self.outdated_tests
        )
    
    def summary_counts(self) -> Dict[str, int]:
        """Get summary counts of findings."""
        return {
            "similar_tests": len(self.similar_pairs),
            "optimizations": len(self.optimizations),
            "redundant": len(self.redundant_tests),
            "outdated": len(self.outdated_tests)
        }


