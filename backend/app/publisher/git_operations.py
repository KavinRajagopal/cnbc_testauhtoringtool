"""Git operations orchestrator for test publishing."""

import logging
from typing import Optional, Dict, Any
from app.github.client import GitHubClient
from app.optimizers.models import OptimizationReport
from app.coverage.coverage_models import CoverageReport

logger = logging.getLogger(__name__)


class GitOperations:
    """Orchestrate git operations for test publishing."""
    
    def __init__(self, github_client: GitHubClient):
        """
        Initialize git operations.
        
        Args:
            github_client: Initialized GitHub client.
        """
        self.client = github_client
    
    def publish_test(
        self,
        issue_number: int,
        test_file_path: str,
        test_content: str,
        issue_title: str,
        optimization_report: Optional[OptimizationReport] = None
    ) -> Dict[str, Any]:
        """
        Publish test to GitHub: create branch, commit file, create PR.
        
        Args:
            issue_number: GitHub issue number.
            test_file_path: Path where test file should be created.
            test_content: Test code content.
            issue_title: Issue title for PR.
            optimization_report: Optional optimization analysis report.
            
        Returns:
            Dictionary with operation results:
            {
                "success": bool,
                "branch_name": str,
                "pr_url": str,
                "error": Optional[str]
            }
        """
        branch_name = f"auto-tests/issue-{issue_number}"
        base_branch = self.client.get_default_branch()
        
        try:
            # Step 1: Create branch
            logger.info(f"Creating branch: {branch_name}")
            if not self.client.create_branch(branch_name, base_branch):
                return {
                    "success": False,
                    "branch_name": branch_name,
                    "pr_url": None,
                    "error": "Failed to create branch"
                }
            
            # Step 2: Commit test file
            commit_message = f"feat: Add automated tests for issue #{issue_number}\n\nGenerated tests for: {issue_title}"
            logger.info(f"Committing test file: {test_file_path}")
            
            if not self.client.commit_file(
                file_path=test_file_path,
                content=test_content,
                message=commit_message,
                branch=branch_name
            ):
                return {
                    "success": False,
                    "branch_name": branch_name,
                    "pr_url": None,
                    "error": "Failed to commit test file"
                }
            
            # Step 3: Create pull request
            pr_title = f"🤖 Automated Tests for #{issue_number}: {issue_title}"
            pr_body = self._build_pr_body(
                issue_number, 
                test_file_path, 
                issue_title,
                optimization_report
            )
            
            logger.info(f"Creating pull request from {branch_name} to {base_branch}")
            pr = self.client.create_pull_request(
                title=pr_title,
                body=pr_body,
                head_branch=branch_name,
                base_branch=base_branch
            )
            
            if not pr:
                return {
                    "success": False,
                    "branch_name": branch_name,
                    "pr_url": None,
                    "error": "Failed to create pull request"
                }
            
            logger.info(f"Successfully published test. PR URL: {pr.html_url}")
            
            return {
                "success": True,
                "branch_name": branch_name,
                "pr_url": pr.html_url,
                "pr_number": pr.number,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Failed to publish test: {e}", exc_info=True)
            return {
                "success": False,
                "branch_name": branch_name,
                "pr_url": None,
                "error": str(e)
            }
    
    def _build_pr_body(
        self,
        issue_number: int,
        test_file_path: str,
        issue_title: str,
        optimization_report: Optional[OptimizationReport] = None
    ) -> str:
        """Build pull request description with optimization report."""
        pr_body = f"""## 🤖 Automated Test Generation

This PR contains automatically generated tests for issue #{issue_number}.

### 📋 Issue Details
- **Issue**: #{issue_number} - {issue_title}
- **Test File**: `{test_file_path}`

### ✅ What's Included
- Automated test cases based on acceptance criteria
- Tests follow repository conventions and framework patterns
- Ready for review and refinement

"""
        
        # Add optimization report if available
        if optimization_report and optimization_report.has_issues():
            pr_body += "\n---\n\n"
            pr_body += optimization_report.to_markdown()
            pr_body += "\n"
        elif optimization_report:
            pr_body += f"\n### ✅ Test Quality: {optimization_report.quality_score:.1f}/10\n"
            pr_body += "All generated tests look good with no issues detected!\n\n"
        
        pr_body += """### 🔍 Review Notes
Please review the generated tests to ensure they:
- Cover all acceptance criteria
- Follow team coding standards
- Include appropriate assertions and edge cases
- Are maintainable and clear

### 🔗 Related Issue
Closes #{issue_number}

---
*This PR was generated automatically by the Test Authoring Tool*
"""
        
        return pr_body.format(issue_number=issue_number)
    
    def post_issue_comment(
        self,
        issue_number: int,
        pr_url: Optional[str],
        test_file_path: str,
        success: bool,
        error: Optional[str] = None
    ) -> bool:
        """
        Post a comment on the issue with test generation results.
        
        Args:
            issue_number: GitHub issue number.
            pr_url: URL of created pull request (if successful).
            test_file_path: Path to generated test file.
            success: Whether generation was successful.
            error: Error message if failed.
            
        Returns:
            True if comment posted successfully.
        """
        if success:
            comment = f"""## ✅ Automated Tests Generated

I've generated automated tests for this issue!

### 📝 Details
- **Test File**: `{test_file_path}`
- **Pull Request**: {pr_url}

### 🚀 Next Steps
1. Review the generated tests in the PR
2. Make any necessary adjustments
3. Ensure tests pass in CI
4. Merge when ready

The tests have been created based on the acceptance criteria and existing codebase patterns.
"""
        else:
            comment = f"""## ❌ Test Generation Failed

I attempted to generate automated tests for this issue, but encountered an error:

**Error**: {error}

### 🔧 Possible Solutions
- Verify the issue has clear acceptance criteria
- Check that the repository is properly configured
- Review the logs for more details

Please try again or contact the maintainers for assistance.
"""
        
        return self.client.post_issue_comment(issue_number, comment)
    
    def post_coverage_comment(
        self,
        issue_number: int,
        coverage_report: CoverageReport
    ) -> bool:
        """
        Post coverage analysis report as a comment on the issue.
        
        Args:
            issue_number: GitHub issue number
            coverage_report: CoverageReport object
            
        Returns:
            True if comment posted successfully
        """
        try:
            comment = coverage_report.to_markdown()
            return self.client.post_issue_comment(issue_number, comment)
        except Exception as e:
            logger.error(f"Failed to post coverage comment: {e}")
            return False


