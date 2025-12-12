"""GitHub API client for issue fetching, code search, and git operations."""

import logging
import os
from typing import Optional, List, Dict, Any
from github import Github, GithubException
from github.Repository import Repository
from github.Issue import Issue
from github.PullRequest import PullRequest
from github.GithubObject import NotSet

from app.models.github_issue import GitHubIssue, GitHubUser, GitHubLabel

logger = logging.getLogger(__name__)


class GitHubClient:
    """Unified GitHub client for API operations."""
    
    def __init__(self, token: Optional[str] = None, repo_name: Optional[str] = None):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub personal access token. If None, reads from GITHUB_TOKEN env var.
            repo_name: Repository in format "owner/repo". If None, reads from GITHUB_REPO env var.
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.repo_name = repo_name or os.getenv("GITHUB_REPO")
        
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN env variable.")
        if not self.repo_name:
            raise ValueError("GitHub repo is required. Set GITHUB_REPO env variable.")
        
        self.client = Github(self.token)
        self._repo: Optional[Repository] = None
        
        logger.info(f"Initialized GitHub client for repo: {self.repo_name}")
    
    @property
    def repo(self) -> Repository:
        """Get the repository object (cached)."""
        if self._repo is None:
            try:
                self._repo = self.client.get_repo(self.repo_name)
                logger.info(f"Connected to repository: {self._repo.full_name}")
            except GithubException as e:
                logger.error(f"Failed to access repository {self.repo_name}: {e}")
                raise
        return self._repo
    
    def get_repo_url(self) -> str:
        """Get the repository clone URL."""
        return self.repo.clone_url
    
    def fetch_issue(self, issue_number: int) -> GitHubIssue:
        """
        Fetch issue details from GitHub.
        
        Args:
            issue_number: The issue number to fetch.
            
        Returns:
            GitHubIssue model with issue details.
        """
        try:
            issue: Issue = self.repo.get_issue(issue_number)
            
            # Convert to our model
            github_issue = GitHubIssue(
                number=issue.number,
                title=issue.title,
                body=issue.body or "",
                state=issue.state,
                user=GitHubUser(
                    login=issue.user.login,
                    id=issue.user.id,
                    avatar_url=issue.user.avatar_url
                ),
                labels=[
                    GitHubLabel(
                        name=label.name,
                        color=label.color,
                        description=label.description or ""
                    )
                    for label in issue.labels
                ],
                created_at=issue.created_at.isoformat(),
                updated_at=issue.updated_at.isoformat(),
                html_url=issue.html_url
            )
            
            logger.info(f"Fetched issue #{issue_number}: {issue.title}")
            return github_issue
            
        except GithubException as e:
            logger.error(f"Failed to fetch issue #{issue_number}: {e}")
            raise
    
    def search_code(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search code in the repository.
        
        Args:
            query: Search query (will be scoped to current repo).
            max_results: Maximum number of results to return.
            
        Returns:
            List of code search results with file path and content.
        """
        try:
            # Add repo scope to query
            full_query = f"{query} repo:{self.repo_name}"
            
            results = []
            code_results = self.client.search_code(full_query)
            
            # Limit results
            count = 0
            for result in code_results:
                if count >= max_results:
                    break
                
                try:
                    # Get file content
                    content = result.decoded_content.decode('utf-8')
                    
                    results.append({
                        "path": result.path,
                        "name": result.name,
                        "sha": result.sha,
                        "url": result.html_url,
                        "content": content,
                        "size": result.size
                    })
                    count += 1
                except Exception as e:
                    logger.warning(f"Failed to decode content for {result.path}: {e}")
                    continue
            
            logger.info(f"Found {len(results)} code results for query: {query}")
            return results
            
        except GithubException as e:
            logger.error(f"Code search failed for query '{query}': {e}")
            return []
    
    def get_file_content(self, file_path: str, ref: str = "main") -> Optional[str]:
        """
        Get content of a specific file.
        
        Args:
            file_path: Path to the file in the repo.
            ref: Git ref (branch/tag/commit), defaults to "main".
            
        Returns:
            File content as string, or None if not found.
        """
        try:
            file_content = self.repo.get_contents(file_path, ref=ref)
            if isinstance(file_content, list):
                # It's a directory
                return None
            return file_content.decoded_content.decode('utf-8')
        except GithubException as e:
            logger.warning(f"Failed to get file {file_path}: {e}")
            return None
    
    def list_directory(self, dir_path: str = "", ref: str = "main") -> List[Dict[str, Any]]:
        """
        List contents of a directory.
        
        Args:
            dir_path: Path to directory (empty for root).
            ref: Git ref (branch/tag/commit).
            
        Returns:
            List of files and directories.
        """
        try:
            contents = self.repo.get_contents(dir_path, ref=ref)
            if not isinstance(contents, list):
                contents = [contents]
            
            return [
                {
                    "name": item.name,
                    "path": item.path,
                    "type": item.type,
                    "size": item.size if item.type == "file" else 0
                }
                for item in contents
            ]
        except GithubException as e:
            logger.warning(f"Failed to list directory {dir_path}: {e}")
            return []
    
    def create_branch(self, branch_name: str, base_branch: str = "main") -> bool:
        """
        Create a new branch.
        
        Args:
            branch_name: Name of the new branch.
            base_branch: Base branch to create from.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Get the base branch reference
            base_ref = self.repo.get_git_ref(f"heads/{base_branch}")
            base_sha = base_ref.object.sha
            
            # Create new branch
            self.repo.create_git_ref(f"refs/heads/{branch_name}", base_sha)
            
            logger.info(f"Created branch: {branch_name} from {base_branch}")
            return True
            
        except GithubException as e:
            if e.status == 422:  # Branch already exists
                logger.info(f"Branch {branch_name} already exists")
                return True
            logger.error(f"Failed to create branch {branch_name}: {e}")
            return False
    
    def commit_file(
        self,
        file_path: str,
        content: str,
        message: str,
        branch: str
    ) -> bool:
        """
        Create or update a file with a commit.
        
        Args:
            file_path: Path to the file in the repo.
            content: File content.
            message: Commit message.
            branch: Branch to commit to.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Check if file exists
            try:
                existing_file = self.repo.get_contents(file_path, ref=branch)
                # Update existing file
                self.repo.update_file(
                    path=file_path,
                    message=message,
                    content=content,
                    sha=existing_file.sha,
                    branch=branch
                )
                logger.info(f"Updated file {file_path} in branch {branch}")
            except GithubException:
                # File doesn't exist, create it
                self.repo.create_file(
                    path=file_path,
                    message=message,
                    content=content,
                    branch=branch
                )
                logger.info(f"Created file {file_path} in branch {branch}")
            
            return True
            
        except GithubException as e:
            logger.error(f"Failed to commit file {file_path}: {e}")
            return False
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main"
    ) -> Optional[PullRequest]:
        """
        Create a pull request.
        
        Args:
            title: PR title.
            body: PR description.
            head_branch: Source branch.
            base_branch: Target branch.
            
        Returns:
            PullRequest object if successful, None otherwise.
        """
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            
            logger.info(f"Created PR #{pr.number}: {title}")
            return pr
            
        except GithubException as e:
            logger.error(f"Failed to create PR: {e}")
            return None
    
    def post_issue_comment(self, issue_number: int, comment: str) -> bool:
        """
        Post a comment on an issue.
        
        Args:
            issue_number: Issue number.
            comment: Comment text (markdown supported).
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            issue = self.repo.get_issue(issue_number)
            issue.create_comment(comment)
            
            logger.info(f"Posted comment on issue #{issue_number}")
            return True
            
        except GithubException as e:
            logger.error(f"Failed to post comment on issue #{issue_number}: {e}")
            return False
    
    def get_default_branch(self) -> str:
        """Get the default branch name (main/master)."""
        return self.repo.default_branch


