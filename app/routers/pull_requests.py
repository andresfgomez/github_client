from typing import Literal

from fastapi import APIRouter, Query

from app.github_client import github_client
from app.models import Approver, PaginatedResponse, PullRequest

router = APIRouter(prefix="/repositories", tags=["pull requests"])


@router.get("/{owner}/{repo}/pulls", response_model=PaginatedResponse[PullRequest])
async def list_pull_requests(
    owner: str,
    repo: str,
    state: Literal["open", "closed", "all"] = Query(default="open"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=30, ge=1, le=100),
) -> PaginatedResponse[PullRequest]:
    """List pull requests for a repository."""
    return await github_client.list_pull_requests(
        owner=owner, repo=repo, state=state, page=page, per_page=per_page
    )


@router.get(
    "/{owner}/{repo}/pulls/approvers", response_model=PaginatedResponse[Approver]
)
async def list_approvers_for_repo(
    owner: str,
    repo: str,
    state: Literal["open", "closed", "all"] = Query(default="all"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=30, ge=1, le=100),
) -> PaginatedResponse[Approver]:
    """List approvers for a repository's pull requests."""
    return await github_client.list_approvers_for_repo(
        owner=owner, repo=repo, state=state, page=page, per_page=per_page
    )


@router.get("/{owner}/approvers", response_model=PaginatedResponse[Approver])
async def list_approvers_for_owner(
    owner: str,
    state: Literal["open", "closed", "all"] = Query(default="all"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=30, ge=1, le=100),
) -> PaginatedResponse[Approver]:
    """List approvers across all repositories for a user or organization."""
    return await github_client.list_approvers_for_owner(
        owner=owner, state=state, page=page, per_page=per_page
    )
