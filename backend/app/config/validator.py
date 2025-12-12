"""Configuration validators with real API calls and retry logic."""

import logging
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime

from openai import OpenAI, OpenAIError
from github import Github, GithubException
import git

from .models import ValidationResult, RepositoryInfo

logger = logging.getLogger(__name__)


def validate_openai_key(api_key: str, max_retries: int = 3) -> ValidationResult:
    """
    Validate OpenAI API key by making a real API call.
    
    Args:
        api_key: OpenAI API key to validate
        max_retries: Maximum number of retry attempts
        
    Returns:
        ValidationResult with success status and any error messages
    """
    try:
        # Create OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Make a minimal test request (very cheap)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        
        logger.info("OpenAI API key validated successfully")
        return ValidationResult(
            success=True,
            attempts_remaining=max_retries,
            api_response={"model": response.model}
        )
        
    except OpenAIError as e:
        error_str = str(e)
        
        # Parse different error types
        if "401" in error_str or "Unauthorized" in error_str:
            return ValidationResult(
                success=False,
                error_message="Invalid API key (401 Unauthorized)",
                retry_suggestion=(
                    "Possible issues:\n"
                    "• Key format is incorrect (should start with 'sk-')\n"
                    "• Key has been revoked or expired\n"
                    "• Account has insufficient credits\n\n"
                    "Get a new key at: https://platform.openai.com/api-keys"
                ),
                attempts_remaining=max_retries - 1
            )
        elif "403" in error_str:
            return ValidationResult(
                success=False,
                error_message="Access forbidden (403)",
                retry_suggestion=(
                    "Your API key may not have access to this model.\n"
                    "Check your OpenAI account settings."
                ),
                attempts_remaining=max_retries - 1
            )
        elif "429" in error_str or "rate" in error_str.lower():
            return ValidationResult(
                success=False,
                error_message="Rate limited (429)",
                retry_suggestion="Too many requests. Wait 60 seconds and try again.",
                attempts_remaining=max_retries - 1
            )
        else:
            return ValidationResult(
                success=False,
                error_message=f"OpenAI API error: {error_str}",
                retry_suggestion="Check your API key and internet connection.",
                attempts_remaining=max_retries - 1
            )
            
    except Exception as e:
        return ValidationResult(
            success=False,
            error_message=f"Unexpected error: {str(e)}",
            retry_suggestion="Check your internet connection and try again.",
            attempts_remaining=max_retries - 1
        )


def validate_github_token(token: str, max_retries: int = 3) -> ValidationResult:
    """
    Validate GitHub token by calling the API and checking permissions.
    
    Args:
        token: GitHub personal access token
        max_retries: Maximum number of retry attempts
        
    Returns:
        ValidationResult with success status and any error messages
    """
    try:
        # Create GitHub client
        client = Github(token)
        
        # Test token by getting user info
        user = client.get_user()
        login = user.login
        
        # Check token scopes (from API response headers)
        # Note: PyGithub doesn't expose headers directly, so we'll do a basic check
        # and validate repo access in the next step
        
        logger.info(f"GitHub token validated successfully for user: {login}")
        return ValidationResult(
            success=True,
            attempts_remaining=max_retries,
            api_response={"user": login}
        )
        
    except GithubException as e:
        status_code = e.status
        
        if status_code == 401:
            return ValidationResult(
                success=False,
                error_message="Invalid GitHub token (401 Unauthorized)",
                retry_suggestion=(
                    "Possible issues:\n"
                    "• Token format is incorrect (should start with 'ghp_' or 'github_pat_')\n"
                    "• Token has been revoked or expired\n\n"
                    "Create a new token at: https://github.com/settings/tokens"
                ),
                attempts_remaining=max_retries - 1
            )
        elif status_code == 403:
            return ValidationResult(
                success=False,
                error_message="Access forbidden (403)",
                retry_suggestion=(
                    "Your token may not have sufficient permissions.\n"
                    "Required scopes: repo (full), workflow"
                ),
                attempts_remaining=max_retries - 1
            )
        elif status_code == 429:
            return ValidationResult(
                success=False,
                error_message="Rate limited (429)",
                retry_suggestion="Too many requests. Wait 60 seconds and try again.",
                attempts_remaining=max_retries - 1
            )
        else:
            return ValidationResult(
                success=False,
                error_message=f"GitHub API error ({status_code}): {e.data.get('message', str(e))}",
                retry_suggestion="Check your token and try again.",
                attempts_remaining=max_retries - 1
            )
            
    except Exception as e:
        return ValidationResult(
            success=False,
            error_message=f"Unexpected error: {str(e)}",
            retry_suggestion="Check your internet connection and try again.",
            attempts_remaining=max_retries - 1
        )


def validate_github_repo(token: str, repo: str, max_retries: int = 3) -> ValidationResult:
    """
    Validate GitHub repository access.
    
    Args:
        token: GitHub personal access token
        repo: Repository in format "owner/repo"
        max_retries: Maximum number of retry attempts
        
    Returns:
        ValidationResult with success status and repository details
    """
    try:
        # Create GitHub client
        client = Github(token)
        
        # Try to access the repository
        repository = client.get_repo(repo)
        
        # Get repository details
        details = {
            "name": repository.name,
            "full_name": repository.full_name,
            "language": repository.language,
            "stars": repository.stargazers_count,
            "updated_at": repository.updated_at.isoformat() if repository.updated_at else None,
            "private": repository.private
        }
        
        logger.info(f"Repository validated successfully: {repo}")
        return ValidationResult(
            success=True,
            attempts_remaining=max_retries,
            api_response=details
        )
        
    except GithubException as e:
        status_code = e.status
        
        if status_code == 404:
            return ValidationResult(
                success=False,
                error_message=f"Repository '{repo}' not found (404)",
                retry_suggestion=(
                    "Possible issues:\n"
                    "• Repository name is misspelled\n"
                    "• Repository is private and token doesn't have access\n"
                    "• Repository doesn't exist\n\n"
                    "Format should be: owner/repository"
                ),
                attempts_remaining=max_retries - 1
            )
        elif status_code == 403:
            return ValidationResult(
                success=False,
                error_message="Access forbidden (403)",
                retry_suggestion=(
                    "Your token doesn't have permission to access this repository.\n"
                    "Make sure:\n"
                    "• Token has 'repo' scope for private repos\n"
                    "• You have access to this repository"
                ),
                attempts_remaining=max_retries - 1
            )
        else:
            return ValidationResult(
                success=False,
                error_message=f"GitHub API error ({status_code}): {e.data.get('message', str(e))}",
                retry_suggestion="Check the repository name and try again.",
                attempts_remaining=max_retries - 1
            )
            
    except Exception as e:
        return ValidationResult(
            success=False,
            error_message=f"Unexpected error: {str(e)}",
            retry_suggestion="Check the repository format (owner/repo) and try again.",
            attempts_remaining=max_retries - 1
        )


def detect_repository_info(token: str, repo: str) -> Optional[RepositoryInfo]:
    """
    Shallow clone repository and detect framework/language.
    
    Args:
        token: GitHub personal access token
        repo: Repository in format "owner/repo"
        
    Returns:
        RepositoryInfo with detected configuration, or None if detection fails
    """
    temp_dir = None
    
    try:
        # Get repository URL
        clone_url = f"https://{token}@github.com/{repo}.git"
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="repo_analysis_")
        
        logger.info(f"Shallow cloning repository {repo} to {temp_dir}")
        
        # Shallow clone (depth=1)
        git.Repo.clone_from(
            clone_url,
            temp_dir,
            depth=1,
            single_branch=True
        )
        
        # Detect framework and language
        repo_path = Path(temp_dir)
        
        # Import framework detector
        from app.detectors.test_framework import TestFrameworkDetector
        from app.github.client import GitHubClient
        
        # Use detector to identify framework
        github_client = GitHubClient(token=token, repo_name=repo)
        detector = TestFrameworkDetector(github_client)
        framework_config = detector.detect()
        
        # Count existing tests
        test_dir = repo_path / framework_config['test_dir']
        test_count = 0
        if test_dir.exists():
            test_pattern = framework_config['test_pattern']
            if 'test_' in test_pattern:
                test_count = len(list(test_dir.rglob('test_*.py'))) + len(list(test_dir.rglob('test_*.js'))) + len(list(test_dir.rglob('test_*.ts')))
            else:
                test_count = len(list(test_dir.rglob('*.test.*'))) + len(list(test_dir.rglob('*.spec.*')))
        
        # Detect language from framework
        language = "Python" if framework_config['framework'] in ['pytest', 'unittest'] else "JavaScript/TypeScript"
        
        # Calculate repo size
        repo_size = sum(f.stat().st_size for f in repo_path.rglob('*') if f.is_file()) / (1024 * 1024)  # MB
        
        # Try to find source directory
        source_dir = None
        for common_src in ['src', 'lib', 'app']:
            if (repo_path / common_src).exists():
                source_dir = common_src
                break
        
        repo_info = RepositoryInfo(
            framework=framework_config['framework'],
            language=language,
            test_directory=framework_config['test_dir'],
            existing_test_count=test_count,
            detected_at=datetime.now().isoformat(),
            source_directory=source_dir,
            repo_size_mb=round(repo_size, 2)
        )
        
        logger.info(f"Repository analysis complete: {framework_config['framework']}, {test_count} tests")
        return repo_info
        
    except Exception as e:
        logger.error(f"Failed to detect repository info: {e}")
        return None
        
    finally:
        # Cleanup temporary directory
        if temp_dir and Path(temp_dir).exists():
            try:
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temp directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")

