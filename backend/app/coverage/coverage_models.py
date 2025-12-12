"""Data models for test coverage analysis."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ModuleCoverage(BaseModel):
    """Coverage for a single module/file."""
    file_path: str
    before: float
    after: float
    change: float
    
    covered_lines: List[int] = Field(default_factory=list)
    uncovered_lines: List[int] = Field(default_factory=list)
    total_lines: int = 0


class CoverageGap(BaseModel):
    """Uncovered code section."""
    file_path: str
    line_start: int
    line_end: int
    function_name: Optional[str] = None
    complexity: int = 0  # Cyclomatic complexity
    reason: str = ""  # Why it matters


class CoverageReport(BaseModel):
    """Complete coverage analysis report."""
    before_coverage: float
    after_coverage: float
    coverage_gain: float
    
    modules: List[ModuleCoverage] = Field(default_factory=list)
    gaps: List[CoverageGap] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    tool: str  # pytest-cov, nyc, etc.
    framework: str  # pytest, jest, etc.
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    test_file_path: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    
    def to_markdown(self) -> str:
        """Convert report to markdown format."""
        from app.coverage.report_builder import CoverageReportBuilder
        builder = CoverageReportBuilder()
        return builder.build_issue_comment(self)
    
    def has_improvement(self) -> bool:
        """Check if coverage improved."""
        return self.coverage_gain > 0


class CoverageData(BaseModel):
    """Raw coverage data from tools."""
    total_coverage: float
    files: Dict[str, Any] = Field(default_factory=dict)
    summary: Dict[str, Any] = Field(default_factory=dict)


