"""Redundancy and outdated test detector using AST analysis."""

import logging
import os
import ast
from typing import List, Dict, Any, Tuple

from app.optimizers.models import TestCase, RedundantTest, OutdatedTest

logger = logging.getLogger(__name__)


class RedundancyDetector:
    """
    Detects redundant and outdated tests.
    Uses AST parsing to check for duplicates and stale code.
    """
    
    def __init__(self):
        """Initialize redundancy detector."""
        self.check_redundant = os.getenv("CHECK_REDUNDANT_TESTS", "true").lower() == "true"
        self.check_outdated = os.getenv("CHECK_OUTDATED_IMPORTS", "true").lower() == "true"
        logger.info(
            f"Redundancy detector initialized "
            f"(redundant: {self.check_redundant}, outdated: {self.check_outdated})"
        )
    
    def detect(
        self,
        test_cases: List[TestCase],
        existing_tests: List[str],
        codebase_context: Dict[str, Any]
    ) -> Tuple[List[RedundantTest], List[OutdatedTest]]:
        """
        Detect redundant and outdated tests.
        
        Args:
            test_cases: New test cases to check
            existing_tests: Existing test file contents
            codebase_context: Codebase context
            
        Returns:
            Tuple of (redundant_tests, outdated_tests)
        """
        redundant_tests = []
        outdated_tests = []
        
        if self.check_redundant and existing_tests:
            redundant_tests = self._find_redundant(test_cases, existing_tests)
        
        if self.check_outdated:
            outdated_tests = self._find_outdated(test_cases, codebase_context)
        
        return redundant_tests, outdated_tests
    
    def _find_redundant(
        self,
        test_cases: List[TestCase],
        existing_tests: List[str]
    ) -> List[RedundantTest]:
        """
        Find tests that are redundant with existing tests.
        
        Args:
            test_cases: New test cases
            existing_tests: Existing test file contents
            
        Returns:
            List of redundant tests
        """
        redundant = []
        
        try:
            # Parse existing tests
            existing_test_names = set()
            existing_test_assertions = {}
            
            for existing_test_code in existing_tests:
                try:
                    tree = ast.parse(existing_test_code)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                            existing_test_names.add(node.name)
                            # Extract assertions
                            assertions = self._extract_assertions(node)
                            existing_test_assertions[node.name] = assertions
                except:
                    continue
            
            # Check new tests against existing
            for test in test_cases:
                # Check for exact name match
                if test.name in existing_test_names:
                    redundant.append(RedundantTest(
                        test=test.name,
                        reason="Test with same name already exists",
                        existing_test=f"existing test: {test.name}",
                        suggestion="Remove or rename this test"
                    ))
                    continue
                
                # Check for similar assertions
                try:
                    tree = ast.parse(test.code)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            new_assertions = self._extract_assertions(node)
                            
                            # Compare with existing tests
                            for existing_name, existing_assertions in existing_test_assertions.items():
                                if self._assertions_overlap(new_assertions, existing_assertions):
                                    redundant.append(RedundantTest(
                                        test=test.name,
                                        reason=f"Similar assertions to existing test",
                                        existing_test=existing_name,
                                        suggestion="Consider consolidating or making more specific"
                                    ))
                                    break
                except:
                    continue
            
            logger.info(f"Found {len(redundant)} redundant tests")
            
        except Exception as e:
            logger.error(f"Redundancy check failed: {e}")
        
        return redundant
    
    def _find_outdated(
        self,
        test_cases: List[TestCase],
        codebase_context: Dict[str, Any]
    ) -> List[OutdatedTest]:
        """
        Find tests with outdated imports or references.
        
        Args:
            test_cases: Test cases to check
            codebase_context: Codebase context with file info
            
        Returns:
            List of outdated tests
        """
        outdated = []
        
        try:
            # Get list of existing modules from codebase
            existing_modules = self._get_existing_modules(codebase_context)
            
            for test in test_cases:
                try:
                    tree = ast.parse(test.code)
                    
                    # Check imports
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                if not self._module_exists(alias.name, existing_modules):
                                    outdated.append(OutdatedTest(
                                        test=test.name,
                                        issue=f"Imports non-existent module: {alias.name}",
                                        fix=f"Update or remove import of {alias.name}",
                                        severity="high"
                                    ))
                        
                        elif isinstance(node, ast.ImportFrom):
                            if node.module and not self._module_exists(node.module, existing_modules):
                                outdated.append(OutdatedTest(
                                    test=test.name,
                                    issue=f"Imports from non-existent module: {node.module}",
                                    fix=f"Update or remove import from {node.module}",
                                    severity="high"
                                ))
                
                except SyntaxError:
                    continue
                except Exception as e:
                    logger.warning(f"Error checking test {test.name}: {e}")
                    continue
            
            logger.info(f"Found {len(outdated)} outdated tests")
            
        except Exception as e:
            logger.error(f"Outdated check failed: {e}")
        
        return outdated
    
    def _extract_assertions(self, func_node: ast.FunctionDef) -> List[str]:
        """
        Extract assertion patterns from a test function.
        
        Args:
            func_node: AST function node
            
        Returns:
            List of assertion signatures
        """
        assertions = []
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Assert):
                # Convert assertion to string representation
                try:
                    assertion_str = ast.unparse(node.test)
                    assertions.append(assertion_str)
                except:
                    pass
            
            # Also check for pytest-style assertions
            elif isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Call):
                    if hasattr(node.value.func, 'attr'):
                        if node.value.func.attr == 'assert':
                            try:
                                assertion_str = ast.unparse(node.value)
                                assertions.append(assertion_str)
                            except:
                                pass
        
        return assertions
    
    def _assertions_overlap(self, assertions1: List[str], assertions2: List[str]) -> bool:
        """
        Check if two sets of assertions significantly overlap.
        
        Args:
            assertions1: First set of assertions
            assertions2: Second set of assertions
            
        Returns:
            True if significant overlap (>50%)
        """
        if not assertions1 or not assertions2:
            return False
        
        # Count matching assertions (allowing for slight variations)
        matches = 0
        for a1 in assertions1:
            for a2 in assertions2:
                # Simple string similarity check
                if a1 == a2 or a1 in a2 or a2 in a1:
                    matches += 1
                    break
        
        # If more than 50% overlap, consider it redundant
        overlap_ratio = matches / min(len(assertions1), len(assertions2))
        return overlap_ratio > 0.5
    
    def _get_existing_modules(self, codebase_context: Dict[str, Any]) -> set:
        """
        Get set of existing module paths from codebase context.
        
        Args:
            codebase_context: Codebase context
            
        Returns:
            Set of module paths
        """
        modules = set()
        
        # Extract from relevant code files
        relevant_code = codebase_context.get('relevant_code', [])
        for code_file in relevant_code:
            path = code_file.get('path', '')
            if path:
                # Convert file path to module path
                module = path.replace('/', '.').replace('.py', '')
                modules.add(module)
        
        return modules
    
    def _module_exists(self, module_name: str, existing_modules: set) -> bool:
        """
        Check if a module exists in the codebase.
        
        Args:
            module_name: Module name to check
            existing_modules: Set of existing module paths
            
        Returns:
            True if module exists or is a standard library module
        """
        # Standard library modules always exist
        stdlib_modules = {
            'os', 'sys', 'ast', 'json', 'typing', 'logging',
            'pytest', 'unittest', 're', 'math', 'datetime',
            'collections', 'itertools', 'functools'
        }
        
        if module_name.split('.')[0] in stdlib_modules:
            return True
        
        # Check against existing modules
        for existing in existing_modules:
            if module_name in existing or existing in module_name:
                return True
        
        return False


