"""Pydantic models for GitHub issue data."""

from typing import Optional, List
from pydantic import BaseModel, Field


class GitHubUser(BaseModel):
    """GitHub user model."""
    login: str
    id: int
    avatar_url: Optional[str] = None


class GitHubLabel(BaseModel):
    """GitHub label model."""
    name: str
    color: str
    description: Optional[str] = None


class GitHubIssue(BaseModel):
    """GitHub issue model."""
    number: int
    title: str
    body: Optional[str] = None
    state: str
    user: GitHubUser
    labels: List[GitHubLabel] = Field(default_factory=list)
    created_at: str
    updated_at: str
    html_url: str
    
    def get_acceptance_criteria(self) -> Optional[str]:
        """Extract acceptance criteria from issue body."""
        if not self.body:
            return None
        
        # Look for common acceptance criteria markers
        markers = [
            "## Acceptance Criteria",
            "## acceptance criteria",
            "# Acceptance Criteria",
            "# acceptance criteria",
            "**Acceptance Criteria**",
            "Acceptance Criteria:",
        ]
        
        body_lower = self.body.lower()
        for marker in markers:
            marker_lower = marker.lower()
            if marker_lower in body_lower:
                # Find the position and extract text after it
                idx = body_lower.find(marker_lower)
                remaining = self.body[idx + len(marker):]
                
                # Try to find the next section (usually starts with ##)
                next_section = remaining.find("\n##")
                if next_section > 0:
                    return remaining[:next_section].strip()
                else:
                    return remaining.strip()
        
        # If no specific marker, return the full body
        return self.body


class GenerateTestsRequest(BaseModel):
    """Request model for test generation."""
    issue_number: int
    repo_override: Optional[str] = None  # Allow overriding configured repo


class GenerateTestsResponse(BaseModel):
    """Response model for test generation."""
    success: bool
    message: str
    issue_number: int
    branch_name: Optional[str] = None
    pull_request_url: Optional[str] = None
    test_files: List[str] = Field(default_factory=list)
    error: Optional[str] = None


