"""Enhanced test generation using codebase context and OpenAI."""

import logging
import os
from typing import Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class TestAuthor:
    """Generate tests using codebase context and AI."""
    
    # Framework-specific templates and system prompts
    FRAMEWORK_PROMPTS = {
        "pytest": {
            "language": "Python",
            "import_statement": "import pytest",
            "test_decorator": "@pytest.mark",
            "assertion_style": "assert",
            "file_extension": ".py"
        },
        "unittest": {
            "language": "Python",
            "import_statement": "import unittest",
            "test_decorator": "",
            "assertion_style": "self.assert",
            "file_extension": ".py"
        },
        "jest": {
            "language": "JavaScript/TypeScript",
            "import_statement": "import { describe, it, expect } from '@jest/globals';",
            "test_decorator": "",
            "assertion_style": "expect()",
            "file_extension": ".test.ts"
        },
        "playwright": {
            "language": "TypeScript",
            "import_statement": "import { test, expect } from '@playwright/test';",
            "test_decorator": "test.describe",
            "assertion_style": "expect()",
            "file_extension": ".spec.ts"
        },
        "mocha": {
            "language": "JavaScript",
            "import_statement": "const { describe, it } = require('mocha');",
            "test_decorator": "",
            "assertion_style": "expect()",
            "file_extension": ".test.js"
        },
        "vitest": {
            "language": "TypeScript",
            "import_statement": "import { describe, it, expect } from 'vitest';",
            "test_decorator": "",
            "assertion_style": "expect()",
            "file_extension": ".test.ts"
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize test author.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        logger.info(f"Initialized TestAuthor with model: {self.model}")
    
    def _build_system_prompt(self, framework: str) -> str:
        """Build framework-specific system prompt."""
        framework_info = self.FRAMEWORK_PROMPTS.get(framework, self.FRAMEWORK_PROMPTS["pytest"])
        
        return f"""You are an expert QA engineer and test automation specialist.

Your task is to generate high-quality, production-ready automated tests using {framework} framework in {framework_info['language']}.

Requirements:
1. Generate 3-7 focused test cases that directly map to the acceptance criteria
2. Each test MUST include a comment linking it to the acceptance criteria (e.g., // AC1: Description)
3. Follow the existing codebase patterns and conventions shown in the context
4. Use the same coding style, imports, and patterns as the example code provided
5. Write clear, maintainable tests with descriptive names
6. Include proper setup and teardown if needed
7. Use appropriate assertions with clear failure messages
8. Follow {framework} best practices

Code Quality:
- Use meaningful variable and function names
- Add comments for complex logic
- Structure tests logically (Arrange, Act, Assert pattern)
- Consider edge cases and error scenarios
- Make tests independent and idempotent

Output Format:
- Return ONLY the test code
- Do NOT wrap in markdown code fences
- Do NOT include explanatory text before or after the code
- The code should be immediately executable
- Use proper imports based on the framework and existing code patterns
"""
    
    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        """Build user prompt with full context."""
        issue = context["issue"]
        framework = context.get("test_framework", {})
        relevant_code = context.get("relevant_code", [])
        test_examples = context.get("test_examples", [])
        
        prompt_parts = [
            "Generate automated tests for the following GitHub issue:\n",
            f"Issue #{issue['number']}: {issue['title']}\n",
            f"\nDescription:\n{issue['body']}\n"
        ]
        
        # Add acceptance criteria if available
        if issue.get("acceptance_criteria"):
            prompt_parts.append(f"\nAcceptance Criteria:\n{issue['acceptance_criteria']}\n")
        
        # Add framework information
        if framework:
            prompt_parts.append(f"\nTest Framework: {framework.get('framework', 'unknown')}")
            prompt_parts.append(f"Test Directory: {framework.get('test_dir', 'tests')}")
            prompt_parts.append(f"File Pattern: {framework.get('test_pattern', 'test_*.py')}\n")
        
        # Add relevant code context
        if relevant_code:
            prompt_parts.append("\n--- RELEVANT CODE FROM REPOSITORY ---\n")
            for code_file in relevant_code[:3]:  # Limit to top 3 files
                prompt_parts.append(f"\nFile: {code_file['path']}\n")
                prompt_parts.append(f"```\n{code_file['content']}\n```\n")
        
        # Add test examples
        if test_examples:
            prompt_parts.append("\n--- EXISTING TEST EXAMPLES (for pattern reference) ---\n")
            for test_file in test_examples[:2]:  # Limit to top 2 examples
                prompt_parts.append(f"\nFile: {test_file['path']}\n")
                prompt_parts.append(f"```\n{test_file['content']}\n```\n")
        
        prompt_parts.append("\n--- INSTRUCTIONS ---\n")
        prompt_parts.append("Generate comprehensive tests following the patterns shown above.")
        prompt_parts.append("Return ONLY the test code, no markdown fences or explanations.")
        
        return "".join(prompt_parts)
    
    def generate_tests(self, context: Dict[str, Any]) -> str:
        """
        Generate tests using AI with full codebase context.
        
        Args:
            context: Dictionary containing issue, codebase context, and framework info.
            
        Returns:
            Generated test code as string.
            
        Raises:
            Exception: If test generation fails.
        """
        try:
            framework = context.get("test_framework", {}).get("framework", "pytest")
            system_prompt = self._build_system_prompt(framework)
            user_prompt = self._build_user_prompt(context)
            
            logger.info(f"Generating tests for issue #{context['issue']['number']} using {framework}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            generated_code = response.choices[0].message.content.strip()
            
            # Clean up markdown fences if present
            if generated_code.startswith("```"):
                lines = generated_code.split("\n")
                # Remove first line with language tag
                if lines[0].startswith("```"):
                    lines = lines[1:]
                # Remove closing fence
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                generated_code = "\n".join(lines)
            
            logger.info(f"Successfully generated {len(generated_code)} characters of test code")
            return generated_code
            
        except Exception as e:
            logger.error(f"Test generation failed: {e}", exc_info=True)
            raise Exception(f"Failed to generate tests: {str(e)}")
    
    def get_test_filename(self, issue_number: int, issue_title: str, framework_config: Dict[str, Any]) -> str:
        """
        Generate appropriate test filename.
        
        Args:
            issue_number: GitHub issue number.
            issue_title: GitHub issue title.
            framework_config: Framework configuration with pattern.
            
        Returns:
            Test filename.
        """
        # Sanitize title for filename
        safe_title = "".join(c if c.isalnum() else "_" for c in issue_title.lower())
        safe_title = safe_title[:40]  # Limit length
        
        # Get file extension from framework
        framework = framework_config.get("framework", "pytest")
        extension = self.FRAMEWORK_PROMPTS.get(framework, {}).get("file_extension", ".py")
        
        # Get pattern from config
        pattern = framework_config.get("test_pattern", "test_*.py")
        
        # Construct filename based on pattern
        if pattern.startswith("test_"):
            filename = f"test_{safe_title}_issue_{issue_number}{extension}"
        elif pattern.endswith("_test.py"):
            filename = f"{safe_title}_issue_{issue_number}_test{extension}"
        elif ".spec." in pattern:
            filename = f"{safe_title}_issue_{issue_number}.spec{extension}"
        elif ".test." in pattern:
            filename = f"{safe_title}_issue_{issue_number}.test{extension}"
        else:
            filename = f"test_{safe_title}_issue_{issue_number}{extension}"
        
        return filename


