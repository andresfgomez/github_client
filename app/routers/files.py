from fastapi import APIRouter

from app.github_client import github_client
from app.models import FileContent, FileItem

router = APIRouter(prefix="/repositories", tags=["files"])


@router.get("/{owner}/{repo}/files", response_model=list[FileItem])
async def list_files(
    owner: str,
    repo: str,
    path: str = "",
) -> list[FileItem]:
    """List files in a repository directory."""
    return await github_client.list_files(owner=owner, repo=repo, path=path)


@router.get("/{owner}/{repo}/files/{path:path}", response_model=FileContent)
async def get_file_content(
    owner: str,
    repo: str,
    path: str,
) -> FileContent:
    """Get the content of a specific file."""
    return await github_client.get_file_content(owner=owner, repo=repo, path=path)
