from typing import Any

import httpx

from app.config import settings
from app.models import (
    Approver,
    FileContent,
    FileItem,
    PaginatedResponse,
    PullRequest,
    Repository,
)


class GitHubClient:
    def __init__(self) -> None:
        self.base_url = settings.github_api_base_url
        self.headers = {
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def _request(
        self, method: str, endpoint: str, params: dict[str, Any] | None = None
    ) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def list_repositories(
        self,
        owner: str,
        page: int = 1,
        per_page: int = 30,
        repo_type: str = "all",
    ) -> PaginatedResponse[Repository]:
        # Try user repos first, fall back to org repos
        try:
            data = await self._request(
                "GET",
                f"/users/{owner}/repos",
                params={"page": page, "per_page": per_page, "type": repo_type},
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                data = await self._request(
                    "GET",
                    f"/orgs/{owner}/repos",
                    params={"page": page, "per_page": per_page, "type": repo_type},
                )
            else:
                raise

        repositories = [Repository.model_validate(repo) for repo in data]
        return PaginatedResponse(
            items=repositories,
            total_count=len(repositories),
            page=page,
            per_page=per_page,
            has_next=len(repositories) == per_page,
        )

    async def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        page: int = 1,
        per_page: int = 30,
    ) -> PaginatedResponse[PullRequest]:
        data = await self._request(
            "GET",
            f"/repos/{owner}/{repo}/pulls",
            params={"state": state, "page": page, "per_page": per_page},
        )
        pull_requests = [PullRequest.model_validate(pr) for pr in data]
        return PaginatedResponse(
            items=pull_requests,
            total_count=len(pull_requests),
            page=page,
            per_page=per_page,
            has_next=len(pull_requests) == per_page,
        )

    async def get_pr_reviews(
        self, owner: str, repo: str, pull_number: int
    ) -> list[dict[str, Any]]:
        return await self._request(
            "GET",
            f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews",
        )

    async def list_approvers_for_repo(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        page: int = 1,
        per_page: int = 30,
    ) -> PaginatedResponse[Approver]:
        # Get PRs for the repo
        prs_response = await self.list_pull_requests(
            owner, repo, state=state, page=page, per_page=per_page
        )

        # Aggregate approvers
        approver_map: dict[str, dict[str, Any]] = {}
        for pr in prs_response.items:
            reviews = await self.get_pr_reviews(owner, repo, pr.number)
            for review in reviews:
                if review["state"] == "APPROVED":
                    user = review["user"]
                    login = user["login"]
                    if login not in approver_map:
                        approver_map[login] = {
                            "login": login,
                            "avatar_url": user["avatar_url"],
                            "html_url": user["html_url"],
                            "approval_count": 0,
                            "repositories": set(),
                        }
                    approver_map[login]["approval_count"] += 1
                    approver_map[login]["repositories"].add(repo)

        approvers = [
            Approver(
                login=data["login"],
                avatar_url=data["avatar_url"],
                html_url=data["html_url"],
                approval_count=data["approval_count"],
                repositories=list(data["repositories"]),
            )
            for data in approver_map.values()
        ]
        approvers.sort(key=lambda a: a.approval_count, reverse=True)

        return PaginatedResponse(
            items=approvers,
            total_count=len(approvers),
            page=1,
            per_page=len(approvers),
            has_next=False,
        )

    async def list_approvers_for_owner(
        self,
        owner: str,
        state: str = "all",
        page: int = 1,
        per_page: int = 30,
    ) -> PaginatedResponse[Approver]:
        # Get repositories for the owner
        repos_response = await self.list_repositories(owner, page=1, per_page=100)

        # Aggregate approvers across all repos
        approver_map: dict[str, dict[str, Any]] = {}
        for repo in repos_response.items:
            prs_response = await self.list_pull_requests(
                owner, repo.name, state=state, page=page, per_page=per_page
            )
            for pr in prs_response.items:
                reviews = await self.get_pr_reviews(owner, repo.name, pr.number)
                for review in reviews:
                    if review["state"] == "APPROVED":
                        user = review["user"]
                        login = user["login"]
                        if login not in approver_map:
                            approver_map[login] = {
                                "login": login,
                                "avatar_url": user["avatar_url"],
                                "html_url": user["html_url"],
                                "approval_count": 0,
                                "repositories": set(),
                            }
                        approver_map[login]["approval_count"] += 1
                        approver_map[login]["repositories"].add(repo.name)

        approvers = [
            Approver(
                login=data["login"],
                avatar_url=data["avatar_url"],
                html_url=data["html_url"],
                approval_count=data["approval_count"],
                repositories=list(data["repositories"]),
            )
            for data in approver_map.values()
        ]
        approvers.sort(key=lambda a: a.approval_count, reverse=True)

        return PaginatedResponse(
            items=approvers,
            total_count=len(approvers),
            page=1,
            per_page=len(approvers),
            has_next=False,
        )

    async def list_files(
        self,
        owner: str,
        repo: str,
        path: str = "",
    ) -> list[FileItem]:
        endpoint = f"/repos/{owner}/{repo}/contents"
        if path:
            endpoint = f"{endpoint}/{path}"
        data = await self._request("GET", endpoint)
        if isinstance(data, dict):
            # Single file returned, wrap in list
            data = [data]
        return [FileItem.model_validate(item) for item in data]

    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
    ) -> FileContent:
        data = await self._request(
            "GET",
            f"/repos/{owner}/{repo}/contents/{path}",
        )
        return FileContent.model_validate(data)


github_client = GitHubClient()
