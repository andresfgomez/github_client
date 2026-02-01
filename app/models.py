from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class User(BaseModel):
    login: str
    avatar_url: str
    html_url: str


class Repository(BaseModel):
    id: int
    name: str
    full_name: str
    description: str | None
    private: bool
    html_url: str
    created_at: datetime
    updated_at: datetime


class PullRequest(BaseModel):
    id: int
    number: int
    title: str
    state: str
    html_url: str
    created_at: datetime
    merged_at: datetime | None
    user: User


class Approver(BaseModel):
    login: str
    avatar_url: str
    html_url: str
    approval_count: int
    repositories: list[str]


class FileItem(BaseModel):
    name: str
    path: str
    type: str  # "file" or "dir"
    size: int
    html_url: str
    download_url: str | None


class FileContent(BaseModel):
    name: str
    path: str
    size: int
    content: str
    encoding: str
    html_url: str


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total_count: int
    page: int
    per_page: int
    has_next: bool
