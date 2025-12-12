"""Code search and context building for test generation."""

import logging
from typing import List, Dict, Any, Optional
from app.github.client import GitHubClient
from app.models.github_issue import GitHubIssue

logger = logging.getLogger(__name__)


class CodeContextBuilder:
    """Build relevant code context from repository for test generation."""
    
    def __init__(self, github_client: GitHubClient):
        """
        Initialize context builder.
        
        Args:
            github_client: Initialized GitHub client.
        """
        self.client = github_client
    
    def extract_keywords(self, issue: GitHubIssue) -> List[str]:
        """
        Extract relevant keywords from issue for code search.
        
        Args:
            issue: GitHub issue.
            
        Returns:
            List of search keywords.
        """
        keywords = []
        
        # Extract from title (split by spaces and remove common words)
        title_words = issue.title.lower().split()
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "as", "is", "was"}
        keywords.extend([w for w in title_words if w not in stop_words and len(w) > 2])
        
        # Extract from labels
        keywords.extend([label.name.lower().replace(" ", "_") for label in issue.labels])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
        
        return unique_keywords[:5]  # Limit to top 5 keywords
    
    def find_similar_tests(self, test_dir: str = "tests") -> List[Dict[str, Any]]:
        """
        Find existing test files to understand patterns.
        
        Args:
            test_dir: Directory containing tests.
            
        Returns:
            List of test files with content.
        """
        try:
            test_files = []
            
            # Try to list test directory
            contents = self.client.list_directory(test_dir)
            
            # Get content of a few test files (up to 3)
            count = 0
            for item in contents:
                if count >= 3:
                    break
                
                if item["type"] == "file" and "test" in item["name"].lower():
                    content = self.client.get_file_content(item["path"])
                    if content:
                        test_files.append({
                            "path": item["path"],
                            "name": item["name"],
                            "content": content[:2000]  # Limit content size
                        })
                        count += 1
            
            logger.info(f"Found {len(test_files)} example test files")
            return test_files
            
        except Exception as e:
            logger.warning(f"Failed to find test examples: {e}")
            return []
    
    def search_relevant_code(self, issue: GitHubIssue, max_files: int = 5) -> List[Dict[str, Any]]:
        """
        Search for code relevant to the issue.
        
        Args:
            issue: GitHub issue with details.
            max_files: Maximum number of files to return.
            
        Returns:
            List of relevant code files.
        """
        keywords = self.extract_keywords(issue)
        
        if not keywords:
            logger.warning("No keywords extracted from issue")
            return []
        
        # Search for each keyword and combine results
        all_results = []
        seen_paths = set()
        
        for keyword in keywords:
            results = self.client.search_code(keyword, max_results=3)
            
            for result in results:
                if result["path"] not in seen_paths:
                    seen_paths.add(result["path"])
                    
                    # Truncate content to save tokens
                    result["content"] = result["content"][:1500]
                    all_results.append(result)
                
                if len(all_results) >= max_files:
                    break
            
            if len(all_results) >= max_files:
                break
        
        logger.info(f"Found {len(all_results)} relevant code files")
        return all_results
    
    def get_repository_structure(self) -> Dict[str, Any]:
        """
        Get high-level repository structure.
        
        Returns:
            Dictionary with repo structure info.
        """
        try:
            structure = {
                "root_files": [],
                "directories": []
            }
            
            # List root directory
            contents = self.client.list_directory("")
            
            for item in contents:
                if item["type"] == "file":
                    structure["root_files"].append(item["name"])
                elif item["type"] == "dir":
                    structure["directories"].append(item["name"])
            
            return structure
            
        except Exception as e:
            logger.warning(f"Failed to get repo structure: {e}")
            return {"root_files": [], "directories": []}
    
    def build_context(self, issue: GitHubIssue, test_framework: Optional[str] = None) -> Dict[str, Any]:
        """
        Build complete context for test generation.
        
        Args:
            issue: GitHub issue.
            test_framework: Detected test framework (if available).
            
        Returns:
            Dictionary with all context information.
        """
        logger.info(f"Building context for issue #{issue.number}")
        
        context = {
            "issue": {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "acceptance_criteria": issue.get_acceptance_criteria(),
                "labels": [label.name for label in issue.labels]
            },
            "repository_structure": self.get_repository_structure(),
            "relevant_code": self.search_relevant_code(issue),
            "test_examples": self.find_similar_tests(),
            "test_framework": test_framework
        }
        
        logger.info(
            f"Context built: {len(context['relevant_code'])} code files, "
            f"{len(context['test_examples'])} test examples"
        )
        
        return context


