"""GitHub webhook handler for automated test generation."""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.models.github_issue import GenerateTestsRequest, GenerateTestsResponse
from app.github.client import GitHubClient
from app.github.code_search import CodeContextBuilder
from app.detectors.test_framework import TestFrameworkDetector
from app.llm.test_author import TestAuthor
from app.publisher.git_operations import GitOperations
from app.optimizers.test_optimizer import TestCaseOptimizer
from app.coverage.coverage_analyzer import CoverageAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter()


class TestGenerationService:
    """Service to orchestrate the entire test generation workflow."""
    
    def __init__(self):
        """Initialize the service."""
        self.github_client = None
        self.context_builder = None
        self.framework_detector = None
        self.test_author = None
        self.git_ops = None
        self.optimizer = None
        self.coverage_analyzer = None
    
    def _initialize_clients(self, repo_override: str = None):
        """Initialize all clients and services."""
        self.github_client = GitHubClient(repo_name=repo_override)
        self.context_builder = CodeContextBuilder(self.github_client)
        self.framework_detector = TestFrameworkDetector(self.github_client)
        self.test_author = TestAuthor()
        self.git_ops = GitOperations(self.github_client)
        self.optimizer = TestCaseOptimizer()
        self.coverage_analyzer = CoverageAnalyzer()
    
    def _get_existing_tests(self, test_dir: str) -> list:
        """
        Get existing test files from repository.
        
        Args:
            test_dir: Test directory path
            
        Returns:
            List of test file contents
        """
        try:
            existing_tests = []
            contents = self.github_client.list_directory(test_dir)
            
            # Limit to first 5 test files to avoid token overflow
            count = 0
            for item in contents:
                if count >= 5:
                    break
                
                if item['type'] == 'file' and 'test' in item['name'].lower():
                    content = self.github_client.get_file_content(item['path'])
                    if content:
                        existing_tests.append(content)
                        count += 1
            
            logger.info(f"Retrieved {len(existing_tests)} existing test files")
            return existing_tests
            
        except Exception as e:
            logger.warning(f"Failed to get existing tests: {e}")
            return []
    
    def generate_tests_for_issue(self, issue_number: int, repo_override: str = None) -> GenerateTestsResponse:
        """
        Main workflow: Generate tests for a GitHub issue.
        
        Args:
            issue_number: GitHub issue number.
            repo_override: Optional repository override.
            
        Returns:
            GenerateTestsResponse with results.
        """
        try:
            logger.info(f"Starting test generation for issue #{issue_number}")
            
            # Initialize clients
            self._initialize_clients(repo_override)
            
            # Step 1: Fetch issue
            logger.info("Step 1: Fetching issue from GitHub")
            issue = self.github_client.fetch_issue(issue_number)
            
            if not issue:
                raise Exception(f"Issue #{issue_number} not found")
            
            logger.info(f"Fetched issue: {issue.title}")
            
            # Step 2: Detect test framework
            logger.info("Step 2: Detecting test framework")
            framework_config = self.framework_detector.detect()
            logger.info(f"Detected framework: {framework_config['framework']}")
            
            # Step 3: Build code context
            logger.info("Step 3: Building code context")
            context = self.context_builder.build_context(issue, framework_config['framework'])
            context['test_framework'] = framework_config
            
            # Step 4: Generate tests using AI
            logger.info("Step 4: Generating tests with AI")
            test_code = self.test_author.generate_tests(context)
            
            if not test_code:
                raise Exception("AI generated empty test code")
            
            logger.info(f"Generated {len(test_code)} characters of test code")
            
            # Step 5: Run optimization analysis
            logger.info("Step 5: Running test case optimization")
            existing_test_files = self._get_existing_tests(framework_config['test_dir'])
            optimization_report = self.optimizer.optimize(
                generated_tests=test_code,
                existing_tests=existing_test_files,
                codebase_context=context
            )
            logger.info(
                f"Optimization complete. Quality score: {optimization_report.quality_score}/10"
            )
            
            # Step 6: Determine test file path
            test_filename = self.test_author.get_test_filename(
                issue_number,
                issue.title,
                framework_config
            )
            test_file_path = f"{framework_config['test_dir']}/{test_filename}"
            
            logger.info(f"Test file path: {test_file_path}")
            
            # Step 7: Publish to GitHub (branch, commit, PR)
            logger.info("Step 7: Publishing tests to GitHub")
            publish_result = self.git_ops.publish_test(
                issue_number=issue_number,
                test_file_path=test_file_path,
                test_content=test_code,
                issue_title=issue.title,
                optimization_report=optimization_report
            )
            
            if not publish_result['success']:
                raise Exception(f"Failed to publish tests: {publish_result['error']}")
            
            # Step 8: Run coverage analysis
            coverage_report = None
            try:
                logger.info("Step 8: Running coverage analysis")
                coverage_report = self.coverage_analyzer.analyze(
                    repo_url=self.github_client.get_repo_url(),
                    test_file_path=test_file_path,
                    framework_config=framework_config,
                    branch_name=publish_result['branch_name']
                )
                logger.info(
                    f"Coverage analysis complete: "
                    f"{coverage_report.before_coverage:.1f}% → "
                    f"{coverage_report.after_coverage:.1f}%"
                )
            except Exception as e:
                logger.warning(f"Coverage analysis failed (non-critical): {e}")
            
            # Step 9: Post comment on issue
            logger.info("Step 9: Posting comment on issue")
            self.git_ops.post_issue_comment(
                issue_number=issue_number,
                pr_url=publish_result['pr_url'],
                test_file_path=test_file_path,
                success=True
            )
            
            # Step 10: Post coverage report to issue (if available)
            if coverage_report and coverage_report.success:
                logger.info("Step 10: Posting coverage report to issue")
                self.git_ops.post_coverage_comment(
                    issue_number=issue_number,
                    coverage_report=coverage_report
                )
            
            logger.info(f"✅ Test generation complete for issue #{issue_number}")
            
            return GenerateTestsResponse(
                success=True,
                message="Tests generated and published successfully",
                issue_number=issue_number,
                branch_name=publish_result['branch_name'],
                pull_request_url=publish_result['pr_url'],
                test_files=[test_file_path],
                error=None
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Test generation failed for issue #{issue_number}: {error_msg}", exc_info=True)
            
            # Try to post failure comment on issue
            try:
                if self.git_ops:
                    self.git_ops.post_issue_comment(
                        issue_number=issue_number,
                        pr_url=None,
                        test_file_path="",
                        success=False,
                        error=error_msg
                    )
            except Exception as comment_error:
                logger.error(f"Failed to post error comment: {comment_error}")
            
            return GenerateTestsResponse(
                success=False,
                message="Test generation failed",
                issue_number=issue_number,
                branch_name=None,
                pull_request_url=None,
                test_files=[],
                error=error_msg
            )


# Initialize service
test_generation_service = TestGenerationService()


@router.post("/generate-tests", response_model=GenerateTestsResponse)
async def generate_tests(
    request: GenerateTestsRequest,
    background_tasks: BackgroundTasks
) -> GenerateTestsResponse:
    """
    Generate tests for a GitHub issue.
    
    This endpoint triggers the full test generation workflow:
    1. Fetch issue from GitHub
    2. Detect test framework
    3. Build code context
    4. Generate tests with AI
    5. Create branch and commit
    6. Create pull request
    7. Post comment on issue
    
    Args:
        request: Request with issue_number and optional repo_override.
        background_tasks: FastAPI background tasks (for async processing).
        
    Returns:
        GenerateTestsResponse with results.
    """
    logger.info(f"Received test generation request for issue #{request.issue_number}")
    
    try:
        # Run synchronously for now (can be moved to background for production)
        result = test_generation_service.generate_tests_for_issue(
            issue_number=request.issue_number,
            repo_override=request.repo_override
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Request handler failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "github-test-generator"}


# Webhook endpoint for future GitHub webhook integration
@router.post("/webhook")
async def github_webhook(background_tasks: BackgroundTasks):
    """
    GitHub webhook endpoint (future enhancement).
    
    This will be used to automatically trigger test generation
    when issues are created or labeled.
    """
    return {
        "message": "Webhook endpoint - to be implemented",
        "status": "pending"
    }


