"""Main Test Case Optimizer - orchestrates all optimization analyses."""

import logging
import os
import ast
from typing import List, Dict, Any, Optional

from app.optimizers.models import (
    TestCase,
    OptimizationReport
)
from app.optimizers.similarity_analyzer import SimilarityAnalyzer
from app.optimizers.ai_suggestions import AISuggestions
from app.optimizers.redundancy_detector import RedundancyDetector

logger = logging.getLogger(__name__)


class TestCaseOptimizer:
    """
    Unified test case optimization feature.
    Analyzes generated tests for quality, similarity, and redundancy.
    """
    
    def __init__(self):
        """Initialize optimizer with all analyzers."""
        self.enabled = os.getenv("ENABLE_TEST_OPTIMIZATION", "true").lower() == "true"
        
        if self.enabled:
            self.similarity_analyzer = SimilarityAnalyzer()
            self.ai_suggestions = AISuggestions()
            self.redundancy_detector = RedundancyDetector()
            logger.info("Test Case Optimizer initialized (enabled)")
        else:
            logger.info("Test Case Optimizer initialized (disabled)")
    
    def optimize(
        self,
        generated_tests: str,
        existing_tests: Optional[List[str]] = None,
        codebase_context: Optional[Dict[str, Any]] = None
    ) -> OptimizationReport:
        """
        Main optimization method - runs all three analyses.
        
        Args:
            generated_tests: The generated test code as a string
            existing_tests: List of existing test file contents (optional)
            codebase_context: Context about the codebase (optional)
            
        Returns:
            OptimizationReport with all findings
        """
        if not self.enabled:
            logger.info("Optimization disabled, returning empty report")
            return OptimizationReport()
        
        try:
            logger.info("Starting test case optimization")
            
            # Parse test file into individual test cases
            test_cases = self._parse_tests(generated_tests)
            logger.info(f"Parsed {len(test_cases)} test cases")
            
            if not test_cases:
                logger.warning("No test cases found to optimize")
                return OptimizationReport()
            
            # Initialize report
            report = OptimizationReport()
            
            # Run all three optimizations
            try:
                report.similar_pairs = self.similarity_analyzer.analyze(test_cases)
                logger.info(f"Found {len(report.similar_pairs)} similar test pairs")
            except Exception as e:
                logger.error(f"Similarity analysis failed: {e}")
            
            try:
                report.optimizations = self.ai_suggestions.suggest(
                    test_cases, 
                    codebase_context or {}
                )
                logger.info(f"Generated {len(report.optimizations)} optimization suggestions")
            except Exception as e:
                logger.error(f"AI suggestions failed: {e}")
            
            try:
                redundant, outdated = self.redundancy_detector.detect(
                    test_cases,
                    existing_tests or [],
                    codebase_context or {}
                )
                report.redundant_tests = redundant
                report.outdated_tests = outdated
                logger.info(
                    f"Found {len(redundant)} redundant and "
                    f"{len(outdated)} outdated tests"
                )
            except Exception as e:
                logger.error(f"Redundancy detection failed: {e}")
            
            # Calculate quality score
            report.quality_score = self._calculate_quality_score(report)
            
            logger.info(f"Optimization complete. Quality score: {report.quality_score}/10")
            return report
            
        except Exception as e:
            logger.error(f"Test optimization failed: {e}", exc_info=True)
            return OptimizationReport()
    
    def _parse_tests(self, test_code: str) -> List[TestCase]:
        """
        Parse test code into individual TestCase objects.
        
        Args:
            test_code: The test file content
            
        Returns:
            List of TestCase objects
        """
        test_cases = []
        
        try:
            tree = ast.parse(test_code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if it's a test function
                    if node.name.startswith('test_'):
                        # Extract docstring
                        docstring = ast.get_docstring(node)
                        
                        # Get function code
                        func_lines = test_code.split('\n')[node.lineno-1:node.end_lineno]
                        func_code = '\n'.join(func_lines)
                        
                        test_case = TestCase(
                            name=node.name,
                            code=func_code,
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            docstring=docstring
                        )
                        test_cases.append(test_case)
                        
        except SyntaxError as e:
            logger.error(f"Failed to parse test code: {e}")
        except Exception as e:
            logger.error(f"Error parsing tests: {e}")
        
        return test_cases
    
    def _calculate_quality_score(self, report: OptimizationReport) -> float:
        """
        Calculate overall quality score (0-10).
        
        Args:
            report: The optimization report
            
        Returns:
            Quality score from 0 to 10
        """
        score = 10.0
        
        # Deduct for similar tests
        score -= len(report.similar_pairs) * 0.5
        
        # Deduct for redundant tests
        score -= len(report.redundant_tests) * 0.75
        
        # Deduct for outdated tests
        score -= len(report.outdated_tests) * 1.0
        
        # Deduct slightly for optimization opportunities (not critical but good to address)
        score -= len(report.optimizations) * 0.25
        
        # Ensure score is between 0 and 10
        return max(0.0, min(10.0, score))


