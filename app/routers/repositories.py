from typing import Literal

from fastapi import APIRouter, Query

from app.github_client import github_client
from app.models import PaginatedResponse, Repository

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.get("/{owner}", response_model=PaginatedResponse[Repository])
async def list_repositories(
    owner: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=30, ge=1, le=100),
    type: Literal["all", "owner", "member"] = Query(default="all"),
) -> PaginatedResponse[Repository]:
    """List repositories for a user or organization."""
    return await github_client.list_repositories(
        owner=owner, page=page, per_page=per_page, repo_type=type
    )
