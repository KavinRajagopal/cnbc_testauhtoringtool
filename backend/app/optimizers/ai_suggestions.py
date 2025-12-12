"""AI-powered test optimization suggestions using GPT."""

import logging
import os
import json
from typing import List, Dict, Any
from openai import OpenAI

from app.optimizers.models import TestCase, OptimizationSuggestion

logger = logging.getLogger(__name__)


class AISuggestions:
    """
    Uses GPT to suggest test improvements and best practices.
    """
    
    def __init__(self):
        """Initialize AI suggestions analyzer."""
        self.enabled = os.getenv("ENABLE_AI_SUGGESTIONS", "true").lower() == "true"
        self.model = os.getenv("AI_OPTIMIZATION_MODEL", "gpt-4o-mini")
        
        if self.enabled:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
                logger.info(f"AI suggestions initialized (model: {self.model})")
            else:
                logger.warning("OpenAI API key not found, AI suggestions disabled")
                self.client = None
        else:
            self.client = None
            logger.info("AI suggestions disabled")
    
    def suggest(
        self,
        test_cases: List[TestCase],
        codebase_context: Dict[str, Any]
    ) -> List[OptimizationSuggestion]:
        """
        Generate AI-powered optimization suggestions.
        
        Args:
            test_cases: List of test cases to analyze
            codebase_context: Context about the codebase
            
        Returns:
            List of optimization suggestions
        """
        if not self.client or not test_cases:
            return []
        
        try:
            logger.info(f"Generating AI suggestions for {len(test_cases)} tests")
            
            # Build prompt for GPT
            prompt = self._build_prompt(test_cases, codebase_context)
            
            # Call GPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse response
            suggestions_text = response.choices[0].message.content
            suggestions = self._parse_suggestions(suggestions_text)
            
            logger.info(f"Generated {len(suggestions)} AI suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"AI suggestions failed: {e}", exc_info=True)
            return []
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for GPT."""
        return """You are an expert test automation engineer analyzing test code quality.

Your task is to identify optimization opportunities in the provided tests. Focus on:

1. **Parameterization**: Tests with similar logic but different inputs
2. **Fixture Extraction**: Repeated setup code that could be fixtures
3. **Assertion Improvements**: Better assertion patterns or missing assertions
4. **Code Smells**: Antipatterns, hard-coded values, poor naming
5. **Missing Edge Cases**: Important scenarios not covered

Respond ONLY with valid JSON in this format:
```json
{
  "suggestions": [
    {
      "type": "parameterization|fixture|assertion|code_smell|edge_case",
      "tests": ["test_name1", "test_name2"],
      "reason": "Brief explanation of the issue",
      "suggestion": "What to do to fix it",
      "code_example": "Optional code example"
    }
  ]
}
```

Be concise and actionable. Limit to the top 5 most important suggestions."""
    
    def _build_prompt(
        self,
        test_cases: List[TestCase],
        codebase_context: Dict[str, Any]
    ) -> str:
        """
        Build prompt for GPT.
        
        Args:
            test_cases: Test cases to analyze
            codebase_context: Codebase context
            
        Returns:
            Prompt string
        """
        prompt_parts = ["Analyze these test cases for optimization opportunities:\n\n"]
        
        # Add framework info
        framework = codebase_context.get('test_framework', {}).get('framework', 'pytest')
        prompt_parts.append(f"Test Framework: {framework}\n\n")
        
        # Add test code
        prompt_parts.append("=== TEST CASES ===\n\n")
        for test in test_cases:
            prompt_parts.append(f"Test: {test.name}\n")
            if test.docstring:
                prompt_parts.append(f"Doc: {test.docstring}\n")
            prompt_parts.append(f"```python\n{test.code}\n```\n\n")
        
        prompt_parts.append("\nProvide optimization suggestions as JSON.")
        
        return "".join(prompt_parts)
    
    def _parse_suggestions(self, response_text: str) -> List[OptimizationSuggestion]:
        """
        Parse GPT response into structured suggestions.
        
        Args:
            response_text: Raw GPT response
            
        Returns:
            List of OptimizationSuggestion objects
        """
        suggestions = []
        
        try:
            # Try to find JSON in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                data = json.loads(json_text)
                
                for item in data.get('suggestions', []):
                    suggestion = OptimizationSuggestion(
                        type=item.get('type', 'general'),
                        tests=item.get('tests', []),
                        reason=item.get('reason', ''),
                        suggestion=item.get('suggestion', ''),
                        code_example=item.get('code_example')
                    )
                    suggestions.append(suggestion)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            # Try to extract suggestions from text
            suggestions = self._fallback_parse(response_text)
        except Exception as e:
            logger.error(f"Error parsing suggestions: {e}")
        
        return suggestions
    
    def _fallback_parse(self, text: str) -> List[OptimizationSuggestion]:
        """
        Fallback parsing if JSON parsing fails.
        
        Args:
            text: Response text
            
        Returns:
            List of suggestions (best effort)
        """
        suggestions = []
        
        # Look for common patterns
        if "parametrize" in text.lower() or "parameter" in text.lower():
            suggestions.append(OptimizationSuggestion(
                type="parameterization",
                tests=[],
                reason="Tests have similar logic with different inputs",
                suggestion="Consider using @pytest.mark.parametrize",
                code_example=None
            ))
        
        if "fixture" in text.lower():
            suggestions.append(OptimizationSuggestion(
                type="fixture",
                tests=[],
                reason="Common setup code detected",
                suggestion="Extract repeated setup to a fixture",
                code_example=None
            ))
        
        return suggestions


