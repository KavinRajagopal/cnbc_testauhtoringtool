"""Analyze coverage gaps and identify uncovered code sections."""

import logging
import ast
from typing import List, Dict, Any
from pathlib import Path

from app.coverage.coverage_models import CoverageGap, CoverageData

logger = logging.getLogger(__name__)


class GapAnalyzer:
    """Identify uncovered code sections and provide recommendations."""
    
    def __init__(self, repo_path: str):
        """
        Initialize gap analyzer.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
    
    def identify_gaps(
        self,
        coverage_data: CoverageData,
        max_gaps: int = 10
    ) -> List[CoverageGap]:
        """
        Find uncovered lines, functions, and branches.
        
        Args:
            coverage_data: Coverage data from runner
            max_gaps: Maximum number of gaps to return
            
        Returns:
            List of CoverageGap objects
        """
        gaps = []
        
        try:
            for file_path, file_data in coverage_data.files.items():
                file_gaps = self._analyze_file(file_path, file_data)
                gaps.extend(file_gaps)
            
            # Sort by importance (complexity, line count)
            gaps.sort(key=lambda g: g.complexity, reverse=True)
            
            # Limit to max_gaps
            return gaps[:max_gaps]
            
        except Exception as e:
            logger.error(f"Gap analysis failed: {e}", exc_info=True)
            return []
    
    def _analyze_file(self, file_path: str, file_data: Dict[str, Any]) -> List[CoverageGap]:
        """Analyze a single file for coverage gaps."""
        gaps = []
        
        try:
            # Extract uncovered lines
            uncovered_lines = self._get_uncovered_lines(file_data)
            
            if not uncovered_lines:
                return gaps
            
            # Read file content
            full_path = self._resolve_file_path(file_path)
            if not full_path or not full_path.exists():
                return gaps
            
            with open(full_path, 'r') as f:
                code = f.read()
            
            # Parse AST to find function names
            try:
                tree = ast.parse(code)
                function_map = self._build_function_map(tree)
            except:
                function_map = {}
            
            # Group uncovered lines into ranges
            line_ranges = self._group_line_ranges(uncovered_lines)
            
            # Create gap objects
            for start, end in line_ranges:
                function_name = self._find_function_at_line(start, function_map)
                complexity = end - start + 1  # Simple complexity = line count
                
                gap = CoverageGap(
                    file_path=file_path,
                    line_start=start,
                    line_end=end,
                    function_name=function_name,
                    complexity=complexity,
                    reason=self._generate_reason(function_name, complexity)
                )
                gaps.append(gap)
            
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")
        
        return gaps
    
    def _get_uncovered_lines(self, file_data: Dict[str, Any]) -> List[int]:
        """Extract uncovered line numbers from coverage data."""
        uncovered = []
        
        # Python coverage format
        if 'missing_lines' in file_data:
            uncovered = file_data['missing_lines']
        
        # JavaScript coverage format (statements)
        elif 's' in file_data:
            statements = file_data['s']
            uncovered = [int(k) for k, v in statements.items() if v == 0]
        
        # Alternative format
        elif 'lines' in file_data:
            lines = file_data['lines']
            uncovered = [int(k) for k, v in lines.items() if v == 0]
        
        return sorted(uncovered)
    
    def _resolve_file_path(self, file_path: str) -> Path:
        """Resolve file path relative to repo."""
        # Handle absolute paths
        path = Path(file_path)
        if path.is_absolute():
            return path
        
        # Try relative to repo
        full_path = self.repo_path / file_path
        if full_path.exists():
            return full_path
        
        # Try without leading directories
        for parent_count in range(3):
            parts = path.parts[parent_count:]
            if parts:
                test_path = self.repo_path / Path(*parts)
                if test_path.exists():
                    return test_path
        
        return None
    
    def _build_function_map(self, tree: ast.AST) -> Dict[int, str]:
        """Build map of line numbers to function names."""
        function_map = {}
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Map all lines in function to function name
                start = node.lineno
                end = node.end_lineno or start
                for line in range(start, end + 1):
                    function_map[line] = node.name
        
        return function_map
    
    def _group_line_ranges(self, lines: List[int], max_gap: int = 3) -> List[tuple]:
        """Group consecutive lines into ranges."""
        if not lines:
            return []
        
        ranges = []
        start = lines[0]
        prev = lines[0]
        
        for line in lines[1:]:
            if line - prev > max_gap:
                # Start new range
                ranges.append((start, prev))
                start = line
            prev = line
        
        # Add last range
        ranges.append((start, prev))
        
        return ranges
    
    def _find_function_at_line(self, line: int, function_map: Dict[int, str]) -> str:
        """Find function name at given line."""
        return function_map.get(line)
    
    def _generate_reason(self, function_name: str, complexity: int) -> str:
        """Generate reason why gap matters."""
        if function_name:
            if complexity > 10:
                return f"Large uncovered function: {function_name}"
            else:
                return f"Uncovered function: {function_name}"
        else:
            if complexity > 10:
                return "Large uncovered code block"
            else:
                return "Uncovered code section"
    
    def generate_recommendations(self, gaps: List[CoverageGap]) -> List[str]:
        """Generate recommendations based on gaps."""
        recommendations = []
        
        # Group gaps by file
        by_file = {}
        for gap in gaps:
            if gap.file_path not in by_file:
                by_file[gap.file_path] = []
            by_file[gap.file_path].append(gap)
        
        # Generate recommendations per file
        for file_path, file_gaps in list(by_file.items())[:5]:  # Top 5 files
            func_names = [g.function_name for g in file_gaps if g.function_name]
            
            if func_names:
                func_list = ", ".join(f"`{f}()`" for f in func_names[:3])
                recommendations.append(
                    f"Add tests for {func_list} in `{file_path}`"
                )
            else:
                line_ranges = [(g.line_start, g.line_end) for g in file_gaps[:2]]
                range_str = ", ".join(f"lines {s}-{e}" for s, e in line_ranges)
                recommendations.append(
                    f"Cover {range_str} in `{file_path}`"
                )
        
        return recommendations


